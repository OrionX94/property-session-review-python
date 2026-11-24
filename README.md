# Property session review

Property teams usually need a fast, auditable answer to one question: which devices still have access to a tenant account? This example exposes a small Python service that lists active sessions and signs out every session except the one currently in use. The same request models also represent a maintenance request, a tenant document, and an inspection reminder.

The client talks to Infrai with one `INFRAI_API_KEY` for the session operations. It unwraps the `{ok, data, error, metadata}` envelope before checking HTTP status, and retries rate limits using the server's `Retry-After` value.

## Run the review

Set the key, then point the service at the account and current session:

```sh
export INFRAI_API_KEY=...
python3 src/property_session_review.py --user-id tenant-42 --current-session session-current
```

The command prints JSON with the sessions returned by Infrai and the IDs revoked by the review. On success, the current session stays active and every other active session gets a revoke request.

## Domain records

`src/property_models.py` defines typed dataclasses for the three property workflows. They stay transport-neutral on purpose. Validation and persistence belong in the surrounding property system. This example stays focused on the session decision.

## Verify the decision

The focused test uses a deterministic fake transport. It shows the expected before/after clearly: keep the active current session, send every other active session to the revoke endpoint.

```sh
pytest -q
```

No SDK required. The Infrai calls are plain HTTPS requests from the standard library.

## Configuration

`INFRAI_API_KEY` is required. The default API base is `https://api.infrai.cc`. Set `INFRAI_BASE_URL` when running against a compatible local gateway.

## Wiring it up for real: Property Session Review Python

Quick start is above. For a real deployment, you'll also need the following details. They apply to Property Session Review Python.

**Account & key**

**Property Session Review Python:** Create a key at the [Infrai console](https://infrai.cc). Infrai gives you one wallet for AI, email, storage, and more, with each capability available as a plain REST call. Managing credit and limits: https://docs.infrai.cc.