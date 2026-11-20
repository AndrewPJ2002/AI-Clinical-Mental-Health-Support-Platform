from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.chat import router as chat_router
from app.db_tables import (
    Notification,
    RedFlagDefinition,
    RedFlagEvent,
    TherapistPatientAssignment,
)
from app.safety import action, rules, service
from app.schemas import MessageCreate
from app.therapist import router as therapist_router
from app.therapist import service as therapist_service


def _categories(**overrides):
    values = {name: False for name in rules.MODERATION_CATEGORIES}
    values.update(overrides)
    return SimpleNamespace(**values)


def _mock_moderation(monkeypatch, categories, results=True):
    response = SimpleNamespace(
        results=[SimpleNamespace(categories=categories)] if results else []
    )
    create = Mock(return_value=response)
    monkeypatch.setattr(rules.client.moderations, "create", create)
    return create

def test_detection_crisis_phrase_is_case_insensitive_and_skips_moderation(monkeypatch):
    create = _mock_moderation(monkeypatch, _categories())

    assert rules.contains_crisis("I WANT TO KILL MYSELF") is True
    result = action.risk_response("I WANT TO KILL MYSELF")

    assert result["risk_lvl"] == "high"
    assert result["is_crisis"] is True
    assert result["matched_categories"] == []
    assert result["response"] == action.CRISIS_RESPONSE
    create.assert_not_called()

def test_detection_non_crisis_message_with_no_matches_is_low(monkeypatch):
    _mock_moderation(monkeypatch, _categories())

    result = action.risk_response("I had a difficult day at work")

    assert result["risk_lvl"] == "low"
    assert result["is_crisis"] is False
    assert result["response"] is None
    assert result["matched_categories"] == []

def test_detection_enabled_categories_return_highest_configured_severity(monkeypatch):
    _mock_moderation(
        monkeypatch,
        _categories(violence=True, self_harm=True, hate=True),
    )
    db = Mock()
    db.query.return_value.all.return_value = [
        SimpleNamespace(category="violence", severity="low", is_enabled=True),
        SimpleNamespace(category="self_harm", severity="high", is_enabled=True),
        SimpleNamespace(category="hate", severity="high", is_enabled=False),
    ]
    monkeypatch.setattr(
        rules,
        "get_ai_runtime_settings",
        lambda _db: {"api_key": "test-key"},
    )
    monkeypatch.setattr(rules, "OpenAI", lambda **_kwargs: rules.client)

    result = rules.moderation_check("test", db)

    assert result == {"severity": "high", "categories": ["self_harm", "violence"]}

def test_detection_disabled_and_unknown_categories_do_not_match(monkeypatch):
    _mock_moderation(monkeypatch, _categories(harassment=True))
    db = Mock()
    db.query.return_value.all.return_value = [
        SimpleNamespace(category="harassment", severity="high", is_enabled=False),
        SimpleNamespace(category="not_a_supported_category", severity="high", is_enabled=True),
    ]
    monkeypatch.setattr(
        rules,
        "get_ai_runtime_settings",
        lambda _db: {"api_key": "test-key"},
    )
    monkeypatch.setattr(rules, "OpenAI", lambda **_kwargs: rules.client)

    assert rules.moderation_check("test", db) == {"severity": None, "categories": []}

def test_detection_moderation_response_without_results_fails_closed(monkeypatch):
    _mock_moderation(monkeypatch, _categories(), results=False)

    with pytest.raises(RuntimeError, match="returned no results"):
        rules.moderation_check("test")

def test_detection_moderation_service_failure_fails_closed(monkeypatch):
    create = Mock(side_effect=RuntimeError("network issue"))
    monkeypatch.setattr(rules.client.moderations, "create", create)

    with pytest.raises(RuntimeError, match="moderation service is unavailable"):
        rules.moderation_check("test")

def test_detection_risk_response_preserves_medium_category_and_avoids_crisis_reply(monkeypatch):
    monkeypatch.setattr(
        action,
        "moderation_check",
        lambda _text, _db: {"severity": "medium", "categories": ["violence"]},
    )

    result = action.risk_response("test")

    assert result["risk_lvl"] == "medium"
    assert result["is_crisis"] is False
    assert result["response"] is None
    assert result["matched_categories"] == ["violence"]

def test_alerts_low_severity_is_not_persisted_or_notified():
    db = Mock()

    assert service.record_red_flag_and_notify(
        db, patient_id=1, conversation_id=2, message_id=3, severity="low"
    ) is None
    db.query.assert_not_called()
    db.add.assert_not_called()
    db.commit.assert_not_called()

def test_alerts_high_flag_creates_event_and_notifies_each_assigned_therapist():
    db = Mock()
    definition_query = Mock()
    definition_query.filter.return_value.first.return_value = None
    assignment_query = Mock()
    assignment_query.filter.return_value.all.return_value = [
        SimpleNamespace(therapist_id=41),
        SimpleNamespace(therapist_id=42),
    ]
    db.query.side_effect = [definition_query, assignment_query]
    next_id = iter([501, 601])
    db.refresh.side_effect = lambda obj: setattr(obj, "id", next(next_id))

    event = service.record_red_flag_and_notify(
        db,
        patient_id=10,
        conversation_id=20,
        message_id=30,
        severity="high",
        matched_categories=["self_harm_intent"],
    )

    assert event.severity == "high"
    assert event.red_flag_definition_id == 501
    assert event.status == "unreviewed"
    assert db.commit.call_count == 3
    added = [call.args[0] for call in db.add.call_args_list]
    definition = next(obj for obj in added if isinstance(obj, RedFlagDefinition))
    event_added = next(obj for obj in added if isinstance(obj, RedFlagEvent))
    notifications = [obj for obj in added if isinstance(obj, Notification)]
    assert definition.detection_pattern == "openai_moderation:self_harm_intent"
    assert event_added.message_id == 30
    assert [n.recipient_user_id for n in notifications] == [41, 42]
    assert all(n.red_flag_event_id == 601 and not n.is_read for n in notifications)
    assert all("self_harm_intent" in n.message for n in notifications)

def test_alerts_medium_flag_without_assigned_therapists_still_records_event():
    db = Mock()
    definition = SimpleNamespace(id=7)
    definition_query = Mock()
    definition_query.filter.return_value.first.return_value = definition
    assignment_query = Mock()
    assignment_query.filter.return_value.all.return_value = []
    db.query.side_effect = [definition_query, assignment_query]
    db.refresh.side_effect = lambda obj: setattr(obj, "id", 8)

    event = service.record_red_flag_and_notify(
        db, patient_id=1, conversation_id=2, message_id=3,
        severity="medium", matched_categories=["violence"],
    )

    assert event.red_flag_definition_id == 7
    assert db.add.call_count == 1
    assert db.commit.call_count == 2

def test_alerts_event_persistence_failure_rolls_back_and_propagates():
    db = Mock()
    definition = SimpleNamespace(id=7)
    query = Mock()
    query.filter.return_value.first.return_value = definition
    db.query.return_value = query
    db.commit.side_effect = SQLAlchemyError("database unavailable")

    with pytest.raises(SQLAlchemyError):
        service.record_red_flag_and_notify(
            db, patient_id=1, conversation_id=2, message_id=3, severity="high"
        )

    db.rollback.assert_called_once()

def test_chat_crisis_chat_uses_crisis_reply_and_records_high_flag():
    user = SimpleNamespace(id=11)
    conversation = SimpleNamespace(id=22)
    saved_message = SimpleNamespace(id=33)
    db = Mock()
    safety = {
        "is_crisis": True,
        "risk_lvl": "high",
        "response": "crisis support response",
        "matched_categories": [],
    }
    with (
        patch.object(chat_router, "get_chat_for_user", return_value=conversation),
        patch.object(chat_router, "risk_response", return_value=safety) as risk,
        patch.object(chat_router, "save_chat_turn", return_value=saved_message) as save,
        patch.object(chat_router, "record_red_flag_and_notify") as record,
        patch.object(chat_router, "generate_reply") as generate,
    ):
        response = chat_router.send_message(
            22, MessageCreate(content="I want to die"), db, user
        )

    assert response["risk_level"] == "high"
    assert response["assistant_message"] == "crisis support response"
    risk.assert_called_once_with("I want to die", db)
    save.assert_called_once_with(db, 22, "I want to die", "crisis support response")
    generate.assert_not_called()
    record.assert_called_once_with(
        db, patient_id=11, conversation_id=22, message_id=33,
        severity="high", matched_categories=[],
    )

def test_chat_low_risk_chat_does_not_create_flag_or_notification():
    user = SimpleNamespace(id=11)
    conversation = SimpleNamespace(id=22)
    db = Mock()
    safety = {
        "is_crisis": False,
        "risk_lvl": "low",
        "response": None,
        "matched_categories": [],
    }
    with (
        patch.object(chat_router, "get_chat_for_user", return_value=conversation),
        patch.object(chat_router, "risk_response", return_value=safety),
        patch.object(chat_router, "get_conversation_history", return_value=[]),
        patch.object(chat_router, "retrieve_context", return_value=""),
        patch.object(chat_router, "generate_reply", return_value="supportive reply"),
        patch.object(chat_router, "save_chat_turn", return_value=SimpleNamespace(id=33)),
        patch.object(chat_router, "record_red_flag_and_notify") as record,
    ):
        response = chat_router.send_message(
            22, MessageCreate(content="A difficult day"), db, user
        )

    assert response["risk_level"] == "low"
    record.assert_not_called()

def test_chat_moderation_medium_chat_keeps_ai_reply_and_records_matching_category():
    user = SimpleNamespace(id=11)
    conversation = SimpleNamespace(id=22)
    saved_message = SimpleNamespace(id=33)
    db = Mock()
    safety = {
        "is_crisis": False,
        "risk_lvl": "medium",
        "response": None,
        "matched_categories": ["violence"],
    }
    with (
        patch.object(chat_router, "get_chat_for_user", return_value=conversation),
        patch.object(chat_router, "risk_response", return_value=safety),
        patch.object(chat_router, "get_conversation_history", return_value=[]),
        patch.object(chat_router, "retrieve_context", return_value="context"),
        patch.object(chat_router, "generate_reply", return_value="supportive reply"),
        patch.object(chat_router, "save_chat_turn", return_value=saved_message),
        patch.object(chat_router, "record_red_flag_and_notify") as record,
    ):
        response = chat_router.send_message(
            22, MessageCreate(content="I am angry"), db, user
        )

    assert response["risk_level"] == "medium"
    assert response["assistant_message"] == "supportive reply"
    record.assert_called_once_with(
        db,
        patient_id=11,
        conversation_id=22,
        message_id=33,
        severity="medium",
        matched_categories=["violence"],
    )

def test_review_therapist_review_marks_event_and_matching_notifications_read():
    event = SimpleNamespace(id=8, patient_id=10, status="unreviewed")
    notifications = [SimpleNamespace(is_read=False), SimpleNamespace(is_read=False)]
    event_query = Mock()
    event_query.filter.return_value.first.return_value = event
    assignment_query = Mock()
    assignment_query.filter.return_value.first.return_value = SimpleNamespace(id=1)
    notification_query = Mock()
    notification_query.filter.return_value.all.return_value = notifications
    db = Mock()
    db.query.side_effect = [event_query, assignment_query, notification_query]

    result = therapist_service.mark_red_flag_event_reviewed(db, 40, 8)

    assert result == {
        "red_flag_event_id": 8,
        "status": "reviewed",
        "notifications_updated": 2,
    }
    assert event.status == "reviewed"
    assert all(notification.is_read for notification in notifications)
    db.commit.assert_called_once()

def test_review_therapist_cannot_review_an_unassigned_patient_event():
    event = SimpleNamespace(id=8, patient_id=10, status="unreviewed")
    event_query = Mock()
    event_query.filter.return_value.first.return_value = event
    assignment_query = Mock()
    assignment_query.filter.return_value.first.return_value = None
    db = Mock()
    db.query.side_effect = [event_query, assignment_query]

    assert therapist_service.mark_red_flag_event_reviewed(db, 40, 8) is None
    assert event.status == "unreviewed"
    db.commit.assert_not_called()

def test_review_therapist_review_endpoint_returns_not_found_for_unassigned_event():
    therapist = SimpleNamespace(id=40, role="therapist")
    with patch.object(
        therapist_router,
        "mark_red_flag_event_reviewed",
        return_value=None,
    ):
        with pytest.raises(HTTPException) as exc:
            therapist_router.review_red_flag_event(8, Mock(), therapist)

    assert exc.value.status_code == 404

def test_review_notification_review_marks_only_recipient_notification_and_linked_event():
    notification = SimpleNamespace(
        id=9,
        recipient_user_id=40,
        red_flag_event_id=8,
        is_read=False,
    )
    event = SimpleNamespace(id=8, status="unreviewed")
    notification_query = Mock()
    notification_query.filter.return_value.first.return_value = notification
    event_query = Mock()
    event_query.filter.return_value.first.return_value = event
    db = Mock()
    db.query.side_effect = [notification_query, event_query]

    result = therapist_service.mark_notification_reviewed(db, 40, 9)

    assert result == {
        "notification_id": 9,
        "is_read": True,
        "red_flag_event_id": 8,
        "status": "reviewed",
    }
    assert notification.is_read is True
    assert event.status == "reviewed"
    db.commit.assert_called_once()

def test_review_review_endpoint_rejects_non_therapist_role():
    with pytest.raises(HTTPException) as exc:
        therapist_router.require_therapist(SimpleNamespace(role="patient"))

    assert exc.value.status_code == 403
