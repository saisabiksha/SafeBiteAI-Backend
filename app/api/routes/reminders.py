"""Reminder API route handlers.

Provides CRUD endpoints for user reminders (hydration, medication, appointments, general).
Note: These entries represent stored schedules only; they do not trigger external push alerts or formulate medical advice.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.reminder import Reminder
from app.models.user import User
from app.schemas.reminder import (
    ReminderCategory,
    ReminderCreate,
    ReminderDeleteResponse,
    ReminderResponse,
    ReminderUpdate,
)

router = APIRouter(prefix="/api/users/{user_id}/reminders", tags=["Reminders"])


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
    response_model=ReminderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a reminder",
    description=(
        "Creates a stored reminder schedule (hydration, medication, appointment, or general). "
        "For medication reminders, only schedules explicitly provided by the user or clinician are stored."
    ),
)
@router.post(
    "",
    response_model=ReminderResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_reminder(
    user_id: int,
    payload: ReminderCreate,
    db: Session = Depends(get_db),
) -> Reminder:
    """Create a new reminder record scoped to the specified user."""
    get_user_or_404(user_id, db)

    new_reminder = Reminder(
        user_id=user_id,
        title=payload.title.strip(),
        category=payload.category,
        scheduled_at=payload.scheduled_at,
        notes=payload.notes.strip() if payload.notes else None,
        is_completed=payload.is_completed,
    )
    db.add(new_reminder)
    db.commit()
    db.refresh(new_reminder)

    return new_reminder


@router.get(
    "/",
    response_model=List[ReminderResponse],
    status_code=status.HTTP_200_OK,
    summary="List reminders",
    description="Retrieves reminders for the specified user, optionally filtered by category.",
)
@router.get(
    "",
    response_model=List[ReminderResponse],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
def list_reminders(
    user_id: int,
    category: Optional[ReminderCategory] = Query(
        default=None,
        description="Filter reminders by category (hydration, medication, appointment, general)",
    ),
    db: Session = Depends(get_db),
) -> List[Reminder]:
    """List reminders scoped to the requested user, ordered by scheduled time."""
    get_user_or_404(user_id, db)

    query = db.query(Reminder).filter(Reminder.user_id == user_id)
    if category:
        query = query.filter(Reminder.category == category)

    reminders = query.order_by(Reminder.scheduled_at.asc(), Reminder.id.asc()).all()
    return reminders


@router.put(
    "/{reminder_id}",
    response_model=ReminderResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a reminder",
    description="Updates fields of an existing reminder scoped to the user.",
)
def update_reminder(
    user_id: int,
    reminder_id: int,
    payload: ReminderUpdate,
    db: Session = Depends(get_db),
) -> Reminder:
    """Update a reminder record scoped to the specified user."""
    get_user_or_404(user_id, db)

    reminder = (
        db.query(Reminder)
        .filter(Reminder.id == reminder_id, Reminder.user_id == user_id)
        .first()
    )
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reminder with ID {reminder_id} not found for user {user_id}.",
        )

    if payload.title is not None:
        reminder.title = payload.title.strip()
    if payload.category is not None:
        reminder.category = payload.category
    if payload.scheduled_at is not None:
        reminder.scheduled_at = payload.scheduled_at
    if payload.notes is not None:
        reminder.notes = payload.notes.strip() if payload.notes else None
    if payload.is_completed is not None:
        reminder.is_completed = payload.is_completed

    db.commit()
    db.refresh(reminder)

    return reminder


@router.delete(
    "/{reminder_id}",
    response_model=ReminderDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a reminder",
    description="Deletes a reminder record scoped to the user.",
)
def delete_reminder(
    user_id: int,
    reminder_id: int,
    db: Session = Depends(get_db),
) -> ReminderDeleteResponse:
    """Delete a reminder record scoped to the specified user."""
    get_user_or_404(user_id, db)

    reminder = (
        db.query(Reminder)
        .filter(Reminder.id == reminder_id, Reminder.user_id == user_id)
        .first()
    )
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reminder with ID {reminder_id} not found for user {user_id}.",
        )

    db.delete(reminder)
    db.commit()

    return ReminderDeleteResponse(
        message="Reminder deleted successfully",
        id=reminder_id,
        user_id=user_id,
    )
