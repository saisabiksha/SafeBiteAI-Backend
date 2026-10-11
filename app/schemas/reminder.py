"""Pydantic schemas for stored wellness, hydration, and medication reminders."""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

ReminderCategory = Literal["hydration", "medication", "appointment", "general"]


class ReminderBase(BaseModel):
    """
    Base schema for stored reminder records.
    Note: These records are stored schedules only; they do not trigger external push notifications.
    For medication reminders, only user- or clinician-supplied schedules are stored—no doses or regimens are generated.
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Brief title or label for the reminder",
        examples=["Drink a glass of water"],
    )
    category: ReminderCategory = Field(
        ...,
        description="Category: hydration, medication, appointment, or general",
        examples=["hydration"],
    )
    scheduled_at: datetime = Field(
        ...,
        description="Target date and time for the reminder schedule",
        examples=["2026-10-12T09:00:00Z"],
    )
    notes: Optional[str] = Field(
        default=None,
        description="Optional instructions or context explicitly provided by user or clinician",
        examples=["Keep water bottle nearby"],
    )
    is_completed: bool = Field(
        default=False,
        description="Whether the scheduled activity has been marked completed",
    )


class ReminderCreate(ReminderBase):
    """Request payload to create a new reminder."""
    pass


class ReminderUpdate(BaseModel):
    """Request payload to update an existing reminder."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=150)
    category: Optional[ReminderCategory] = Field(default=None)
    scheduled_at: Optional[datetime] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    is_completed: Optional[bool] = Field(default=None)


class ReminderResponse(ReminderBase):
    """Response payload for a stored reminder."""

    id: int = Field(..., description="Unique database identifier for the reminder")
    user_id: int = Field(..., description="ID of the user who owns the reminder")
    created_at: datetime = Field(..., description="Timestamp when the reminder was created")
    notification_notice: str = Field(
        default="Stored schedule entry only. Does not dispatch external alerts, SMS, or automated alarms.",
        description="Notice clarifying that this record does not trigger external push notifications",
    )

    model_config = ConfigDict(from_attributes=True)


class ReminderDeleteResponse(BaseModel):
    """Deletion confirmation response."""

    message: str = Field(..., examples=["Reminder deleted successfully"])
    id: int = Field(..., examples=[1])
    user_id: int = Field(..., examples=[2])
