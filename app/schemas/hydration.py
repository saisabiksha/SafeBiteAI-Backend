"""Pydantic schemas for hydration intake logging and daily summaries."""
from datetime import date as dt_date
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class HydrationCreate(BaseModel):
    """Request payload to log a water intake entry."""

    amount_ml: int = Field(
        ...,
        gt=0,
        le=5000,
        description="Volume of water consumed in millilitres (must be a positive, realistic quantity, up to 5000ml)",
        examples=[250],
    )
    recorded_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the water was consumed (defaults to current time if omitted)",
        examples=["2026-10-12T08:30:00Z"],
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional contextual note (e.g. morning glass, post-exercise)",
        examples=["Morning glass of water"],
    )


class HydrationResponse(BaseModel):
    """Response payload for a hydration intake record."""

    id: int = Field(..., description="Unique database identifier for the hydration record")
    user_id: int = Field(..., description="ID of the user who logged the intake")
    amount_ml: int = Field(..., description="Recorded volume in millilitres")
    recorded_at: datetime = Field(..., description="Timestamp associated with the consumption")
    notes: Optional[str] = Field(None, description="Optional user note")
    created_at: datetime = Field(..., description="Timestamp when the entry was stored")

    model_config = ConfigDict(from_attributes=True)


class HydrationSummaryResponse(BaseModel):
    """Daily hydration summary response."""

    user_id: int = Field(..., description="User ID")
    date: dt_date = Field(..., description="Target date for the summary (YYYY-MM-DD)")
    total_amount_ml: int = Field(..., description="Total recorded water intake in millilitres for the specified date")
    entry_count: int = Field(..., description="Number of hydration logs recorded on this date")
    metric_label: str = Field(
        default="Recorded Intake",
        description="Label clarifying that this figure represents user-reported intake volume only",
    )
    disclaimer: str = Field(
        default=(
            "This summary represents total user-recorded fluid intake only. It does NOT constitute a clinical "
            "hydration assessment, medical evaluation, or personalized hydration prescription. Daily fluid needs "
            "vary based on body composition, activity level, climate, and medical history. Consult a physician "
            "for individualized medical guidance."
        ),
        description="Mandatory non-diagnostic and non-prescriptive disclaimer",
    )
