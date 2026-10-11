"""User profile database model."""
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.allergy import Allergy
    from app.models.exposure import Exposure
    from app.models.hydration import HydrationRecord
    from app.models.reminder import Reminder


class User(Base):
    """
    User profile model for storing basic profile information.
    Does not store sensitive credentials or passwords.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationship: A user can have multiple allergy records
    allergies: Mapped[List["Allergy"]] = relationship(
        "Allergy",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Relationship: A user can have multiple exposure incident records
    exposures: Mapped[List["Exposure"]] = relationship(
        "Exposure",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Relationship: A user can have multiple hydration intake records
    hydration_records: Mapped[List["HydrationRecord"]] = relationship(
        "HydrationRecord",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Relationship: A user can have multiple reminders
    reminders: Mapped[List["Reminder"]] = relationship(
        "Reminder",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
