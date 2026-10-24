
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db_tables import Conversation, Message

MAX_HISTORY_MESSAGES = 20


def create_chat_for_user(db: Session, user_id: int) -> Conversation:
    """Create a conversation for the authenticated patient."""
    conversation = Conversation(patient_id=user_id)
    db.add(conversation)
    _commit_or_rollback(db)
    db.refresh(conversation)
    return conversation


def get_chat_for_user(
    db: Session,
    chat_id: int,
    user_id: int,
) -> Conversation | None:
    """Return a conversation only if it belongs to this patient."""
    return (
        db.query(Conversation)
        .filter(
            Conversation.id == chat_id,
            Conversation.patient_id == user_id,
        )
        .first()
    )


def get_conversation_history(
    db: Session,
    chat_id: int,
) -> list[dict[str, str]]:
    """Return recent messages in chronological order."""
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == chat_id)
        .order_by(Message.id.desc())
        .limit(MAX_HISTORY_MESSAGES)
        .all()
    )
    messages.reverse()

    return [
        {
            "role": (
                "user"
                if message.sender_type == "patient"
                else "assistant"
            ),
            "content": message.content,
        }
        for message in messages
    ]


def save_chat_turn(
    db: Session,
    chat_id: int,
    user_message: str,
    assistant_message: str,
) -> None:
    """Save both sides of a conversation turn."""
    db.add_all(
        [
            Message(
                conversation_id=chat_id,
                sender_type="patient",
                content=user_message,
            ),
            Message(
                conversation_id=chat_id,
                sender_type="assistant",
                content=assistant_message,
            ),
        ]
    )
    _commit_or_rollback(db)


def _commit_or_rollback(db: Session) -> None:
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
