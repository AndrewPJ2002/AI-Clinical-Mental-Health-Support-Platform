from sqlalchemy.orm import Session

from app.chat.service import (
    get_conversation_messages_for_user,
    get_user_conversations,
)
from app.db_tables import (
    Notification,
    RedFlagEvent,
    TherapistPatientAssignment,
    User,
)


def therapist_has_patient(
    db: Session,
    therapist_id: int,
    patient_id: int,
) -> bool:
    assignment = (
        db.query(TherapistPatientAssignment)
        .filter(
            TherapistPatientAssignment.therapist_id == therapist_id,
            TherapistPatientAssignment.patient_id == patient_id,
        )
        .first()
    )

    return assignment is not None


def get_assigned_patients(
    db: Session,
    therapist_id: int,
) -> list[dict]:
    patients = (
        db.query(User)
        .join(
            TherapistPatientAssignment,
            TherapistPatientAssignment.patient_id == User.id,
        )
        .filter(
            TherapistPatientAssignment.therapist_id == therapist_id,
            User.role == "patient",
            User.is_active.is_(True),
        )
        .order_by(
            User.last_name.asc(),
            User.first_name.asc(),
        )
        .all()
    )

    return [
        {
            "id": patient.id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "email": patient.email,
        }
        for patient in patients
    ]


def get_assigned_patient_conversations(
    db: Session,
    therapist_id: int,
    patient_id: int,
):
    if not therapist_has_patient(
        db,
        therapist_id,
        patient_id,
    ):
        return None

    conversations = get_user_conversations(
        db,
        patient_id,
    )

    red_flag_events = (
        db.query(RedFlagEvent)
        .filter(
            RedFlagEvent.patient_id == patient_id,
        )
        .order_by(
            RedFlagEvent.detected_at.desc(),
            RedFlagEvent.id.desc(),
        )
        .all()
    )

    flags_by_conversation = {}

    for event in red_flag_events:
        existing = flags_by_conversation.get(
            event.conversation_id
        )

        if existing is None:
            flags_by_conversation[
                event.conversation_id
            ] = event
            continue

        if (
            event.severity == "high"
            and existing.severity != "high"
        ):
            flags_by_conversation[
                event.conversation_id
            ] = event

    for conversation in conversations:
        event = flags_by_conversation.get(
            conversation["id"]
        )

        conversation["flagged"] = event is not None
        conversation["flag_severity"] = (
            event.severity
            if event is not None
            else None
        )
        conversation["flag_status"] = (
            event.status
            if event is not None
            else None
        )

    return conversations


def get_assigned_patient_conversation(
    db: Session,
    therapist_id: int,
    patient_id: int,
    chat_id: int,
):
    if not therapist_has_patient(
        db,
        therapist_id,
        patient_id,
    ):
        return None

    conversation = get_conversation_messages_for_user(
        db,
        chat_id,
        patient_id,
    )

    if conversation is None:
        return None

    red_flag_events = (
        db.query(RedFlagEvent)
        .filter(
            RedFlagEvent.patient_id == patient_id,
            RedFlagEvent.conversation_id == chat_id,
        )
        .order_by(
            RedFlagEvent.detected_at.desc(),
            RedFlagEvent.id.desc(),
        )
        .all()
    )

    conversation["red_flags"] = [
        {
            "id": event.id,
            "message_id": event.message_id,
            "severity": event.severity,
            "status": event.status,
            "detected_at": event.detected_at,
        }
        for event in red_flag_events
    ]

    return conversation


def get_therapist_notifications(
    db: Session,
    therapist_id: int,
) -> list[dict]:
    notifications = (
        db.query(Notification)
        .filter(
            Notification.recipient_user_id == therapist_id,
        )
        .order_by(
            Notification.created_at.desc(),
            Notification.id.desc(),
        )
        .all()
    )

    results = []

    for notification in notifications:
        red_flag_event = None
        patient = None

        if notification.red_flag_event_id is not None:
            red_flag_event = (
                db.query(RedFlagEvent)
                .filter(
                    RedFlagEvent.id
                    == notification.red_flag_event_id,
                )
                .first()
            )

        if red_flag_event is not None:
            patient = (
                db.query(User)
                .filter(
                    User.id == red_flag_event.patient_id,
                )
                .first()
            )

        results.append(
            {
                "id": notification.id,
                "type": notification.type,
                "message": notification.message,
                "is_read": notification.is_read,
                "created_at": notification.created_at,
                "red_flag_event_id": (
                    red_flag_event.id
                    if red_flag_event is not None
                    else None
                ),
                "conversation_id": (
                    red_flag_event.conversation_id
                    if red_flag_event is not None
                    else None
                ),
                "patient_id": (
                    red_flag_event.patient_id
                    if red_flag_event is not None
                    else None
                ),
                "patient_first_name": (
                    patient.first_name
                    if patient is not None
                    else None
                ),
                "patient_last_name": (
                    patient.last_name
                    if patient is not None
                    else None
                ),
                "severity": (
                    red_flag_event.severity
                    if red_flag_event is not None
                    else None
                ),
                "status": (
                    red_flag_event.status
                    if red_flag_event is not None
                    else None
                ),
            }
        )

    return results


def mark_notification_reviewed(
    db: Session,
    therapist_id: int,
    notification_id: int,
) -> dict | None:
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.recipient_user_id == therapist_id,
        )
        .first()
    )

    if notification is None:
        return None

    notification.is_read = True

    red_flag_event = None

    if notification.red_flag_event_id is not None:
        red_flag_event = (
            db.query(RedFlagEvent)
            .filter(
                RedFlagEvent.id
                == notification.red_flag_event_id,
            )
            .first()
        )

    if red_flag_event is not None:
        red_flag_event.status = "reviewed"

    db.commit()

    return {
        "notification_id": notification.id,
        "is_read": notification.is_read,
        "red_flag_event_id": (
            red_flag_event.id
            if red_flag_event is not None
            else None
        ),
        "status": (
            red_flag_event.status
            if red_flag_event is not None
            else None
        ),
    }