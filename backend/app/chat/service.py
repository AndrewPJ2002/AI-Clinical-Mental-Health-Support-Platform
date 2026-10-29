from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db_tables import Conversation, Message


MAX_HISTORY_MESSAGES = 20
HISTORY_TITLE_LENGTH = 45
HISTORY_PREVIEW_LENGTH = 110


def create_chat_for_user(
    db: Session,
    user_id: int,
) -> Conversation:
    """Create a conversation for the authenticated patient."""

    conversation = Conversation(
        patient_id=user_id,
    )

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
    """
    Return recent messages in chronological order.

    This is used to provide conversational context to the AI.
    """

    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == chat_id,
        )
        .order_by(
            Message.id.desc(),
        )
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


def get_user_conversations(
    db: Session,
    user_id: int,
) -> list[dict]:
    """
    Return all conversations belonging to the authenticated patient.

    The first patient message is used to create a short display title
    and preview for the History drawer.
    """

    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.patient_id == user_id,
        )
        .order_by(
            Conversation.started_at.desc(),
            Conversation.id.desc(),
        )
        .all()
    )

    history_items = []

    for conversation in conversations:
        first_patient_message = (
            db.query(Message)
            .filter(
                Message.conversation_id == conversation.id,
                Message.sender_type == "patient",
            )
            .order_by(
                Message.created_at.asc(),
                Message.id.asc(),
            )
            .first()
        )

        if first_patient_message:
            full_text = first_patient_message.content.strip()

            title = _truncate_text(
                full_text,
                HISTORY_TITLE_LENGTH,
            )

            preview = _truncate_text(
                full_text,
                HISTORY_PREVIEW_LENGTH,
            )
        else:
            title = "New conversation"
            preview = "No messages yet."

        history_items.append(
            {
                "id": conversation.id,
                "started_at": conversation.started_at,
                "ended_at": conversation.ended_at,
                "title": title,
                "preview": preview,
            }
        )

    return history_items


def get_conversation_messages_for_user(
    db: Session,
    chat_id: int,
    user_id: int,
) -> dict | None:
    """
    Return one conversation and all of its messages,
    but only when it belongs to the authenticated patient.
    """

    conversation = get_chat_for_user(
        db,
        chat_id,
        user_id,
    )

    if conversation is None:
        return None

    messages = (
        db.query(Message)
        .filter(
            Message.conversation_id == chat_id,
        )
        .order_by(
            Message.created_at.asc(),
            Message.id.asc(),
        )
        .all()
    )

    return {
        "id": conversation.id,
        "started_at": conversation.started_at,
        "ended_at": conversation.ended_at,
        "messages": [
            {
                "id": message.id,
                "sender": (
                    "user"
                    if message.sender_type == "patient"
                    else "ai"
                ),
                "content": message.content,
                "created_at": message.created_at,
            }
            for message in messages
        ],
    }


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


def _truncate_text(
    text: str,
    max_length: int,
) -> str:
    """Shorten text for display without generating a summary."""

    if len(text) <= max_length:
        return text

    return text[: max_length - 3].rstrip() + "..."


def _commit_or_rollback(
    db: Session,
) -> None:
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise