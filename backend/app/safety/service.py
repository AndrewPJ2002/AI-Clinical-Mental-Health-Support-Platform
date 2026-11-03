from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db_tables import (
    Notification,
    RedFlagDefinition,
    RedFlagEvent,
    TherapistPatientAssignment,
)


def record_red_flag_and_notify(
    db: Session,
    patient_id: int,
    conversation_id: int,
    message_id: int,
    severity: str,
) -> RedFlagEvent | None:
    """
    Persist a detected red flag and notify the patient's
    assigned therapist or therapists.

    Low-risk messages are not persisted as red-flag events.
    """

    if severity == "low":
        return None

    definition = _get_or_create_definition(
        db,
        severity,
    )

    red_flag_event = RedFlagEvent(
        message_id=message_id,
        red_flag_definition_id=definition.id,
        patient_id=patient_id,
        conversation_id=conversation_id,
        severity=severity,
        status="unreviewed",
    )

    db.add(red_flag_event)

    try:
        db.commit()
        db.refresh(red_flag_event)
    except SQLAlchemyError:
        db.rollback()
        raise

    therapist_assignments = (
        db.query(TherapistPatientAssignment)
        .filter(
            TherapistPatientAssignment.patient_id == patient_id,
        )
        .all()
    )

    for assignment in therapist_assignments:
        notification = Notification(
            recipient_user_id=assignment.therapist_id,
            red_flag_event_id=red_flag_event.id,
            type="red_flag",
            message=(
                f"A {severity}-risk message was detected "
                f"in conversation {conversation_id}."
            ),
            is_read=False,
        )

        db.add(notification)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return red_flag_event


def _get_or_create_definition(
    db: Session,
    severity: str,
) -> RedFlagDefinition:
    """
    Return the runtime safety-rule definition for this severity,
    creating it when it does not already exist.
    """

    definition_name = (
        f"{severity.capitalize()} Risk Safety Trigger"
    )

    definition = (
        db.query(RedFlagDefinition)
        .filter(
            RedFlagDefinition.name == definition_name,
        )
        .first()
    )

    if definition is not None:
        return definition

    definition = RedFlagDefinition(
        name=definition_name,
        description=(
            "Message identified by the Anchored Support Services "
            "runtime safety screening process."
        ),
        detection_pattern="runtime:safety.risk_response",
        severity=severity,
        is_active=True,
    )

    db.add(definition)

    try:
        db.commit()
        db.refresh(definition)
    except SQLAlchemyError:
        db.rollback()
        raise

    return definition