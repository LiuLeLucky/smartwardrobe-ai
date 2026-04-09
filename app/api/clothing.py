import aiofiles
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import settings
from app.database.session import get_db
from app.models.user import User
from app.schemas.clothing import ClothingCreate, ClothingResponse, ClothingUpdate
from app.services.clothing_service import (
    create_clothing,
    delete_clothing,
    get_clothing_by_id,
    get_user_clothing,
    update_clothing,
)
from app.services.ai_service import get_ai_service

logger = logging.getLogger(__name__)

_ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
_ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
_MAX_BYTES = 5 * 1024 * 1024  # 5 MB

router = APIRouter(prefix="/clothing", tags=["clothing"])


@router.post("/", response_model=ClothingResponse, status_code=status.HTTP_201_CREATED)
async def create(
    item_in: ClothingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ClothingResponse:
    return await create_clothing(db, item_in, current_user.id)


@router.get("/", response_model=list[ClothingResponse])
async def list_items(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ClothingResponse]:
    return await get_user_clothing(db, current_user.id)


@router.get("/{item_id}", response_model=ClothingResponse)
async def get_one(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ClothingResponse:
    item = await get_clothing_by_id(db, item_id, current_user.id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.patch("/{item_id}", response_model=ClothingResponse)
async def update(
    item_id: str,
    update_data: ClothingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ClothingResponse:
    item = await update_clothing(db, item_id, current_user.id, update_data)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await delete_clothing(db, item_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")


@router.post("/{item_id}/upload-image", response_model=ClothingResponse)
async def upload_image(
    item_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ClothingResponse:
    # Ownership check
    item = await get_clothing_by_id(db, item_id, current_user.id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    # Validate extension (content-type can be spoofed; extension is a fast first gate)
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{suffix}'. Allowed: jpg, jpeg, png, webp.",
        )

    # Read entire file to enforce size limit
    contents = await file.read()
    if len(contents) > _MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large ({len(contents) // 1024} KB). Maximum allowed is 5 MB.",
        )

    # Build unique filename and save
    safe_filename = f"{current_user.id}_{item_id}{suffix}"
    dest = Path(settings.UPLOAD_DIR) / safe_filename

    async with aiofiles.open(dest, "wb") as f:
        await f.write(contents)

    # Persist the image URL
    item.image_url = f"/uploads/{safe_filename}"
    await db.commit()
    await db.refresh(item)

    # Vision analysis — failures must never break the upload
    try:
        ai_service = get_ai_service()
        analysis = await ai_service.analyze_clothing_image(contents)
        if "error" in analysis:
            logger.warning("Vision analysis skipped for item %s: %s", item_id, analysis["error"])
        else:
            ai_update = ClothingUpdate(
                category=analysis.get("category"),
                sub_category=analysis.get("sub_category"),
                color_code=analysis.get("color_code"),
                material=analysis.get("material"),
                season=analysis.get("season"),
            )
            updated = await update_clothing(db, item_id, current_user.id, ai_update)
            if updated:
                item = updated
    except Exception as exc:
        logger.warning("Vision analysis failed for item %s: %s", item_id, exc)

    return item
