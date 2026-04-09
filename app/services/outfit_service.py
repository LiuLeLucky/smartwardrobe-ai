from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EmptyWardrobeError
from app.models.clothing import Clothing
from app.models.outfit import Outfit
from app.schemas.outfit import OutfitCreate, OutfitGenerateRequest
from app.services.ai_service import get_ai_service


async def save_outfit(
    db: AsyncSession, user_id: str, outfit_data: OutfitCreate
) -> Outfit:
    # Fetch only items that belong to this user
    unique_ids = list(dict.fromkeys(outfit_data.clothing_item_ids))

    result = await db.execute(
        select(Clothing).where(
            Clothing.id.in_(unique_ids),
            Clothing.user_id == user_id,
        )
    )
    items = list(result.scalars().all())

    # Guard: all requested IDs must exist and belong to this user
    if len(items) != len(unique_ids):
        found_ids = {item.id for item in items}
        missing = [i for i in outfit_data.clothing_item_ids if i not in found_ids]
        raise ValueError(f"Clothing items not found or do not belong to user: {missing}")

    outfit = Outfit(
        user_id=user_id,
        name=outfit_data.name,
        occasion=outfit_data.occasion,
        clothing_items=items,
        source="manual",
        is_saved=True,
    )
    db.add(outfit)
    await db.commit()

    # Re-fetch so selectin loading fires within the open session
    refreshed = await db.execute(select(Outfit).where(Outfit.id == outfit.id))
    return refreshed.scalar_one()


def _score_to_grade(score: float) -> str:
    """Convert a 1.0–10.0 float score to the single-character grade stored in Outfit.ai_score.

    Outfit.ai_score is String(1) designed for A/B/C grades. The AI service returns
    a float; this function bridges the two representations.
    """
    if score >= 7.0:
        return "A"
    if score >= 4.0:
        return "B"
    return "C"


async def generate_and_save_outfit(
    db: AsyncSession,
    user_id: str,
    request: OutfitGenerateRequest,
) -> list[Outfit]:
    # 1. Fetch all clothing items that belong to this user
    result = await db.execute(
        select(Clothing).where(Clothing.user_id == user_id)
    )
    clothing_items = list(result.scalars().all())

    # 2. Require at least 2 items for meaningful AI generation
    if len(clothing_items) < 2:
        raise EmptyWardrobeError(
            "At least 2 clothing items are required to generate an outfit."
        )

    # 3. Call the AI service — returns list of up to 3 recommendations
    ai_service = get_ai_service()
    recommendations = await ai_service.generate_outfit(
        clothing_items=clothing_items,
        occasion=request.occasion,
        weather_context=request.weather_context,
        style_preference=request.style_preference,
    )

    # 4. Build and validate each outfit, then persist all in one commit
    user_item_ids = {item.id for item in clothing_items}
    created_outfits: list[Outfit] = []

    for i, recommendation in enumerate(recommendations):
        invalid_ids = [x for x in recommendation.selected_item_ids if x not in user_item_ids]
        if invalid_ids:
            raise ValueError(
                f"AI returned item IDs that do not belong to this user: {invalid_ids}"
            )

        selected_items = [
            item for item in clothing_items
            if item.id in set(recommendation.selected_item_ids)
        ]

        outfit = Outfit(
            user_id=user_id,
            name=f"Outfit for {request.occasion} - {date.today():%Y-%m-%d} #{i + 1}",
            occasion=request.occasion,
            ai_explanation=recommendation.ai_explanation,
            ai_score=_score_to_grade(recommendation.ai_score),
            improvement_suggestions=recommendation.improvement_suggestions,
            clothing_items=selected_items,
            source="ai",
            is_saved=False,
        )
        db.add(outfit)
        created_outfits.append(outfit)

    await db.commit()

    # 5. Re-fetch all so selectin loading fires within the open session
    outfit_ids = [o.id for o in created_outfits]
    result = await db.execute(select(Outfit).where(Outfit.id.in_(outfit_ids)))
    fetched = {o.id: o for o in result.scalars().all()}
    # Preserve score-descending order from the AI
    return [fetched[oid] for oid in outfit_ids]


async def get_user_outfits(db: AsyncSession, user_id: str) -> list[Outfit]:
    result = await db.execute(
        select(Outfit).where(Outfit.user_id == user_id)
    )
    return list(result.scalars().all())


async def get_unsaved_outfits(db: AsyncSession, user_id: str) -> list[Outfit]:
    result = await db.execute(
        select(Outfit).where(Outfit.user_id == user_id, Outfit.is_saved == False)  # noqa: E712
    )
    return sorted(result.scalars().all(), key=lambda o: o.created_at, reverse=True)


async def save_generated_outfit(
    db: AsyncSession, outfit_id: str, user_id: str
) -> Outfit | None:
    result = await db.execute(
        select(Outfit).where(Outfit.id == outfit_id, Outfit.user_id == user_id)
    )
    outfit = result.scalar_one_or_none()
    if not outfit:
        return None
    outfit.is_saved = True
    await db.commit()
    refreshed = await db.execute(select(Outfit).where(Outfit.id == outfit.id))
    return refreshed.scalar_one()


async def cleanup_unsaved_outfits(db: AsyncSession, user_id: str) -> int:
    result = await db.execute(
        select(Outfit).where(Outfit.user_id == user_id, Outfit.is_saved == False)  # noqa: E712
    )
    unsaved = sorted(result.scalars().all(), key=lambda o: o.created_at, reverse=True)
    to_delete = unsaved[30:]
    for outfit in to_delete:
        await db.delete(outfit)
    if to_delete:
        await db.commit()
    return len(to_delete)
