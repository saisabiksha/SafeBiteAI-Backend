"""Allergy API route endpoints.

Provides CRUD operations for user allergies.
Note: These endpoints are intended for development and demo purposes.
Authentication, passwords, and sensitive medical decision logic are excluded at this stage.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.allergy import Allergy
from app.models.user import User
from app.schemas.allergy import (
    AllergyCreate,
    AllergyDeleteResponse,
    AllergyResponse,
    AllergyUpdate,
)

router = APIRouter(prefix="/api/users/{user_id}/allergies", tags=["Allergies"])


def get_user_or_404(user_id: int, db: Session) -> User:
    """Helper to verify user existence and return User instance."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )
    return user


@router.post(
    "/",
    response_model=AllergyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an allergy for a user",
    description="Adds a new allergen to the specified user profile. Rejects case-insensitive duplicates.",
)
@router.post(
    "",
    response_model=AllergyResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def add_allergy(
    user_id: int,
    allergy_in: AllergyCreate,
    db: Session = Depends(get_db),
) -> Allergy:
    """Add a new allergy record for a specific user."""
    # Ensure parent user exists
    get_user_or_404(user_id, db)

    normalized_name = allergy_in.allergen_name.strip()

    # Prevent duplicate allergen entries for this user (case-insensitive)
    existing_allergy = (
        db.query(Allergy)
        .filter(
            Allergy.user_id == user_id,
            func.lower(Allergy.allergen_name) == normalized_name.lower(),
        )
        .first()
    )
    if existing_allergy:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Allergy '{normalized_name}' already exists for user {user_id}.",
        )

    new_allergy = Allergy(
        user_id=user_id,
        allergen_name=normalized_name,
        category=allergy_in.category.strip(),
        aliases=allergy_in.aliases,
        notes=allergy_in.notes,
    )

    db.add(new_allergy)
    db.commit()
    db.refresh(new_allergy)

    return new_allergy


@router.get(
    "/",
    response_model=List[AllergyResponse],
    status_code=status.HTTP_200_OK,
    summary="List allergies for a user",
    description="Retrieves all registered allergies associated with the specified user profile.",
)
@router.get(
    "",
    response_model=List[AllergyResponse],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
def list_allergies(
    user_id: int,
    db: Session = Depends(get_db),
) -> List[Allergy]:
    """List all allergies for a specific user."""
    # Ensure parent user exists
    get_user_or_404(user_id, db)

    allergies = db.query(Allergy).filter(Allergy.user_id == user_id).all()
    return allergies


@router.put(
    "/{allergy_id}",
    response_model=AllergyResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an allergy",
    description="Updates an existing allergy for the specified user.",
)
def update_allergy(
    user_id: int,
    allergy_id: int,
    allergy_in: AllergyUpdate,
    db: Session = Depends(get_db),
) -> Allergy:
    """Update an allergy record scoped to the specified user."""
    # Ensure parent user exists
    get_user_or_404(user_id, db)

    # Ensure allergy exists and belongs to this user
    allergy = (
        db.query(Allergy)
        .filter(
            Allergy.id == allergy_id,
            Allergy.user_id == user_id,
        )
        .first()
    )
    if not allergy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Allergy with ID {allergy_id} not found for user {user_id}.",
        )

    # Check for duplicate name collision if updating allergen_name
    if allergy_in.allergen_name is not None:
        normalized_name = allergy_in.allergen_name.strip()
        conflict = (
            db.query(Allergy)
            .filter(
                Allergy.user_id == user_id,
                Allergy.id != allergy_id,
                func.lower(Allergy.allergen_name) == normalized_name.lower(),
            )
            .first()
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Allergy '{normalized_name}' already exists for user {user_id}.",
            )
        allergy.allergen_name = normalized_name

    if allergy_in.category is not None:
        allergy.category = allergy_in.category.strip()

    if allergy_in.aliases is not None:
        allergy.aliases = allergy_in.aliases

    if allergy_in.notes is not None:
        allergy.notes = allergy_in.notes

    db.commit()
    db.refresh(allergy)

    return allergy


@router.delete(
    "/{allergy_id}",
    response_model=AllergyDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete an allergy",
    description="Removes an allergy record scoped to the specified user.",
)
def delete_allergy(
    user_id: int,
    allergy_id: int,
    db: Session = Depends(get_db),
) -> AllergyDeleteResponse:
    """Delete an allergy record scoped to the specified user."""
    # Ensure parent user exists
    get_user_or_404(user_id, db)

    # Ensure allergy exists and belongs to this user
    allergy = (
        db.query(Allergy)
        .filter(
            Allergy.id == allergy_id,
            Allergy.user_id == user_id,
        )
        .first()
    )
    if not allergy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Allergy with ID {allergy_id} not found for user {user_id}.",
        )

    db.delete(allergy)
    db.commit()

    return AllergyDeleteResponse(
        message="Allergy deleted successfully",
        id=allergy_id,
        user_id=user_id,
    )
