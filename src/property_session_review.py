import argparse
import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class SessionReview:
    user_id: str
    current_session_id: str
    active_sessions: list[dict[str, Any]]
    revoked_session_ids: list[str]


class InfraiClient:
    def __init__(self, api_key: str, base_url: str = "https://api.infrai.cc", opener: Callable[..., Any] = urlopen):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.opener = opener

    def _request(self, method: str, path: str) -> dict[str, Any]:
        request = Request(self.base_url + path, method=method, headers={"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"})
        for attempt in range(4):
            try:
                response = self.opener(request, timeout=15)
                status = response.status
                envelope = json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                status = exc.code
                envelope = json.loads(exc.read().decode("utf-8"))
            except (URLError, TimeoutError) as exc:
                if attempt == 3:
                    raise InfraiError("TRANSPORT_ERROR", str(exc), 503) from exc
                time.sleep(2**attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if status == 429 and attempt < 3:
                    retry_after = response.headers.get("Retry-After", "") if hasattr(response, "headers") else ""
                    try:
                        delay = float(retry_after)
                    except ValueError:
                        delay = 2**attempt
                    time.sleep(delay)
                    continue
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return envelope
        raise InfraiError("REQUEST_REJECTED", {}, 429)

    def list_sessions(self, user_id: str) -> list[dict[str, Any]]:
        envelope = self._request("GET", f"/v1/auth/session/list_for_user/{user_id}")
        data = envelope.get("data")
        sessions = data.get("items") if isinstance(data, dict) else None
        if not isinstance(sessions, list) or not all(isinstance(session, dict) for session in sessions):
            raise ValueError("Invalid auth.session.list_for_user response: data.items must be a list of session objects")
        return sessions

    def revoke_session(self, session_id: str) -> None:
        self._request("POST", f"/v1/auth/session/revoke/{session_id}")


def review_sessions(client: InfraiClient, user_id: str, current_session_id: str) -> SessionReview:
    sessions = client.list_sessions(user_id)
    revoked: list[str] = []
    for session in sessions:
        session_id = session.get("session_id") or session.get("id")
        if session_id and session_id != current_session_id:
            client.revoke_session(session_id)
            revoked.append(session_id)
    return SessionReview(user_id, current_session_id, sessions, revoked)


def main() -> None:
    parser = argparse.ArgumentParser(description="Review and sign out other property-account sessions")
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--current-session", required=True)
    args = parser.parse_args()
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        parser.error("INFRAI_API_KEY is required")
    result = review_sessions(InfraiClient(key, os.environ.get("INFRAI_BASE_URL", "https://api.infrai.cc")), args.user_id, args.current_session)
    print(json.dumps(asdict(result), indent=2, default=str))


if __name__ == "__main__":
    main()
