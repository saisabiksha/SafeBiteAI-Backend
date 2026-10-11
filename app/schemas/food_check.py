"""Pydantic schemas for the food checking endpoint."""
from typing import List, Optional

from pydantic import BaseModel, Field


class FoodCheckRequest(BaseModel):
    """Request payload for food allergen screening."""

    food_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Name of the food product or dish to check",
        examples=["Peanut Butter Granola Bar"],
    )
    ingredients: List[str] = Field(
        default_factory=list,
        description="List of declared ingredients",
        examples=[["rolled oats", "sugar", "peanut butter", "chocolate chips"]],
    )


class AllergenMatch(BaseModel):
    """Details of a detected allergen match."""

    allergen_name: str = Field(
        ...,
        description="Name of the user's registered allergen that matched",
        examples=["Peanut"],
    )
    category: str = Field(
        ...,
        description="Category of the allergen (e.g. food)",
        examples=["food"],
    )
    matched_ingredient: str = Field(
        ...,
        description="The ingredient string from the food that triggered the match",
        examples=["peanut butter"],
    )
    matched_term: str = Field(
        ...,
        description="The allergen name or alias term that was found in the ingredient",
        examples=["peanut"],
    )


class FoodCheckResponse(BaseModel):
    """Response payload for food allergen screening."""

    food_name: str = Field(..., description="Name of the food product checked")
    user_id: int = Field(..., description="ID of the user profile whose allergies were screened")
    status: str = Field(
        ...,
        description="Outcome status: potential_allergen_detected | no_listed_allergen_identified | unable_to_verify",
        examples=["potential_allergen_detected"],
    )
    message: str = Field(..., description="Human-readable summary of the check result")
    detected_allergens: List[str] = Field(
        default_factory=list,
        description="List of registered allergen names detected in the food",
    )
    detected_ingredients: List[str] = Field(
        default_factory=list,
        description="List of specific ingredients that triggered a match",
    )
    matches: List[AllergenMatch] = Field(
        default_factory=list,
        description="Detailed list of detected allergen matches",
    )
    disclaimer: str = Field(
        ...,
        description="Mandatory medical and food safety disclaimer",
    )


class ScanLabelResponse(BaseModel):
    """Response payload for food label image scanning and allergen screening."""

    food_name: str = Field(..., description="Name of the food product or label")
    user_id: int = Field(..., description="ID of the user profile whose allergies were screened")
    extracted_ingredients: List[str] = Field(
        default_factory=list,
        description="List of ingredients extracted from the package image by Gemini vision",
        examples=[["Sugar", "Peanuts", "Milk powder", "Salt"]],
    )
    is_complete_and_readable: bool = Field(
        ...,
        description="Whether the ingredient text appeared legible and unoccluded on the image",
        examples=[True],
    )
    uncertainty_or_notes: Optional[str] = Field(
        default=None,
        description="Notes regarding image clarity, partial occlusions, or extraction issues",
        examples=[None],
    )
    status: str = Field(
        ...,
        description="Outcome status: potential_allergen_detected | no_listed_allergen_identified | unable_to_verify",
        examples=["potential_allergen_detected"],
    )
    message: str = Field(..., description="Human-readable summary of the allergen evaluation")
    detected_allergens: List[str] = Field(
        default_factory=list,
        description="User-registered allergens that were detected in the extracted text",
        examples=[["Peanut"]],
    )
    detected_ingredients: List[str] = Field(
        default_factory=list,
        description="Specific ingredients extracted from the label that matched",
        examples=[["Peanuts"]],
    )
    matches: List[AllergenMatch] = Field(
        default_factory=list,
        description="Detailed list of detected allergen matches",
    )
    disclaimer: str = Field(
        ...,
        description="Mandatory medical and food safety disclaimer",
    )
