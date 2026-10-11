"""Exposure incident API route handlers.

Provides endpoints to record suspected exposure incidents, retrieve user exposure history,
and provide conservative interim first-aid guidance.
Note: For development and demo purposes only. No medical diagnosis is provided.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.exposure import Exposure
from app.models.user import User
from app.schemas.exposure import ExposureCreate, ExposureResponse
from app.services.exposure_assistant import evaluate_symptoms

router = APIRouter(prefix="/api/users/{user_id}/exposures", tags=["Exposure Assistant"])


def get_user_or_404(user_id: int, db: Session) -> User:
    """Ensure user exists in the database, raising HTTP 404 if not."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )
    return user


@router.post(
    "/",
    response_model=ExposureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record an exposure incident",
    description=(
        "Records a suspected allergen exposure incident and returns immediate, cautious "
        "first-aid guidance based on reported symptoms."
    ),
)
@router.post(
    "",
    response_model=ExposureResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def record_exposure(
    user_id: int,
    payload: ExposureCreate,
    db: Session = Depends(get_db),
) -> ExposureResponse:
    """
    Record an exposure incident for a user and return cautious first-aid guidance:
    1. Verifies the user exists (returns 404 if not).
    2. Saves the incident record to SQLite.
    3. Evaluates symptoms and attaches rule-based interim guidance.
    """
    # 1. Verify user exists
    get_user_or_404(user_id, db)

    # Clean symptom strings
    clean_symptoms = [s.strip() for s in payload.symptoms if s and s.strip()]

    # 2. Persist record to database
    new_exposure = Exposure(
        user_id=user_id,
        suspected_allergen=payload.suspected_allergen.strip() if payload.suspected_allergen else None,
        symptoms=clean_symptoms,
        exposure_time=payload.exposure_time,
        notes=payload.notes.strip() if payload.notes else None,
    )
    db.add(new_exposure)
    db.commit()
    db.refresh(new_exposure)

    # 3. Generate interim guidance
    guidance = evaluate_symptoms(clean_symptoms)

    return ExposureResponse(
        id=new_exposure.id,
        user_id=new_exposure.user_id,
        suspected_allergen=new_exposure.suspected_allergen,
        symptoms=new_exposure.symptoms,
        exposure_time=new_exposure.exposure_time,
        notes=new_exposure.notes,
        created_at=new_exposure.created_at,
        guidance=guidance,
    )


@router.get(
    "/",
    response_model=List[ExposureResponse],
    status_code=status.HTTP_200_OK,
    summary="List user exposure records",
    description="Retrieves exposure records for the specified user, ordered newest first.",
)
@router.get(
    "",
    response_model=List[ExposureResponse],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
def list_exposures(
    user_id: int,
    db: Session = Depends(get_db),
) -> List[ExposureResponse]:
    """
    List past exposures for a specific user:
    1. Verifies the user exists (returns 404 if not).
    2. Retrieves only records for that user, ordered newest first.
    """
    get_user_or_404(user_id, db)

    records = (
        db.query(Exposure)
        .filter(Exposure.user_id == user_id)
        .order_by(Exposure.created_at.desc(), Exposure.id.desc())
        .all()
    )

    return [ExposureResponse.model_validate(r) for r in records]
