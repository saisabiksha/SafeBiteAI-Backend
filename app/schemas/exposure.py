"""Pydantic schemas for exposure incident recording and first-aid guidance."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ExposureBase(BaseModel):
    """Base schema for an exposure record."""

    suspected_allergen: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Name of the food or substance suspected of triggering the reaction",
        examples=["Peanut butter cookie"],
    )
    symptoms: List[str] = Field(
        default_factory=list,
        description="List of symptoms reported by the user",
        examples=[["itchy mouth", "hives on arms"]],
    )
    exposure_time: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the suspected exposure occurred (optional)",
        examples=["2026-10-11T20:30:00Z"],
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional context, food brand, or location details (optional)",
        examples=["Ate bakery cookie at dinner party"],
    )


class ExposureCreate(ExposureBase):
    """Request payload for recording a new exposure incident."""
    pass


class FirstAidGuidance(BaseModel):
    """Cautious interim first-aid guidance returned upon recording an exposure."""

    urgency: str = Field(
        ...,
        description="Urgency classification: EMERGENCY | MONITOR_CLOSELY | PRECAUTIONARY",
        examples=["EMERGENCY"],
    )
    emergency_warning: Optional[str] = Field(
        default=None,
        description="Prominent warning displayed when severe, red-flag symptoms are reported",
    )
    instructions: List[str] = Field(
        default_factory=list,
        description="Step-by-step interim first-aid actions",
    )
    medication_warning: str = Field(
        ...,
        description="Explicit guidance regarding epinephrine versus antihistamines",
    )
    disclaimer: str = Field(
        ...,
        description="Mandatory medical and non-diagnostic disclaimer",
    )


class ExposureResponse(ExposureBase):
    """Response payload for exposure incidents."""

    id: int = Field(..., description="Unique database identifier for the exposure record")
    user_id: int = Field(..., description="ID of the user who experienced the exposure")
    created_at: datetime = Field(..., description="Timestamp when the record was created")
    guidance: Optional[FirstAidGuidance] = Field(
        default=None,
        description="Cautious first-aid guidance generated from reported symptoms",
    )

    model_config = ConfigDict(from_attributes=True)
