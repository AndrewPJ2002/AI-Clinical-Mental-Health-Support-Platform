from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.db_tables import User
from app.therapist.service import (
    get_assigned_patient_conversation,
    get_assigned_patient_conversations,
    get_assigned_patients,
    get_therapist_notifications,
    mark_notification_reviewed,
)


router = APIRouter(
    prefix="/therapist",
    tags=["Therapist"],
)


def require_therapist(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Allow access only to authenticated therapist accounts.
    """

    if current_user.role != "therapist":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Therapist access required.",
        )

    return current_user


@router.get("/patients")
def list_assigned_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_therapist),
):
    """
    Return active patients assigned to the authenticated therapist.
    """

    try:
        patients = get_assigned_patients(
            db,
            current_user.id,
        )
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Assigned patients could not be loaded.",
        ) from exc

    return {
        "patients": patients,
    }


@router.get("/notifications")
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_therapist),
):
    """
    Return notifications belonging to the authenticated therapist.
    """

    try:
        notifications = get_therapist_notifications(
            db,
            current_user.id,
        )
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Therapist notifications could not be loaded.",
        ) from exc

    return {
        "notifications": notifications,
    }


@router.patch("/notifications/{notification_id}/review")
def review_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_therapist),
):
    """
    Mark a therapist notification as read and its linked
    red-flag event as reviewed.
    """

    try:
        result = mark_notification_reviewed(
            db,
            current_user.id,
            notification_id,
        )
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The notification could not be updated.",
        ) from exc

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )

    return result


@router.get("/patients/{patient_id}/conversations")
def list_patient_conversations(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_therapist),
):
    """
    Return conversation history only for a patient
    assigned to the authenticated therapist.
    """

    try:
        conversations = get_assigned_patient_conversations(
            db,
            current_user.id,
            patient_id,
        )
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Patient conversation history could not be loaded.",
        ) from exc

    if conversations is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned patient not found.",
        )

    return {
        "patient_id": patient_id,
        "conversations": conversations,
    }


@router.get(
    "/patients/{patient_id}/conversations/{chat_id}"
)
def get_patient_conversation(
    patient_id: int,
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_therapist),
):
    """
    Return the original conversation only when the patient
    is assigned to the authenticated therapist.
    """

    try:
        conversation = get_assigned_patient_conversation(
            db,
            current_user.id,
            patient_id,
            chat_id,
        )
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The conversation could not be loaded.",
        ) from exc

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    return conversation