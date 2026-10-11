"""User profile API route endpoints.

Note: These endpoints are intended for development and demo purposes.
Authentication, passwords, and sensitive medical data are intentionally excluded at this stage.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user profile",
    description="Creates a new user profile with basic metadata. Rejects duplicate email addresses.",
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> User:
    """
    Create a new user profile.
    - Validates email format via Pydantic.
    - Returns HTTP 409 Conflict if email is already registered.
    """
    # Check for existing user with the same email
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists.",
        )

    # Instantiate new User model
    new_user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        age=user_in.age,
        height_cm=user_in.height_cm,
        weight_kg=user_in.weight_kg,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user profile by ID",
    description="Retrieves a user profile by their unique ID.",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> User:
    """
    Retrieve user profile by unique ID.
    - Returns HTTP 404 if user not found.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )

    return user
