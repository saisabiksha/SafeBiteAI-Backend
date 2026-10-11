"""Hydration intake API route handlers.

Endpoints to log fluid consumption, retrieve records by date, and fetch daily intake summaries.
"""
from datetime import date, datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.hydration import HydrationRecord
from app.models.user import User
from app.schemas.hydration import (
    HydrationCreate,
    HydrationResponse,
    HydrationSummaryResponse,
)

router = APIRouter(prefix="/api/users/{user_id}/hydration", tags=["Hydration Tracker"])


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
    response_model=HydrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record water intake",
    description="Logs fluid consumption volume in millilitres for a specified user.",
)
@router.post(
    "",
    response_model=HydrationResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def record_hydration(
    user_id: int,
    payload: HydrationCreate,
    db: Session = Depends(get_db),
) -> HydrationResponse:
    """
    Record a water intake entry:
    1. Verifies the user exists (returns 404 if missing).
    2. Validates positive quantity (enforced by Pydantic gt=0).
    3. Saves entry to the SQLite database.
    """
    get_user_or_404(user_id, db)

    effective_recorded_at = payload.recorded_at or datetime.now(timezone.utc)

    record = HydrationRecord(
        user_id=user_id,
        amount_ml=payload.amount_ml,
        recorded_at=effective_recorded_at,
        notes=payload.notes.strip() if payload.notes else None,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return record


@router.get(
    "/summary",
    response_model=HydrationSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get daily hydration summary",
    description="Returns total recorded water intake for a specific date (defaults to current date).",
)
def get_hydration_summary(
    user_id: int,
    target_date: Optional[date] = Query(
        default=None,
        alias="date",
        description="Filter by specific date (YYYY-MM-DD). Defaults to current date if omitted.",
    ),
    db: Session = Depends(get_db),
) -> HydrationSummaryResponse:
    """
    Get aggregated water intake for a given calendar date:
    1. Verifies the user exists (404 if not).
    2. Sums total millilitres logged on that date.
    3. Returns totals clearly labelled as recorded intake (not medical advice).
    """
    get_user_or_404(user_id, db)

    selected_date = target_date or datetime.now(timezone.utc).date()
    date_str = selected_date.strftime("%Y-%m-%d")

    records = (
        db.query(HydrationRecord)
        .filter(
            HydrationRecord.user_id == user_id,
            func.date(HydrationRecord.recorded_at) == date_str,
        )
        .all()
    )

    total_ml = sum(r.amount_ml for r in records)
    entry_count = len(records)

    return HydrationSummaryResponse(
        user_id=user_id,
        date=selected_date,
        total_amount_ml=total_ml,
        entry_count=entry_count,
    )


@router.get(
    "/",
    response_model=List[HydrationResponse],
    status_code=status.HTTP_200_OK,
    summary="List hydration records for a date",
    description="Lists individual water intake entries for a requested date (defaults to current date).",
)
@router.get(
    "",
    response_model=List[HydrationResponse],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
def list_hydration_records(
    user_id: int,
    target_date: Optional[date] = Query(
        default=None,
        alias="date",
        description="Filter entries for a specific date (YYYY-MM-DD). Defaults to current date if omitted.",
    ),
    db: Session = Depends(get_db),
) -> List[HydrationRecord]:
    """
    List hydration logs for a user on a given date:
    1. Verifies the user exists (404 if not).
    2. Retrieves entries matching the target date, ordered newest first.
    """
    get_user_or_404(user_id, db)

    selected_date = target_date or datetime.now(timezone.utc).date()
    date_str = selected_date.strftime("%Y-%m-%d")

    records = (
        db.query(HydrationRecord)
        .filter(
            HydrationRecord.user_id == user_id,
            func.date(HydrationRecord.recorded_at) == date_str,
        )
        .order_by(HydrationRecord.recorded_at.desc(), HydrationRecord.id.desc())
        .all()
    )

    return records
