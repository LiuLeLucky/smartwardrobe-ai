from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clothing import Clothing
from app.schemas.clothing import ClothingCreate, ClothingUpdate


async def create_clothing(
    db: AsyncSession, item_in: ClothingCreate, user_id: str
) -> Clothing:
    item = Clothing(user_id=user_id, **item_in.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def get_user_clothing(db: AsyncSession, user_id: str) -> list[Clothing]:
    result = await db.execute(
        select(Clothing).where(Clothing.user_id == user_id)
    )
    return list(result.scalars().all())


async def get_clothing_by_id(
    db: AsyncSession, item_id: str, user_id: str
) -> Clothing | None:
    result = await db.execute(
        select(Clothing).where(Clothing.id == item_id, Clothing.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_clothing(
    db: AsyncSession, item_id: str, user_id: str, update_data: ClothingUpdate
) -> Clothing | None:
    item = await get_clothing_by_id(db, item_id, user_id)
    if not item:
        return None
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


async def delete_clothing(
    db: AsyncSession, item_id: str, user_id: str
) -> bool:
    item = await get_clothing_by_id(db, item_id, user_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True
