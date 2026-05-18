# voicetel-api

Official Python SDK for the [VoiceTel REST API](https://api.voicetel.com).

Targets API version **v2.2.6**. Supports Python 3.10+.

## Install

```bash
pip install voicetel-api
```

## Quickstart

```python
from voicetel import Client

with Client() as c:
    # Exchange username + password for an API key (rate-limited: 6/hour/IP).
    c.login(username=1234567890, password="...")

    account = c.account.get()
    print(account)

    for n in c.numbers.list():
        print(n["number"])
```

Or, if you already have an API key:

```python
from voicetel import Client

with Client(api_key="32-hex-string") as c:
    ...
```

### Async

```python
import asyncio
from voicetel import AsyncClient

async def main():
    async with AsyncClient(api_key="...") as c:
        print(await c.account.get())

asyncio.run(main())
```

## Authentication

Every endpoint requires `Authorization: Bearer <apikey>` **except** `POST /v2.2/account/api-key`,
which exchanges username + password for a fresh key. `Client.login()` and `AsyncClient.login()`
handle this exchange and install the returned key on the transport.

Re-fetch the API key after any password change — the old one is invalidated.

## Rate limits

These endpoints are limited to **6 requests per hour per IP**:

- `account/info`
- `account/mrc` (`account.recurring_charges()`)
- `account/cdr` (`account.cdr()`)
- `account/api-key` (`client.login()`)

429 responses are retried with `Retry-After` honored, up to `max_retries` (default `2`).

## Errors

All HTTP errors raise subclasses of `voicetel.ApiError`:

| Status | Exception              |
|--------|------------------------|
| 400    | `BadRequestError`      |
| 401    | `AuthenticationError`  |
| 403    | `PermissionDeniedError`|
| 404    | `NotFoundError`        |
| 409    | `ConflictError`        |
| 429    | `RateLimitError`       |
| 5xx    | `ServerError`          |
| other  | `ApiError`             |

```python
from voicetel import Client, RateLimitError

try:
    c.account.cdr(start=0, end=0)
except RateLimitError as e:
    print(f"slow down: {e}")
```

## Resource groups

| Attribute            | Tag (OpenAPI) | Purpose                                       |
|----------------------|---------------|-----------------------------------------------|
| `client.account`     | Account       | Profile, CDRs, credits, payments, MRC, signup |
| `client.acl`         | ACL           | IP allowlist (CIDR entries)                   |
| `client.authentication` | Authentication | SIP/HTTP auth type and password            |
| `client.e911`        | e911          | e911 records, address validation              |
| `client.gateways`    | Gateways      | Outbound termination gateways                 |
| `client.inumbering`  | iNumbering    | Inventory, orders, port-ins                   |
| `client.lookups`     | Lookups       | CNAM and LRN dips                             |
| `client.messaging`   | Messaging     | SMS/MMS, 10DLC brands & campaigns             |
| `client.numbers`     | Numbers       | All operations on TNs owned by the account    |
| `client.support`     | Support       | Support tickets                               |

## Development

```bash
git clone https://github.com/voicetel/python-sdk
cd python-sdk
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Unit tests (fast, no network)
pytest tests/unit

# Integration tests (hits api.voicetel.com, read-only)
cp .env.example .env  # fill in VOICETEL_USERNAME / VOICETEL_PASSWORD
pytest -m integration

# Coverage
pytest --cov --cov-report=term-missing
```

## License

Apache 2.0
