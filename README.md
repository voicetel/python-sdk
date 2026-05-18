# 📞 VoiceTel Python SDK

The official Python client for the [VoiceTel REST API](https://voicetel.com/docs/api/v2.2/) — provision numbers, place orders, validate e911, send messages, and manage your account, all with type-safe, async-ready Python.

![Version](https://img.shields.io/badge/version-2.2.8-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![Typed](https://img.shields.io/badge/typed-pydantic--v2-blue)

## 📚 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quickstart](#-quickstart)
- [Authentication](#-authentication)
- [Resource Reference](#-resource-reference)
- [Error Handling](#-error-handling)
- [Async Support](#-async-support)
- [Rate Limits](#-rate-limits)
- [Development](#-development)
- [API Documentation](#-api-documentation)
- [Contributors](#-contributors)
- [Sponsors](#-sponsors)
- [License](#-license)

## ✨ Features

### 🛡️ Strongly Typed End-to-End
- **Pydantic v2 models** for every one of the 73 API operations — request bodies validated before they leave your machine, responses validated when they arrive.
- **mypy-strict clean.** Full type coverage, including async, generics, and discriminated unions.
- **Autocomplete everywhere.** Your IDE knows the shape of every field — no more guessing what's in `result["data"]["numbers"]`.

### ⚡ Sync + Async, Same Surface
- `Client` for blocking calls, `AsyncClient` for `await`-based async — identical method names, identical return types.
- Built on `httpx` — supports HTTP/2, connection pooling, and custom transports if you need them.

### 🔁 Production-Grade Transport
- **Automatic retry** with exponential backoff on 429 / 5xx — honors `Retry-After` headers.
- **Configurable timeouts** per client or per call.
- **Bearer auth** managed for you; password→key exchange handled by `client.login()`.
- **Structured exception hierarchy** — `RateLimitError`, `AuthenticationError`, `NotFoundError`, etc. all subclasses of `ApiError` you can catch broadly or narrowly.

### 📞 Complete API Coverage
- **Numbers** — list, get, add, remove, route, translate, CNAM, LIDB, fax, forward, SMS, messaging campaigns, port-out PIN, account moves.
- **Account** — profile, sub-accounts, CDRs, credits, payments, MRC, registration, password recovery.
- **e911** — record provisioning, address validation, lookup, removal.
- **Gateways** — list, create, update, delete, view bound numbers.
- **Messaging** — SMS & MMS sending, message history, 10DLC brand and campaign registration, per-number messaging state.
- **Lookups** — CNAM and LRN dips.
- **iNumbering** — inventory search, coverage queries, number orders, port-in submissions, port-out availability checks.
- **Support** — ticket create / read / update / delete, threaded messages, replies.
- **ACL** — IP allowlist management with structured 409 conflict bodies.
- **Authentication** — switch between Digest, IP-only, or hybrid modes; rotate passwords.

### 🧪 Battle-Tested
- **108 unit tests** at **100% statement + branch coverage.**
- **Integration test suite** that runs read-only operations against `api.voicetel.com` — gated by env vars, safe for CI.
- **No mocks-pretending-to-be-tests.** Mocked HTTP layer with `respx`, real Pydantic validation on every fixture so spec drift gets caught.

### 📦 Clean Distribution
- Zero codegen footprint — every byte hand-written.
- Built with `hatchling`; ships as wheel + sdist.
- `py.typed` marker — downstream type checkers see your imports natively.

## 🚀 Installation

```bash
pip install voicetel-api
```

Requires Python 3.10 or later. Tested against 3.10, 3.11, 3.12, and 3.13.

## 🏁 Quickstart

```python
from voicetel import Client

with Client() as c:
    # Exchange username + password for an API key (one-time per session)
    c.login(username=1000000001, password="hunter2")

    # Typed responses — your IDE knows what `me` is.
    me = c.account.get()
    print(f"Balance: ${me.cash:.2f}  |  Caller ID: {me.callerId}")

    # List your numbers
    for n in c.numbers.list().numbers:
        print(f"{n.number}  route={n.route}  cnam={n.cnam}  sms={n.smsEnabled}")
```

Or, if you already have an API key:

```python
from voicetel import Client

with Client(api_key="32hex...") as c:
    coverage = c.inumbering.coverage(state="NJ")
    for bucket in coverage.coverage:
        print(f"{bucket.npa}-{bucket.nxx}: {bucket.count} TNs available")
```

## 🔑 Authentication

Every endpoint requires `Authorization: Bearer <apikey>` **except** `POST /v2.2/account/api-key`, which exchanges username + password for a fresh key. `Client.login()` (and `AsyncClient.login()`) handles the exchange and installs the returned key on the transport.

Re-fetch the API key after any password change — the old one is invalidated.

> Don't have credentials yet? Get them at **[voicetel.com/docs/api/v2.2/credentials](https://voicetel.com/docs/api/v2.2/credentials/)**.

```python
from voicetel import Client

with Client() as c:
    key = c.login(username=1000000001, password="hunter2")
    # `key` is the new 32-hex bearer; the client already has it installed.
```

## 🗺️ Resource Reference

| Resource | Operations | Example |
|---|---|---|
| `client.account` | Profile, CDR, credits, payments, MRC, signup, recovery, sub-accounts | `c.account.cdr(start=t1, end=t2)` |
| `client.acl` | IP allowlist (CIDR entries) | `c.acl.add(AclModifyRequest(acl=[...]))` |
| `client.authentication` | SIP/HTTP auth mode + password | `c.authentication.update(AuthPutRequest(authType=1))` |
| `client.e911` | Records, address validation, provisioning | `c.e911.validate(E911AddressRequest(...))` |
| `client.gateways` | Termination routes | `c.gateways.list()` |
| `client.inumbering` | Inventory, orders, port-ins | `c.inumbering.search_inventory(npa=201)` |
| `client.lookups` | CNAM & LRN dips | `c.lookups.lrn("2015551234", ani="2012548000")` |
| `client.messaging` | SMS/MMS, 10DLC brands & campaigns | `c.messaging.send(MessageSendRequest(...))` |
| `client.numbers` | All operations on TNs on the account | `c.numbers.assign_campaign("2015551234", ...)` |
| `client.support` | Tickets, replies, attachments | `c.support.create(TicketCreateRequest(...))` |

Every method that takes a request body accepts a typed Pydantic model imported from `voicetel.models`:

```python
from voicetel import Client
from voicetel.models import (
    MessageSendRequest,
    NumberCampaignAssignRequest,
    PortSubmitRequest,
)

with Client(api_key=key) as c:
    sent = c.messaging.send(MessageSendRequest(
        fromNumber="2012548000",
        toNumber="2015551234",
        text="Your code is 482917",
    ))
    print(f"Sent: {sent.id}  ({sent.parts} segment(s))")

    c.numbers.assign_campaign(
        "2015551234",
        NumberCampaignAssignRequest(campaignId="CABC123"),
    )
```

## 🚨 Error Handling

All HTTP errors raise subclasses of `voicetel.ApiError`. Catch broadly or narrowly:

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
from voicetel import Client, NotFoundError, RateLimitError

with Client(api_key=key) as c:
    try:
        n = c.numbers.get("9999999999")
    except NotFoundError:
        print("That number isn't on your account.")
    except RateLimitError as e:
        print(f"Slow down — retry in {e.body.get('retryAfter', '?')}s")
```

## ⚡ Async Support

Identical surface to `Client`, with `await`-based methods:

```python
import asyncio
from voicetel import AsyncClient

async def fetch_state(numbers: list[str]) -> None:
    async with AsyncClient(api_key="...") as c:
        state = await c.messaging.numbers_state(numbers=numbers)
        for s in state.numbers:
            print(f"{s.number}: network={s.network} campaign={s.campaign}")

asyncio.run(fetch_state(["2015551234", "2015551235"]))
```

## ⏱️ Rate Limits

These endpoints are limited to **6 requests per hour per IP**:

- `account/info`
- `account/mrc` (`client.account.recurring_charges()`)
- `account/cdr` (`client.account.cdr()`)
- `account/api-key` (`client.login()`)

The SDK automatically retries 429 responses with `Retry-After` honored, up to `max_retries` (default `2`). To bump it:

```python
Client(api_key=key, max_retries=4, timeout=60.0)
```

## 🛠️ Development

```bash
git clone https://github.com/voicetel/python-sdk
cd python-sdk
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Unit tests (fast, no network)
pytest tests/unit

# 100% coverage gate
pytest tests/unit --cov --cov-fail-under=100

# Lint + type-check
ruff check src tests
mypy src

# Integration tests (live api.voicetel.com, read-only)
cp .env.example .env  # fill in VOICETEL_USERNAME / VOICETEL_PASSWORD
pytest tests/integration

# Build wheel + sdist
python -m build
twine check dist/*
```

## 📖 API Documentation

- **Reference docs:** [voicetel.com/docs/api/v2.2/](https://voicetel.com/docs/api/v2.2/)
- **Interactive playground:** [voicetel.com/docs/api/v2.2/playground/](https://voicetel.com/docs/api/v2.2/playground/) — try the API in your browser without writing any code
- **API credentials:** [voicetel.com/docs/api/v2.2/credentials/](https://voicetel.com/docs/api/v2.2/credentials/)
- **Type definitions:** see the `voicetel.models` module — every wire shape has a Pydantic model.

## 🙌 Contributors

- [Michael Mavroudis](https://github.com/mavroudis) — Lead Developer

Contributions welcome. Open an issue describing the change you want to make, or send a pull request against `main`.

## 💖 Sponsors

| Sponsor | Contribution |
|---------|--------------|
| [VoiceTel Communications](https://www.voicetel.com) | Primary development and production hosting |

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
