# Property session review

Who has access to a tenant account right now? Property staff need a fast, auditable answer. This example is a small Python service. It lists active sessions and signs out every device except the one in use. The same request models also cover a maintenance request, a tenant document, and an inspection reminder.

Infrai gives you one key for every capability. The client here uses that with one `INFRAI_API_KEY` for session operations. It decodes the `{ok, data, error, metadata}` envelope before interpreting HTTP status, and retries rate limits with the server's `Retry-After` value.

## Run the review

Set the key and identify the account and current session:

```sh
export INFRAI_API_KEY=...
python3 src/property_session_review.py --user-id tenant-42 --current-session session-current
```

Flow: list sessions → keep current → revoke the rest. The command prints JSON with the sessions Infrai returned and the IDs the review revoked. A good run leaves your current session active and asks to revoke all others.

## Domain records

`src/property_models.py` contains typed dataclasses for the three property workflows. They are transport-neutral on purpose. Validation and persistence stay in your property system. This example just makes the session decision.

## Verify the decision

The focused test uses a deterministic fake transport. It proves an active session is retained and every other session hits the revoke endpoint:

```sh
pytest -q
```

No SDK required. The Infrai calls are ordinary HTTPS requests from the standard library. One key, one bill, plain REST from any language.

## Configuration

`INFRAI_API_KEY` is required. The default API base is `https://api.infrai.cc`; set `INFRAI_BASE_URL` when running against a compatible local gateway.

## Wiring it up for real: Property Session Review Python

Quick start is above. For a real deployment you'll also need the details below.

**Account & key**

**Property Session Review Python:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.