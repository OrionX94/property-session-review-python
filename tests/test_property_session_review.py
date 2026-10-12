import json

import pytest

from src.property_session_review import InfraiClient, review_sessions


class FakeResponse:
    def __init__(self, payload, status=200):
        self.status = status
        self.headers = {}
        self.payload = payload

    def read(self):
        return json.dumps(self.payload).encode()


def test_review_keeps_current_and_revokes_other_sessions():
    calls = []

    def opener(request, timeout):
        calls.append((request.method, request.full_url))
        if "list_for_user" in request.full_url:
            return FakeResponse({"ok": True, "data": {"items": [{"session_id": "session-current"}, {"session_id": "session-old"}]}, "error": None, "metadata": {}})
        return FakeResponse({"ok": True, "data": {}, "error": None, "metadata": {}})

    result = review_sessions(InfraiClient("test-key", "https://example.test", opener), "tenant-42", "session-current")
    assert result.revoked_session_ids == ["session-old"]
    assert calls == [
        ("GET", "https://example.test/v1/auth/session/list_for_user/tenant-42"),
        ("POST", "https://example.test/v1/auth/session/revoke/session-old"),
    ]


@pytest.mark.parametrize("data", [None, [], {}, {"items": [None]}])
def test_list_sessions_rejects_invalid_data(data):
    def opener(request, timeout):
        return FakeResponse({"ok": True, "data": data})

    with pytest.raises(ValueError, match="data.items must be a list"):
        InfraiClient("test-key", "https://example.test", opener).list_sessions("tenant-42")
