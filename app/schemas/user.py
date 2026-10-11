"""Pydantic schemas for user profile data validation and serialization."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """
    Shared attributes for user profiles.
    Note: These endpoints are for development and testing; no sensitive credentials are stored.
    """

    full_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Full name of the user",
        examples=["Jane Doe"],
    )
    email: EmailStr = Field(
        ...,
        description="Unique email address",
        examples=["jane.doe@example.com"],
    )
    age: Optional[int] = Field(
        default=None,
        ge=0,
        le=130,
        description="Age of the user in years (optional)",
        examples=[28],
    )
    height_cm: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=300.0,
        description="Height in centimeters (optional)",
        examples=[168.5],
    )
    weight_kg: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=500.0,
        description="Weight in kilograms (optional)",
        examples=[62.0],
    )


class UserCreate(UserBase):
    """Schema for creating a new user profile."""
    pass


class UserResponse(UserBase):
    """
    Schema for serialized user profile responses.
    """

    id: int = Field(..., description="Unique database identifier for the user", examples=[1])
    created_at: datetime = Field(..., description="Timestamp when the record was created")

    model_config = ConfigDict(from_attributes=True)
