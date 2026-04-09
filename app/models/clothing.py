import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Clothing(Base):
    __tablename__ = "clothing"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Core attributes
    category: Mapped[str] = mapped_column(String(50), nullable=False)        # e.g. 上装 / 下装 / 外套
    sub_category: Mapped[str] = mapped_column(String(50), nullable=False)    # e.g. 卫衣 / 直筒裤
    color_code: Mapped[str] = mapped_column(String(7), nullable=False)       # hex e.g. #FFFFFF
    material: Mapped[str] = mapped_column(String(50), nullable=False)        # e.g. 纯棉 / 亚麻
    season: Mapped[list] = mapped_column(JSON, nullable=False, default=list) # e.g. ["spring", "autumn"]

    # Image
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Reserved — Phase 4 (vision) and Phase 6 (ChromaDB)
    vector_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    raw_ai_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
