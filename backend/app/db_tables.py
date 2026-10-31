# postgre tables go here

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ENUM as PGEnum

from app.database import Base


# Reuse the PostgreSQL enums that already exist in Supabase.
# create_type=False prevents SQLAlchemy from trying to create them.
user_role_enum = PGEnum(
    "patient",
    "therapist",
    "admin",
    name="user_role",
    create_type=False,
)

sender_type_enum = PGEnum(
    "patient",
    "assistant",
    name="sender_type",
    create_type=False,
)


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(user_role_enum, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class TherapistPatientAssignment(Base):
    __tablename__ = "therapist_patient_assignments"

    __table_args__ = (
        UniqueConstraint(
            "therapist_id",
            "patient_id",
            name="unique_therapist_patient",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    therapist_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    patient_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    patient_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    started_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id = Column(
        BigInteger,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    sender_type = Column(sender_type_enum, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class ConsentAcknowledgement(Base):
    __tablename__ = "consent_acknowledgements"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    disclosure_version = Column(String, nullable=False)
    acknowledged_at = Column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class RedFlagDefinition(Base):
    __tablename__ = "red_flag_definitions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    detection_pattern = Column(Text, nullable=False)
    severity = Column(String(50), nullable=False)
    is_active = Column(
        Boolean,
        nullable=False,
        server_default="true",
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class RedFlagEvent(Base):
    __tablename__ = "red_flag_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    message_id = Column(
        BigInteger,
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
    )

    red_flag_definition_id = Column(
        BigInteger,
        ForeignKey(
            "red_flag_definitions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    patient_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    conversation_id = Column(
        BigInteger,
        ForeignKey(
            "conversations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    severity = Column(String(50), nullable=False)

    detected_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    status = Column(String(50), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    recipient_user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    red_flag_event_id = Column(
        BigInteger,
        ForeignKey(
            "red_flag_events.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )

    type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)

    is_read = Column(
        Boolean,
        nullable=False,
        server_default="false",
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )