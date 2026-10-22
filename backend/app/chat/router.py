from fastapi import APIRouter, Depends, HTTPException, status
from openai import OpenAIError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user_id
from app.chat.llm import generate_reply
from app.chat.service import (
    create_chat_for_user,
    get_chat_for_user,
    get_conversation_history,
    save_chat_turn,
)
from app.database import get_db
from app.safety.action import CRISIS_RESPONSE, risk_response
from app.schemas import ChatCreate, ChatRead, MessageCreate, MessageTurnResponse

router = APIRouter(prefix="/chats", tags=["chat"])

# Request flow:
# 1. React sends a message.
# 2. Backend checks the JWT and identifies the user.
# 3. Backend checks the chat belongs to that user.
# 4. Backend checks for crisis language.
# 5. If crisis: return the safe crisis response.
# 6. If not crisis: call OpenAI with conversation history.
# 7. Save both messages in PostgreSQL.
# 8. Return the assistant reply to React.


@router.post("", response_model=ChatRead, status_code=status.HTTP_201_CREATED)
def create_chat(
    chat_data: ChatCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> ChatRead:
    return create_chat_for_user(db, user_id, chat_data.title)


@router.post("/{chat_id}/messages", response_model=MessageTurnResponse)
def send_message(
    chat_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> MessageTurnResponse:
    chat = get_chat_for_user(db, chat_id, user_id)
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    try:
        safety_result = risk_response(message_data.content)
        if safety_result["is_crisis"]:
            assistant_reply = CRISIS_RESPONSE
        else:
            history = get_conversation_history(db, chat_id)
            assistant_reply = generate_reply(history, message_data.content)
    except OpenAIError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="A required AI service is temporarily unavailable.",
        ) from exc

    save_chat_turn(db, chat_id, message_data.content, assistant_reply)
    return MessageTurnResponse(
        chat_id=chat_id,
        user_message=message_data.content,
        assistant_message=assistant_reply,
        risk_level=safety_result["risk_lvl"],
    )
