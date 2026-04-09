import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

# Pure association table — no extra columns, no ORM class needed
outfit_items_table = Table(
    "outfit_items",
    Base.metadata,
    Column(
        "outfit_id",
        String(36),
        ForeignKey("outfits.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "clothing_id",
        String(36),
        ForeignKey("clothing.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Outfit(Base):
    __tablename__ = "outfits"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    occasion: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ai_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Reserved for Phase 3 AI scoring (A / B / C)
    ai_score: Mapped[str | None] = mapped_column(String(1), nullable=True)

    source: Mapped[str] = mapped_column(String(10), nullable=False, default="ai")
    is_saved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    improvement_suggestions: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Many-to-many — lazy="selectin" required for async SQLAlchemy
    clothing_items: Mapped[list["Clothing"]] = relationship(  # type: ignore[name-defined]
        "Clothing",
        secondary=outfit_items_table,
        lazy="selectin",
    )
