from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db_tables import Chat, ChatMessage

MAX_HISTORY_MESSAGES = 20


def create_chat_for_user(db: Session, user_id: int, title: str) -> Chat:
    chat = Chat(owner_id=user_id, title=title)
    db.add(chat)
    _commit_or_rollback(db)
    db.refresh(chat)
    return chat


def get_chat_for_user(db: Session, chat_id: int, user_id: int) -> Chat | None:
    return (
        db.query(Chat)
        .filter(Chat.id == chat_id, Chat.owner_id == user_id)
        .first()
    )


def get_conversation_history(
    db: Session,
    chat_id: int,
) -> list[dict[str, str]]:
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.id.desc())
        .limit(MAX_HISTORY_MESSAGES)
        .all()
    )
    messages.reverse()
    return [{"role": message.role, "content": message.content} for message in messages]


def save_chat_turn(
    db: Session,
    chat_id: int,
    user_message: str,
    assistant_message: str,
) -> None:
    db.add_all(
        [
            ChatMessage(chat_id=chat_id, role="user", content=user_message),
            ChatMessage(chat_id=chat_id, role="assistant", content=assistant_message),
        ]
    )
    _commit_or_rollback(db)


def _commit_or_rollback(db: Session) -> None:
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
