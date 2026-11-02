from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.admin.service import (
    assign_patient_to_therapist,
    get_admin_assignments,
    get_admin_safety_activity,
    get_admin_summary,
    get_admin_system_metadata,
    get_admin_users,
    get_available_therapists,
    remove_patient_assignment,
)
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.db_tables import User


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


class AssignmentRequest(BaseModel):
    therapist_id: int


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required.",
        )

    return current_user


@router.get("/summary")
def admin_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        return get_admin_summary(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin summary could not be loaded.",
        ) from exc


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        users = get_admin_users(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Users could not be loaded.",
        ) from exc

    return {
        "users": users,
    }


@router.get("/therapists")
def list_therapists(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        therapists = get_available_therapists(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Therapists could not be loaded.",
        ) from exc

    return {
        "therapists": therapists,
    }


@router.get("/assignments")
def list_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        assignments = get_admin_assignments(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Patient assignments could not be loaded.",
        ) from exc

    return {
        "assignments": assignments,
    }


@router.get("/safety")
def list_safety_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        activity = get_admin_safety_activity(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Safety activity could not be loaded.",
        ) from exc

    return {
        "activity": activity,
    }


@router.get("/system")
def system_metadata(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        return get_admin_system_metadata(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System metadata could not be loaded.",
        ) from exc


@router.put("/assignments/{patient_id}")
def update_assignment(
    patient_id: int,
    payload: AssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        assignment = assign_patient_to_therapist(
            db,
            patient_id,
            payload.therapist_id,
        )
    except SQLAlchemyError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Patient assignment could not be updated.",
        ) from exc

    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active patient or therapist not found.",
        )

    return assignment


@router.delete("/assignments/{patient_id}")
def delete_assignment(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        removed = remove_patient_assignment(
            db,
            patient_id,
        )
    except SQLAlchemyError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Patient assignment could not be removed.",
        ) from exc

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient assignment not found.",
        )

    return {
        "patient_id": patient_id,
        "removed": True,
    }