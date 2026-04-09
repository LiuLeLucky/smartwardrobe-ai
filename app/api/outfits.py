from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import EmptyWardrobeError
from app.database.session import get_db
from app.models.outfit import Outfit
from app.models.user import User
from app.schemas.outfit import OutfitCreate, OutfitGenerateRequest, OutfitResponse
from app.services.outfit_service import (
    cleanup_unsaved_outfits,
    generate_and_save_outfit,
    get_unsaved_outfits,
    get_user_outfits,
    save_generated_outfit,
    save_outfit,
)

router = APIRouter(prefix="/outfits", tags=["outfits"])


@router.post("/", response_model=OutfitResponse, status_code=status.HTTP_201_CREATED)
async def create_outfit(
    outfit_in: OutfitCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OutfitResponse:
    try:
        outfit = await save_outfit(db, current_user.id, outfit_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return outfit


@router.post("/generate", response_model=list[OutfitResponse], status_code=status.HTTP_201_CREATED)
async def generate_outfit(
    request: OutfitGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[OutfitResponse]:
    try:
        outfits = await generate_and_save_outfit(db, current_user.id, request)
    except EmptyWardrobeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return outfits


@router.get("/unsaved", response_model=list[OutfitResponse])
async def list_unsaved_outfits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[OutfitResponse]:
    return await get_unsaved_outfits(db, current_user.id)


@router.get("/", response_model=list[OutfitResponse])
async def list_outfits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[OutfitResponse]:
    return await get_user_outfits(db, current_user.id)


@router.post("/{outfit_id}/save", response_model=OutfitResponse)
async def save_outfit_endpoint(
    outfit_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OutfitResponse:
    outfit = await save_generated_outfit(db, outfit_id, current_user.id)
    if not outfit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")
    await cleanup_unsaved_outfits(db, current_user.id)
    return outfit


@router.delete("/{outfit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_outfit(
    outfit_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(Outfit).where(Outfit.id == outfit_id, Outfit.user_id == current_user.id)
    )
    outfit = result.scalar_one_or_none()
    if not outfit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")
    await db.delete(outfit)
    await db.commit()
