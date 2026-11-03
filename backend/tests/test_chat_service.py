
from unittest.mock import Mock, patch

from app.chat.service import (
    create_chat_for_user,
    get_chat_for_user,
    save_chat_turn,
)



def test_create_chat_for_user_commits_and_refreshes():
    db = Mock()
    conversation = Mock()

    with patch(
        "app.chat.service.Conversation",
        return_value=conversation,
    ) as mock_conversation:
        result = create_chat_for_user(db, user_id=123)

    assert result is conversation
    mock_conversation.assert_called_once_with(patient_id=123)
    db.add.assert_called_once_with(conversation)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(conversation)



def test_get_chat_for_user_returns_matching_conversation():
    db = Mock()
    expected_conversation = Mock()

    db.query.return_value.filter.return_value.first.return_value = (
        expected_conversation
    )

    result = get_chat_for_user(db, chat_id=456, user_id=123)

    assert result is expected_conversation
    db.query.assert_called_once()


def test_save_chat_turn_commits_both_messages():
    db = Mock()

    save_chat_turn(
        db,
        chat_id=456,
        user_message="Test message",
        assistant_message="Test reply",
    )

    db.add_all.assert_called_once()
    messages = db.add_all.call_args.args[0]

    assert len(messages) == 2
    assert messages[0].sender_type == "patient"
    assert messages[0].content == "Test message"
    assert messages[1].sender_type == "assistant"
    assert messages[1].content == "Test reply"
    db.commit.assert_called_once()
