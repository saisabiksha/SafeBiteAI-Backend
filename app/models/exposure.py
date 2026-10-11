"""Exposure incident database model."""
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Exposure(Base):
    """
    Exposure incident record documenting a suspected exposure event and symptoms.
    """

    __tablename__ = "exposures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    suspected_allergen: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    symptoms: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    exposure_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationship back to parent user
    user: Mapped["User"] = relationship("User", back_populates="exposures")

    def __repr__(self) -> str:
        return f"<Exposure id={self.id} user_id={self.user_id} suspected_allergen={self.suspected_allergen}>"
