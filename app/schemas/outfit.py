from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.clothing import ClothingResponse


class OutfitBase(BaseModel):
    name: str
    occasion: str | None = None


class OutfitCreate(OutfitBase):
    clothing_item_ids: list[str] = Field(min_length=1)


class OutfitGenerateRequest(BaseModel):
    occasion: str
    weather_context: str | None = None
    style_preference: str | None = None


class OutfitResponse(OutfitBase):
    id: str
    user_id: str
    ai_explanation: str | None
    ai_score: str | None
    source: str
    is_saved: bool
    improvement_suggestions: str = ""
    created_at: datetime
    clothing_items: list[ClothingResponse]

    model_config = ConfigDict(from_attributes=True)

    @field_validator("improvement_suggestions", mode="before")
    @classmethod
    def _none_to_empty(cls, v: object) -> str:
        return v if isinstance(v, str) else ""
