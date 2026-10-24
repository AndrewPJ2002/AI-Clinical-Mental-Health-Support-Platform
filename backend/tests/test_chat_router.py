
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from app.chat import router as chat_router


def test_send_message_returns_503_when_moderation_fails():
    fake_user = Mock()
    fake_user.id = 123

    fake_conversation = Mock()
    fake_conversation.id = 456
    fake_conversation.patient_id = 123

    fake_db = Mock()
    fake_message = Mock()
    fake_message.content = "A harmless test message"

    with (
        patch.object(
            chat_router,
            "get_chat_for_user",
            return_value=fake_conversation,
        ),
        patch.object(
            chat_router,
            "risk_response",
            side_effect=RuntimeError("The moderation service is unavailable."),
        ),
    ):
        with pytest.raises(HTTPException) as exc_info:
            chat_router.send_message(
                chat_id=456,
                message_data=fake_message,
                db=fake_db,
                current_user=fake_user,
            )

    assert exc_info.value.status_code == 503
    assert "safety service" in exc_info.value.detail.lower()
