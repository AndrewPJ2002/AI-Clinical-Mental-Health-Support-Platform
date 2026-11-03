from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.config import settings
from app.db_tables import (
    RedFlagEvent,
    TherapistPatientAssignment,
    User,
)


def get_admin_summary(
    db: Session,
) -> dict:
    active_patients = (
        db.query(func.count(User.id))
        .filter(
            User.role == "patient",
            User.is_active.is_(True),
        )
        .scalar()
        or 0
    )

    active_therapists = (
        db.query(func.count(User.id))
        .filter(
            User.role == "therapist",
            User.is_active.is_(True),
        )
        .scalar()
        or 0
    )

    assignments = (
        db.query(func.count(TherapistPatientAssignment.id))
        .scalar()
        or 0
    )

    unreviewed_flags = (
        db.query(func.count(RedFlagEvent.id))
        .filter(
            RedFlagEvent.status == "unreviewed",
        )
        .scalar()
        or 0
    )

    return {
        "active_patients": active_patients,
        "active_therapists": active_therapists,
        "assignments": assignments,
        "unreviewed_flags": unreviewed_flags,
    }


def get_admin_users(
    db: Session,
) -> list[dict]:
    users = (
        db.query(User)
        .order_by(
            User.role.asc(),
            User.last_name.asc(),
            User.first_name.asc(),
        )
        .all()
    )

    return [
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
        }
        for user in users
    ]


def get_admin_assignments(
    db: Session,
) -> list[dict]:
    patients = (
        db.query(User)
        .filter(
            User.role == "patient",
            User.is_active.is_(True),
        )
        .order_by(
            User.last_name.asc(),
            User.first_name.asc(),
        )
        .all()
    )

    results = []

    for patient in patients:
        assignment = (
            db.query(TherapistPatientAssignment)
            .filter(
                TherapistPatientAssignment.patient_id
                == patient.id,
            )
            .first()
        )

        therapist = None

        if assignment is not None:
            therapist = (
                db.query(User)
                .filter(
                    User.id == assignment.therapist_id,
                    User.role == "therapist",
                )
                .first()
            )

        results.append(
            {
                "patient_id": patient.id,
                "patient_first_name": patient.first_name,
                "patient_last_name": patient.last_name,
                "patient_email": patient.email,
                "assignment_id": (
                    assignment.id
                    if assignment is not None
                    else None
                ),
                "therapist_id": (
                    therapist.id
                    if therapist is not None
                    else None
                ),
                "therapist_first_name": (
                    therapist.first_name
                    if therapist is not None
                    else None
                ),
                "therapist_last_name": (
                    therapist.last_name
                    if therapist is not None
                    else None
                ),
                "therapist_email": (
                    therapist.email
                    if therapist is not None
                    else None
                ),
            }
        )

    return results


def get_available_therapists(
    db: Session,
) -> list[dict]:
    therapists = (
        db.query(User)
        .filter(
            User.role == "therapist",
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
            "id": therapist.id,
            "first_name": therapist.first_name,
            "last_name": therapist.last_name,
            "email": therapist.email,
        }
        for therapist in therapists
    ]


def get_admin_safety_activity(
    db: Session,
) -> list[dict]:
    events = (
        db.query(RedFlagEvent)
        .order_by(
            RedFlagEvent.detected_at.desc(),
            RedFlagEvent.id.desc(),
        )
        .all()
    )

    results = []

    for event in events:
        patient = (
            db.query(User)
            .filter(
                User.id == event.patient_id,
                User.role == "patient",
            )
            .first()
        )

        assignment = (
            db.query(TherapistPatientAssignment)
            .filter(
                TherapistPatientAssignment.patient_id
                == event.patient_id,
            )
            .first()
        )

        therapist = None

        if assignment is not None:
            therapist = (
                db.query(User)
                .filter(
                    User.id == assignment.therapist_id,
                    User.role == "therapist",
                )
                .first()
            )

        results.append(
            {
                "id": event.id,
                "patient_id": event.patient_id,
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
                "severity": event.severity,
                "status": event.status,
                "detected_at": event.detected_at,
                "therapist_id": (
                    therapist.id
                    if therapist is not None
                    else None
                ),
                "therapist_first_name": (
                    therapist.first_name
                    if therapist is not None
                    else None
                ),
                "therapist_last_name": (
                    therapist.last_name
                    if therapist is not None
                    else None
                ),
            }
        )

    return results


def get_admin_system_metadata(
    db: Session,
) -> dict:
    chunk_count = (
        db.execute(
            text(
                """
                SELECT COUNT(*)
                FROM knowledge_chunks
                """
            )
        ).scalar()
        or 0
    )

    source_rows = db.execute(
        text(
            """
            SELECT DISTINCT source_document
            FROM knowledge_chunks
            WHERE source_document IS NOT NULL
            ORDER BY source_document
            """
        )
    ).fetchall()

    source_documents = [
        row[0]
        for row in source_rows
        if row[0]
    ]

    active_knowledge_items = (
        db.execute(
            text(
                """
                SELECT COUNT(*)
                FROM knowledge_items
                WHERE is_active = TRUE
                """
            )
        ).scalar()
        or 0
    )

    return {
        "knowledge_base": {
            "configured": chunk_count > 0,
            "source_document_count": len(source_documents),
            "chunk_count": chunk_count,
            "active_knowledge_items": active_knowledge_items,
            "source_documents": source_documents,
        },
        "system": {
            "authentication_enabled": True,
            "supported_roles": [
                "patient",
                "therapist",
                "admin",
            ],
            "assignment_enforcement_enabled": True,
            "safety_monitoring_enabled": True,
            "admin_transcript_access": "restricted",
            "jwt_algorithm": settings.jwt_algorithm,
            "access_token_expire_minutes": (
                settings.access_token_expire
            ),
            "ai_model": (
                settings.openapi_model
                if settings.openapi_model
                else "Configured"
            ),
        },
    }


def assign_patient_to_therapist(
    db: Session,
    patient_id: int,
    therapist_id: int,
) -> dict | None:
    patient = (
        db.query(User)
        .filter(
            User.id == patient_id,
            User.role == "patient",
            User.is_active.is_(True),
        )
        .first()
    )

    if patient is None:
        return None

    therapist = (
        db.query(User)
        .filter(
            User.id == therapist_id,
            User.role == "therapist",
            User.is_active.is_(True),
        )
        .first()
    )

    if therapist is None:
        return None

    existing_assignments = (
        db.query(TherapistPatientAssignment)
        .filter(
            TherapistPatientAssignment.patient_id == patient_id,
        )
        .all()
    )

    for assignment in existing_assignments:
        db.delete(assignment)

    new_assignment = TherapistPatientAssignment(
        therapist_id=therapist_id,
        patient_id=patient_id,
    )

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    return {
        "assignment_id": new_assignment.id,
        "patient_id": patient.id,
        "patient_first_name": patient.first_name,
        "patient_last_name": patient.last_name,
        "therapist_id": therapist.id,
        "therapist_first_name": therapist.first_name,
        "therapist_last_name": therapist.last_name,
    }


def remove_patient_assignment(
    db: Session,
    patient_id: int,
) -> bool:
    outstanding_alert = (
        db.query(RedFlagEvent)
        .filter(
            RedFlagEvent.patient_id == patient_id,
            RedFlagEvent.severity == "high",
            RedFlagEvent.status == "unreviewed",
        )
        .first()
    )

    if outstanding_alert:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=409,
            detail=(
                "Cannot unassign patient: "
                "outstanding high-risk safety alerts "
                "must be reviewed first."
            ),
        )

    assignments = (
        db.query(TherapistPatientAssignment)
        .filter(
            TherapistPatientAssignment.patient_id == patient_id,
        )
        .all()
    )

    if not assignments:
        return False

    for assignment in assignments:
        db.delete(assignment)

    db.commit()

    return True