
from unittest.mock import Mock, patch

import pytest

from app.safety import rules


def test_contains_crisis_detects_direct_phrase():
    assert rules.contains_crisis("I want to kill myself") is True


def test_contains_crisis_returns_false_for_unrelated_text():
    assert rules.contains_crisis("I had a difficult day at work") is False


@patch("app.safety.rules.client.moderations.create")
def test_moderation_returns_high_for_self_harm(mock_create):
    mock_create.return_value = Mock(
        results=[
            Mock(
                categories=Mock(
                    self_harm=True,
                    self_harm_intent=False,
                    self_harm_instructions=False,
                    violence=False,
                    illicit_violent=False,
                    harassment=False,
                )
            )
        ]
    )

    assert rules.usr_message_check("test message") == "high"


@patch("app.safety.rules.client.moderations.create")
def test_moderation_failure_raises_runtime_error(mock_create):
    mock_create.side_effect = Exception("simulated service failure")

    with pytest.raises(RuntimeError, match="moderation service is unavailable"):
        rules.usr_message_check("test message")
