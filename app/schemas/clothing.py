from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClothingCreate(BaseModel):
    category: str
    sub_category: str
    color_code: str = Field(pattern=r'^#[0-9a-fA-F]{6}$')
    material: str
    season: list[str]


class ClothingUpdate(BaseModel):
    category: str | None = None
    sub_category: str | None = None
    color_code: str | None = Field(default=None, pattern=r'^#[0-9a-fA-F]{6}$')
    material: str | None = None
    season: list[str] | None = None


class ClothingResponse(BaseModel):
    id: str
    user_id: str
    category: str
    sub_category: str
    color_code: str
    material: str
    season: list[str]
    image_url: str | None
    vector_id: str | None
    raw_ai_metadata: dict | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
