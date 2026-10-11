"""Food checker API route endpoints.

Provides deterministic screening of food ingredients against a user's saved allergies,
as well as vision-based food packaging label scanning via Gemini.
Note: For development and demo purposes only. No medical diagnosis or safety guarantee is provided.
"""
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.allergy import Allergy
from app.models.user import User
from app.schemas.food_check import (
    FoodCheckRequest,
    FoodCheckResponse,
    ScanLabelResponse,
)
from app.services.food_checker import check_food_for_allergens
from app.services.label_scanner import extract_ingredients_from_image

router = APIRouter(prefix="/api/users/{user_id}/food-check", tags=["Food Checker"])

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post(
    "/",
    response_model=FoodCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Screen food ingredients for user allergens",
    description=(
        "Deterministically checks a food product's ingredient list against the user's saved allergies. "
        "Returns detection status, matching terms, and a mandatory safety disclaimer."
    ),
)
@router.post(
    "",
    response_model=FoodCheckResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
def screen_food(
    user_id: int,
    payload: FoodCheckRequest,
    db: Session = Depends(get_db),
) -> FoodCheckResponse:
    """
    Screen food ingredients for a specific user:
    1. Verifies user exists (returns HTTP 404 if not found).
    2. Loads user's saved allergies and aliases from the SQLite database.
    3. Runs deterministic, case-normalized keyword and alias matching.
    4. Returns appropriate status ('potential_allergen_detected', 'no_listed_allergen_identified', or 'unable_to_verify').
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )

    user_allergies = db.query(Allergy).filter(Allergy.user_id == user_id).all()

    return check_food_for_allergens(
        food_name=payload.food_name,
        user_id=user_id,
        raw_ingredients=payload.ingredients,
        user_allergies=user_allergies,
    )


@router.post(
    "/scan-label",
    response_model=ScanLabelResponse,
    status_code=status.HTTP_200_OK,
    summary="Scan food label image for allergens",
    description=(
        "Uploads a food packaging label image (JPEG, PNG, or WebP up to 5 MB), extracts visible "
        "ingredient text using Gemini vision, and screens against the user's saved allergies."
    ),
)
async def scan_label(
    user_id: int,
    file: UploadFile = File(
        ...,
        description="Image file of the food label or ingredients list (JPEG, PNG, or WebP, max 5 MB)",
    ),
    food_name: Optional[str] = Form(
        default="Scanned Food Product",
        description="Optional name or title for the scanned food item",
    ),
    db: Session = Depends(get_db),
) -> ScanLabelResponse:
    """
    Scan a food label image:
    1. Verifies the user exists in SQLite (returns 404 if missing).
    2. Validates image MIME type (JPEG, PNG, WebP) and 5 MB size limit.
    3. Reads image bytes safely in memory without permanent disk storage.
    4. Uses Gemini vision model to extract only clearly visible ingredient text.
    5. Feeds extracted ingredients into existing deterministic allergen-matching logic.
    6. Returns extracted terms, readability status, detected allergens, and safety disclaimer.
    """
    # 1. Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )

    # 2. Validate MIME type
    content_type = file.content_type or ""
    if content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format. Supported formats: image/jpeg, image/png, image/webp.",
        )

    # 3. Read image bytes into memory and validate size
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded image file is empty.",
        )
    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file size exceeds the 5 MB limit.",
        )

    # 4. Extract ingredients using Gemini vision
    extracted_ingredients, is_readable, uncertainty = extract_ingredients_from_image(
        image_bytes=image_bytes,
        mime_type=content_type,
    )

    # 5. Load user allergies from database
    user_allergies = db.query(Allergy).filter(Allergy.user_id == user_id).all()

    # 6. Pass extracted ingredients to existing check_food_for_allergens logic
    cleaned_food_name = food_name.strip() if food_name else "Scanned Food Product"
    check_result = check_food_for_allergens(
        food_name=cleaned_food_name,
        user_id=user_id,
        raw_ingredients=extracted_ingredients,
        user_allergies=user_allergies,
    )

    # 7. Safety assessment:
    # If a potential allergen is matched, clearly report it.
    # If no allergen is found but the label was unreadable or incomplete, return 'unable_to_verify'.
    if check_result.status == "potential_allergen_detected":
        final_status = "potential_allergen_detected"
        final_message = check_result.message
    elif not is_readable or not extracted_ingredients:
        final_status = "unable_to_verify"
        final_message = (
            uncertainty
            or "The food label could not be verified completely or was unreadable. "
            "Do not assume this food is safe."
        )
    else:
        final_status = check_result.status
        final_message = check_result.message

    return ScanLabelResponse(
        food_name=cleaned_food_name,
        user_id=user_id,
        extracted_ingredients=extracted_ingredients,
        is_complete_and_readable=is_readable,
        uncertainty_or_notes=uncertainty,
        status=final_status,
        message=final_message,
        detected_allergens=check_result.detected_allergens,
        detected_ingredients=check_result.detected_ingredients,
        matches=check_result.matches,
        disclaimer=check_result.disclaimer,
    )
