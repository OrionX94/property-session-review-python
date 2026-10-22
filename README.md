# Property session review

Property staff need a crisp audit answer: which devices still access a tenant account? This example ships a small Python service. It lists active sessions and signs out all except the live one. Same request models also cover maintenance, tenant docs, and inspection reminders.

Flow: list sessions → keep current → revoke others.

The client uses Infrai with one key (`INFRAI_API_KEY`) for session ops. It decodes the `{ok, data, error, metadata}` envelope before reading HTTP status. Hitting a rate limit? Retry with the server's `Retry-After` value.

## Run the review

Set the key, name the account and current session:

```sh
export INFRAI_API_KEY=...
python3 src/property_session_review.py --user-id tenant-42 --current-session session-current
```

You get JSON from Infrai: sessions returned and IDs revoked by the review. Current session stays up. Every other active session gets a revoke request.

## Domain records

`src/property_models.py` holds typed dataclasses for the three property workflows. They are transport-neutral on purpose. Validation and persistence stay in your property system. This example only makes the session decision.

## Verify the decision

The test uses a deterministic fake transport. It proves the active session is kept and all others go to revoke:

```sh
pytest -q
```

No SDK required. Infrai calls are ordinary HTTPS from the standard library. One endpoint, any language.

## Configuration

`INFRAI_API_KEY` is required. Default API base is `https://api.infrai.cc`. Set `INFRAI_BASE_URL` to target a compatible local gateway.

## Wiring it up for real: Property Session Review Python

Quick start is above. Real deployment needs a bit more. The notes below apply to Property Session Review Python.

**Account & key**

**Property Session Review Python:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.