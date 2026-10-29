from fastapi import APIRouter, Depends, HTTPException, status
from openai import OpenAIError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.chat.llm import generate_reply
from app.chat.service import (
    create_chat_for_user,
    get_chat_for_user,
    get_conversation_history,
    get_conversation_messages_for_user,
    get_user_conversations,
    save_chat_turn,
)
from app.database import get_db
from app.db_tables import User
from app.knowledge_base import get_relevant_knowledge
from app.safety.action import risk_response
from app.schemas import MessageCreate


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.get("")
def list_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return conversation history for the authenticated patient.
    """

    try:
        conversations = get_user_conversations(
            db,
            current_user.id,
        )
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Conversation history could not be loaded.",
        ) from exc

    return {
        "conversations": conversations,
    }


@router.get("/{chat_id}")
def get_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return one conversation and its messages
    only if it belongs to the authenticated patient.
    """

    try:
        conversation = get_conversation_messages_for_user(
            db,
            chat_id,
            current_user.id,
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


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
def create_chat(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = create_chat_for_user(
        db,
        current_user.id,
    )

    return {
        "id": conversation.id,
        "patient_id": conversation.patient_id,
        "created_at": conversation.created_at,
    }


@router.post("/{chat_id}/messages")
def send_message(
    chat_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content = message_data.content.strip()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message content must not be empty.",
        )

    conversation = get_chat_for_user(
        db,
        chat_id,
        current_user.id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    try:
        safety_result = risk_response(content)

        if safety_result["is_crisis"]:
            assistant_reply = safety_result["response"]
        else:
            history = get_conversation_history(
                db,
                chat_id,
            )
            knowledge_context = get_relevant_knowledge(content)

            assistant_reply = generate_reply(
                history,
                content,
                knowledge_context,
            )

            if knowledge_context:
                print("USING KNOWLEDGE BASE")
            else:
                print("NO KNOWLEDGE BASE USED")

            assistant_reply = generate_reply(
                history,
                content,
            )

        save_chat_turn(
            db,
            chat_id,
            content,
            assistant_reply,
        )

    except OpenAIError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "The AI safety or response service is temporarily "
                "unavailable. Please try again."
            ),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "The safety service is temporarily unavailable. "
                "Please try again."
            ),
        ) from exc

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The conversation could not be saved.",
        ) from exc

    return {
        "chat_id": conversation.id,
        "user_message": content,
        "assistant_message": assistant_reply,
        "risk_level": safety_result["risk_lvl"],
    }