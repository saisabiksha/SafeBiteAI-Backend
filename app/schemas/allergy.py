"""Pydantic schemas for allergy data validation and serialization."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AllergyBase(BaseModel):
    """
    Base schema for allergen information.
    Note: These endpoints are for development and testing; real medical logic is excluded.
    """

    allergen_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the allergen (e.g. Peanut, Penicillin, Shellfish)",
        examples=["Peanut"],
    )
    category: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Category such as food, medication, or environmental",
        examples=["food"],
    )
    aliases: List[str] = Field(
        default_factory=list,
        description="Optional alternative names or aliases for the allergen",
        examples=[["groundnut", "arachis oil"]],
    )
    notes: Optional[str] = Field(
        default=None,
        description="Optional additional notes or severity details",
        examples=["Requires epinephrine pen"],
    )


class AllergyCreate(AllergyBase):
    """Schema for adding a new allergy to a user profile."""
    pass


class AllergyUpdate(BaseModel):
    """Schema for updating an existing allergy record."""

    allergen_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Name of the allergen",
        examples=["Peanut"],
    )
    category: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Category such as food or medication",
        examples=["food"],
    )
    aliases: Optional[List[str]] = Field(
        default=None,
        description="Optional list of alternative names or aliases",
        examples=[["groundnut", "arachis hypogaea"]],
    )
    notes: Optional[str] = Field(
        default=None,
        description="Optional additional notes",
        examples=["Updated severity note"],
    )


class AllergyResponse(AllergyBase):
    """Schema for returning allergy details."""

    id: int = Field(..., description="Unique database identifier for the allergy record", examples=[1])
    user_id: int = Field(..., description="ID of the user who owns this allergy", examples=[2])
    created_at: datetime = Field(..., description="Timestamp when the record was created")

    model_config = ConfigDict(from_attributes=True)


class AllergyDeleteResponse(BaseModel):
    """Schema for deletion confirmation message."""

    message: str = Field(..., examples=["Allergy deleted successfully"])
    id: int = Field(..., examples=[1])
    user_id: int = Field(..., examples=[2])
