import json
from datetime import datetime
from pathlib import Path

from app.auth.security import hash_password
from app.database import SessionLocal
from app.db_tables import (
    Conversation,
    Message,
    TherapistPatientAssignment,
    User,
)


DEMO_PASSWORD = "DemoPassword123!"

DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "content-data-document"
    / "Paul_M2_Synthetic_Demo_Data.json"
)


def parse_timestamp(value: str) -> datetime:
    """Convert an ISO timestamp ending in Z into a Python datetime."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def split_name(name: str) -> tuple[str, str]:
    """Convert the synthetic display name into first and last name fields."""
    cleaned_name = name.removeprefix("Dr. ").strip()
    parts = cleaned_name.split()

    if len(parts) == 1:
        return parts[0], "User"

    return parts[0], " ".join(parts[1:])


def get_or_create_user(
    db,
    email: str,
    name: str,
    role: str,
) -> User:
    """Create a demo user unless the email already exists."""

    existing_user = (
        db.query(User)
        .filter(User.email == email.lower())
        .first()
    )

    if existing_user:
        return existing_user

    first_name, last_name = split_name(name)

    user = User(
        email=email.lower(),
        password_hash=hash_password(DEMO_PASSWORD),
        role=role,
        first_name=first_name,
        last_name=last_name,
        is_active=True,
    )

    db.add(user)
    db.flush()

    return user


def conversation_exists(
    db,
    patient_id: int,
    timestamp: datetime,
) -> bool:
    """Prevent duplicate synthetic conversations when the seed is rerun."""

    return (
        db.query(Conversation)
        .filter(
            Conversation.patient_id == patient_id,
            Conversation.started_at == timestamp,
        )
        .first()
        is not None
    )


def main():
    with DATA_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    db = SessionLocal()

    try:
        therapist_map = {}
        patient_map = {}

        for therapist_data in data["therapists"]:
            therapist = get_or_create_user(
                db,
                therapist_data["email"],
                therapist_data["name"],
                "therapist",
            )

            therapist_map[therapist_data["id"]] = therapist

        for patient_data in data["patients"]:
            patient = get_or_create_user(
                db,
                patient_data["email"],
                patient_data["name"],
                "patient",
            )

            patient_map[patient_data["id"]] = patient

        for admin_data in data["admins"]:
            get_or_create_user(
                db,
                admin_data["email"],
                admin_data["name"],
                "admin",
            )

        db.flush()

        for patient_data in data["patients"]:
            patient = patient_map[patient_data["id"]]

            therapist = therapist_map[
                patient_data["assignedTherapist"]
            ]

            existing_assignment = (
                db.query(TherapistPatientAssignment)
                .filter(
                    TherapistPatientAssignment.therapist_id
                    == therapist.id,
                    TherapistPatientAssignment.patient_id
                    == patient.id,
                )
                .first()
            )

            if existing_assignment is None:
                db.add(
                    TherapistPatientAssignment(
                        therapist_id=therapist.id,
                        patient_id=patient.id,
                    )
                )

            for conversation_data in patient_data["conversations"]:
                timestamp = parse_timestamp(
                    conversation_data["timestamp"]
                )

                if conversation_exists(
                    db,
                    patient.id,
                    timestamp,
                ):
                    continue

                conversation = Conversation(
                    patient_id=patient.id,
                    started_at=timestamp,
                    created_at=timestamp,
                )

                db.add(conversation)
                db.flush()

                db.add(
                    Message(
                        conversation_id=conversation.id,
                        sender_type="patient",
                        content=conversation_data["text"],
                        created_at=timestamp,
                    )
                )

        db.commit()

        print("Synthetic demo data seeded successfully.")
        print()
        print("Demo accounts use this password:")
        print(DEMO_PASSWORD)
        print()
        print("Therapists:")

        for therapist_data in data["therapists"]:
            therapist = therapist_map[therapist_data["id"]]
            print(
                therapist.id,
                therapist.email,
                therapist.role,
            )

        print()
        print("Patients:")

        for patient_data in data["patients"]:
            patient = patient_map[patient_data["id"]]
            print(
                patient.id,
                patient.email,
                patient.role,
            )

        print()
        print("Admin:")

        admin_email = data["admins"][0]["email"].lower()

        admin = (
            db.query(User)
            .filter(User.email == admin_email)
            .first()
        )

        print(
            admin.id,
            admin.email,
            admin.role,
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()