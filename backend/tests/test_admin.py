from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app.admin.service import remove_patient_assignment


def test_unassignment_blocked_by_unreviewed_high_alert():
    db = Mock()

    alert_query = Mock()
    alert_query.filter.return_value = alert_query
    alert_query.first.return_value = SimpleNamespace(id=1)

    db.query.return_value = alert_query

    with pytest.raises(HTTPException) as exc:
        remove_patient_assignment(db, patient_id=10)

    assert exc.value.status_code == 409
    assert "high-risk safety alerts" in exc.value.detail
    db.delete.assert_not_called()
    db.commit.assert_not_called()


def test_unassignment_allowed_when_no_unreviewed_high_alerts():
    db = Mock()
    assignment = SimpleNamespace(id=1)

    alert_query = Mock()
    alert_query.filter.return_value = alert_query
    alert_query.first.return_value = None

    assignment_query = Mock()
    assignment_query.filter.return_value = assignment_query
    assignment_query.all.return_value = [assignment]

    db.query.side_effect = [alert_query, assignment_query]

    result = remove_patient_assignment(db, patient_id=10)

    assert result is True
    db.delete.assert_called_once_with(assignment)
    db.commit.assert_called_once()
