"""Resource-method tests against v2.2.10 typed response models.

Each test:
1. Mocks the live endpoint with a payload that the response model can validate.
2. Calls the SDK method.
3. Asserts both that the wire shape is correct (URL, method, body) AND that the typed
   response carries the expected data via attribute access.
"""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest
import respx

from voicetel import AsyncClient, Client
from voicetel.models import (
    AccountAddRequest,
    AccountCdrData,
    AccountData,
    AccountPutRequest,
    AccountRecoverRequest,
    AccountSignupRequest,
    AclModifyRequest,
    AuthPutRequest,
    CidrEntry,
    CnamData,
    E911AddressRequest,
    E911CreateRequest,
    E911Entry,
    E911ProvisionByIdRequest,
    GatewayAddRequest,
    GatewayUpdateRequest,
    LrnLookupData,
    MessageSendRequest,
    MessagingBrandCreateRequest,
    MessagingCampaignCreateRequest,
    NumberAddRequest,
    NumberCampaignAssignRequest,
    NumberCnamRequest,
    NumberDetail,
    NumberFaxRequest,
    NumberForwardRequest,
    NumberLidbRequest,
    NumberMessagingPatchRequest,
    NumberMoveRequest,
    NumberRouteRequest,
    NumbersListData,
    NumberSmsRequest,
    NumberTranslationRequest,
    OrderCreateRequest,
    PortOutPinUpdateRequest,
    PortSubmitRequest,
    TicketCreateRequest,
    TicketReplyRequest,
    TicketUpdateRequest,
)

BASE = "https://api.voicetel.test"


def env(data: Any) -> dict[str, Any]:
    """Build a standard ``{"status":"success","data":...}`` envelope."""
    return {"status": "success", "data": data}


# --------------------------------------------------------------- Account ---


def test_account_get_returns_typed_account_data(
    client: Client, mock_router: respx.Router
) -> None:
    mock_router.get("/v2.2/account").mock(
        return_value=httpx.Response(
            200,
            json=env({
                "username": "1000000001",
                "name": "Acme Inc",
                "email": "u@a.com",
                "cash": 12.50,
                "callerId": "2015551234",
                "ccs": 4,
                "authType": 1,
                "rates": {"sms": 0.01, "mms": 0.05},
                "services": {"sms": True, "mms": False, "e911": True},
            }),
        )
    )
    me = client.account.get()
    assert isinstance(me, AccountData)
    assert me.username == "1000000001"
    assert me.cash == 12.50
    assert me.rates is not None and me.rates.sms == 0.01
    assert me.services is not None and me.services.e911 is True


def test_account_update_payload_and_response(client: Client, mock_router: respx.Router) -> None:
    route = mock_router.put("/v2.2/account").mock(
        return_value=httpx.Response(200, json=env({"updated": ["timezone"]}))
    )
    result = client.account.update(AccountPutRequest(timezone="UTC"))
    assert result.updated == ["timezone"]
    assert json.loads(route.calls.last.request.content) == {"timezone": "UTC"}


def test_account_add(client: Client, mock_router: respx.Router) -> None:
    mock_router.post("/v2.2/account").mock(
        return_value=httpx.Response(
            201,
            json=env({"username": "1000000099", "name": "Sub", "email": "s@x.com", "password": "abc"}),
        )
    )
    result = client.account.add(AccountAddRequest(username=1000000099, name="Sub", email="s@x.com"))
    assert result.password == "abc"
    assert result.username == "1000000099"


def test_account_signup(client: Client, mock_router: respx.Router) -> None:
    mock_router.post("/v2.2/accounts").mock(
        return_value=httpx.Response(
            201, json=env({"username": "1000000099", "email": "x@y.com", "password": "abc"})
        )
    )
    result = client.account.signup(AccountSignupRequest(name="X", email="x@y.com"))
    assert result.password == "abc"


def test_account_cdr_passes_query_and_parses_records(
    client: Client, mock_router: respx.Router
) -> None:
    cdr_payload = env(
        {
            "start": 1747345200,
            "end": 1747258800,
            "cdr": [
                {
                    "id": "abc123",
                    "key": ["1000", "1747345200"],
                    "value": {
                        "dur": "40",
                        "dst": "8008786160",
                        "ba": "0.017500",
                        "nr": "0.025",
                        "cn": "TOLL%20FREE",
                        "ip": "1.2.3.4",
                        "cid": "8666326621",
                    },
                }
            ],
        }
    )
    route = mock_router.get("/v2.2/account/cdr").mock(
        return_value=httpx.Response(200, json=cdr_payload)
    )
    result = client.account.cdr(start=1747345200, end=1747258800)
    assert isinstance(result, AccountCdrData)
    assert result.start == 1747345200
    assert len(result.cdr) == 1
    assert result.cdr[0].id == "abc123"
    assert result.cdr[0].value.dur == "40"  # intentionally string for precision
    assert "start=1747345200" in str(route.calls.last.request.url)


def test_account_credits(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/account/credits").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "credits": [
                        {"amount": 25.0, "date": "2024-09-30T12:52:59+00:00", "paid": False}
                    ]
                }
            ),
        )
    )
    result = client.account.credits()
    assert len(result.credits) == 1
    assert result.credits[0].amount == 25.0
    assert result.credits[0].paid is False


def test_account_recurring_charges(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/account/recurring-charges").mock(
        return_value=httpx.Response(
            200,
            json=env({"charges": [{"amount": 0.5, "description": "DID"}], "total": 0.5}),
        )
    )
    result = client.account.recurring_charges()
    assert result.total == 0.5
    assert result.charges[0].description == "DID"


def test_account_payments(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/account/payments").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "payments": [
                        {
                            "amount": 25.0,
                            "date": "2024-09-30T12:52:59+00:00",
                            "status": "Completed",
                            "payerEmail": "c@e.com",
                            "transactionId": "TX1",
                        }
                    ]
                }
            ),
        )
    )
    result = client.account.payments()
    assert result.payments[0].status == "Completed"


def test_account_registration(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/account/registration").mock(
        return_value=httpx.Response(
            200, json=env({"agent": "Zoiper", "uri": "sip:x@y", "expires": 300})
        )
    )
    result = client.account.registration()
    assert result.agent == "Zoiper"


def test_account_recover_omits_auth(mock_router: respx.Router) -> None:
    route = mock_router.post("/v2.2/account/recovery").mock(
        return_value=httpx.Response(200, json=env({"message": "sent"}))
    )
    c = Client(api_key=None, base_url=BASE, max_retries=0)
    result = c.account.recover(AccountRecoverRequest(email="x@y.com"))
    assert result.message == "sent"
    assert "Authorization" not in route.calls.last.request.headers


# --------------------------------------------------------------------- ACL ---


def test_acl_list(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/acl").mock(
        return_value=httpx.Response(200, json=env({"acl": [{"cidr": "203.0.113.0/24"}]}))
    )
    result = client.acl.list()
    assert result.acl[0].cidr == "203.0.113.0/24"


def test_acl_add_and_remove(client: Client, mock_router: respx.Router) -> None:
    body = AclModifyRequest(acl=[CidrEntry(cidr="203.0.113.0/24")])
    mock_router.post("/v2.2/acl").mock(
        return_value=httpx.Response(200, json=env({"added": [{"cidr": "203.0.113.0/24"}]}))
    )
    mock_router.delete("/v2.2/acl").mock(
        return_value=httpx.Response(200, json=env({"removed": [{"cidr": "203.0.113.0/24"}]}))
    )
    a = client.acl.add(body)
    assert a.added[0].cidr == "203.0.113.0/24"
    r = client.acl.remove(body)
    assert r.removed[0].cidr == "203.0.113.0/24"


# ------------------------------------------------------------------- Auth ---


def test_authentication_get(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/auth").mock(
        return_value=httpx.Response(
            200,
            json=env({"authType": 1, "authTypeDescription": "IP Auth", "acl": [{"cidr": "203.0.113.0/24"}]}),
        )
    )
    result = client.authentication.get()
    assert result.authType == 1
    assert result.acl[0].cidr == "203.0.113.0/24"


def test_authentication_update(client: Client, mock_router: respx.Router) -> None:
    mock_router.put("/v2.2/auth").mock(
        return_value=httpx.Response(200, json=env({"updated": [{"field": "authType", "value": 2}]}))
    )
    result = client.authentication.update(AuthPutRequest(authType=2))
    assert result.updated[0].field == "authType"
    assert result.updated[0].value == 2


# ------------------------------------------------------------------- E911 ---


def test_e911_list(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/e911").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "records": [
                        {
                            "dn": "12015551234",
                            "callername": "ACME",
                            "address1": "1 Main",
                            "city": "Closter",
                            "state": "NJ",
                            "zip": "07624",
                        }
                    ]
                }
            ),
        )
    )
    result = client.e911.list()
    assert isinstance(result.records[0], E911Entry)
    assert result.records[0].dn == "12015551234"


def test_e911_full_surface(client: Client, mock_router: respx.Router) -> None:
    e911_record = {
        "dn": "12015551234",
        "callername": "ACME",
        "address1": "1 Main",
        "city": "Closter",
        "state": "NJ",
        "zip": "07624",
    }
    mock_router.post("/v2.2/e911").mock(
        return_value=httpx.Response(201, json=env({"record": e911_record}))
    )
    mock_router.post("/v2.2/e911/validations").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "address": {
                        "addressid": 1234567,
                        "address1": "1 Main",
                        "city": "Closter",
                        "state": "NJ",
                        "zip": "07624",
                    }
                }
            ),
        )
    )
    mock_router.get("/v2.2/e911/2015551234").mock(
        return_value=httpx.Response(200, json=env({"record": e911_record}))
    )
    mock_router.put("/v2.2/e911/2015551234").mock(
        return_value=httpx.Response(200, json=env({"record": e911_record}))
    )
    mock_router.delete("/v2.2/e911/2015551234").mock(return_value=httpx.Response(204))

    created = client.e911.create(
        E911CreateRequest(
            dn="2015551234",
            callername="ACME",
            address1="1 Main",
            city="Closter",
            state="NJ",
            zip="07624",
        )
    )
    assert created.record.callername == "ACME"
    validated = client.e911.validate(
        E911AddressRequest(address1="1 Main", city="Closter", state="NJ", zip="07624")
    )
    assert validated.address.addressid == 1234567
    got = client.e911.get("2015551234")
    assert got.record.dn == "12015551234"
    provisioned = client.e911.provision(
        "2015551234", E911ProvisionByIdRequest(callername="ACME", addressid=1234567)
    )
    assert provisioned.record.dn == "12015551234"
    assert client.e911.remove("2015551234") is None


# --------------------------------------------------------------- Gateways ---


def test_gateways_full_surface(client: Client, mock_router: respx.Router) -> None:
    gateway = {"id": 1000, "gateway": "1.2.3.4:5060", "prefix": "9", "limit": 23, "system": False}
    mock_router.get("/v2.2/gateways").mock(
        return_value=httpx.Response(200, json=env({"gateways": [gateway]}))
    )
    mock_router.post("/v2.2/gateways").mock(return_value=httpx.Response(201, json=env(gateway)))
    mock_router.get("/v2.2/gateways/1000").mock(return_value=httpx.Response(200, json=env(gateway)))
    mock_router.put("/v2.2/gateways/1000").mock(return_value=httpx.Response(200, json=env(gateway)))
    mock_router.delete("/v2.2/gateways/1000").mock(return_value=httpx.Response(204))
    mock_router.get("/v2.2/gateways/1000/numbers").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "numbers": [
                        {
                            "number": "2015551234",
                            "translated": "2015551234",
                            "forward": False,
                            "forwardTo": None,
                            "cnam": False,
                            "carrier": 0,
                            "smsEnabled": False,
                            "faxEnabled": False,
                        }
                    ]
                }
            ),
        )
    )

    gs = client.gateways.list()
    assert gs.gateways[0].id == 1000

    added = client.gateways.add(GatewayAddRequest(gateway="1.2.3.4:5060"))
    assert added.id == 1000

    got = client.gateways.get(1000)
    assert got.gateway == "1.2.3.4:5060"

    updated = client.gateways.update(1000, GatewayUpdateRequest(prefix="9"))
    assert updated.prefix == "9"

    assert client.gateways.remove(1000) is None

    nums = client.gateways.numbers(1000)
    assert nums.numbers[0].number == "2015551234"


# ---------------------------------------------------------------- Lookups ---


def test_lookups_cnam(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/cnam/2012548000").mock(
        return_value=httpx.Response(200, json=env({"cnam": "VOICETEL", "number": "2012548000"}))
    )
    result = client.lookups.cnam("2012548000")
    assert isinstance(result, CnamData)
    assert result.cnam == "VOICETEL"


def test_lookups_lrn(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/lrn/2015551234/2012548000").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "ani": "2012548000",
                    "destination": "2015551234",
                    "lrn": {
                        "lrn": "12125550000",
                        "state": "NY",
                        "city": "NEW YORK",
                        "rc": "NEW YORK",
                        "lata": "132",
                        "ocn": "9101",
                        "lec": "ATT",
                        "lecType": "ILEC",
                        "jurisdiction": "INTERSTATE",
                        "local": "N",
                    },
                }
            ),
        )
    )
    result = client.lookups.lrn("2015551234", "2012548000")
    assert isinstance(result, LrnLookupData)
    assert result.lrn.lrn == "12125550000"
    assert result.lrn.state == "NY"


# --------------------------------------------------------------- Messaging ---


def test_messaging_full_surface(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/messages").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "number": "2012548000",
                    "type": "sms",
                    "fromTs": 100,
                    "toTs": 200,
                    "messages": [],
                }
            ),
        )
    )
    mock_router.post("/v2.2/messages").mock(
        return_value=httpx.Response(
            201,
            json=env(
                {
                    "id": "abc123",
                    "type": "sms",
                    "fromNumber": "2012548000",
                    "toNumber": "2015551234",
                    "parts": 1,
                }
            ),
        )
    )
    mock_router.post("/v2.2/messaging/brands").mock(
        return_value=httpx.Response(
            201, json=env({"result": {"statusCode": "200", "status": "Success"}})
        )
    )
    mock_router.get("/v2.2/messaging/campaigns").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {"campaigns": [{"id": "C1", "status": "ACTIVE", "numbers": ["2015551234"]}]}
            ),
        )
    )
    mock_router.post("/v2.2/messaging/campaigns").mock(
        return_value=httpx.Response(
            201, json=env({"result": {"statusCode": "200", "status": "Success"}})
        )
    )
    mock_router.get("/v2.2/numbers/messaging").mock(
        return_value=httpx.Response(200, json=env({"numbers": []}))
    )

    hist = client.messaging.history(number="2012548000")
    assert hist.type == "sms"
    sent = client.messaging.send(
        MessageSendRequest(fromNumber="2012548000", toNumber="2015551234", text="hi")
    )
    assert sent.id == "abc123" and sent.type == "sms"
    brand = client.messaging.brands(
        MessagingBrandCreateRequest(messagingBrandId="BABC", messagingBrandName="X")
    )
    assert brand.result.status == "Success"
    status = client.messaging.campaign_status()
    assert status.campaigns[0].id == "C1"
    camp = client.messaging.campaign_create(
        MessagingCampaignCreateRequest(
            messagingBrandId="B", externalCampaignId="C", campaignDescription="d"
        )
    )
    assert camp.result.status == "Success"
    state = client.messaging.numbers_state(numbers=["2015551234", "2015551235"])
    assert state.numbers == []


def test_messaging_numbers_state_no_args(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/numbers/messaging").mock(
        return_value=httpx.Response(200, json=env({"numbers": []}))
    )
    assert client.messaging.numbers_state().numbers == []


# ---------------------------------------------------------------- Numbers ---


_NUMBER_DETAIL = {
    "number": "2015551234",
    "translated": "2015551234",
    "route": 4,
    "gateway": "1.2.3.4:5060",
    "cnam": True,
    "forward": False,
    "forwardTo": None,
    "carrier": 0,
    "smsEnabled": True,
    "faxEnabled": False,
}


def test_numbers_list_and_get(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/numbers").mock(
        return_value=httpx.Response(200, json=env({"numbers": [_NUMBER_DETAIL]}))
    )
    mock_router.get("/v2.2/numbers/2015551234").mock(
        return_value=httpx.Response(200, json=env(_NUMBER_DETAIL))
    )
    ns = client.numbers.list()
    assert isinstance(ns, NumbersListData)
    assert ns.numbers[0].number == "2015551234"
    n = client.numbers.get("2015551234")
    assert isinstance(n, NumberDetail)
    assert n.cnam is True


def test_numbers_204_endpoints_return_none(client: Client, mock_router: respx.Router) -> None:
    mock_router.delete("/v2.2/numbers/2015551234").mock(return_value=httpx.Response(204))
    mock_router.post("/v2.2/numbers/2015551234/release").mock(return_value=httpx.Response(204))
    mock_router.delete("/v2.2/numbers/2015551234/fax").mock(return_value=httpx.Response(204))
    mock_router.delete("/v2.2/numbers/2015551234/forward").mock(return_value=httpx.Response(204))
    mock_router.delete("/v2.2/numbers/2015551234/sms").mock(return_value=httpx.Response(204))
    assert client.numbers.remove("2015551234") is None
    assert client.numbers.release("2015551234") is None
    assert client.numbers.remove_fax("2015551234") is None
    assert client.numbers.remove_forward("2015551234") is None
    assert client.numbers.remove_sms("2015551234") is None


def test_numbers_with_typed_bodies(client: Client, mock_router: respx.Router) -> None:
    mock_router.post("/v2.2/numbers").mock(
        return_value=httpx.Response(201, json=env({"number": "2015551234", "route": 4}))
    )
    mock_router.patch("/v2.2/numbers/2015551234").mock(
        return_value=httpx.Response(
            200, json=env({"number": "2015551234", "accountId": 99, "route": 4})
        )
    )
    mock_router.put("/v2.2/numbers/2015551234/route").mock(
        return_value=httpx.Response(200, json=env({"number": "2015551234", "route": 7}))
    )
    mock_router.put("/v2.2/numbers/2015551234/translation").mock(
        return_value=httpx.Response(
            200, json=env({"number": "2015551234", "translation": "2015551235"})
        )
    )
    mock_router.put("/v2.2/numbers/2015551234/cnam").mock(
        return_value=httpx.Response(200, json=env({"number": "2015551234", "cnam": True}))
    )
    mock_router.put("/v2.2/numbers/2015551234/lidb").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "number": "2015551234",
                    "cnam": "ACME",
                    "customerOrderReference": "ref-1",
                    "carrierStatus": "Success",
                }
            ),
        )
    )
    mock_router.get("/v2.2/numbers/2015551234/fax").mock(
        return_value=httpx.Response(200, json=env({"number": "2015551234", "email": "f@x.com"}))
    )
    mock_router.put("/v2.2/numbers/2015551234/fax").mock(
        return_value=httpx.Response(200, json=env({"number": "2015551234", "email": "f@x.com"}))
    )
    mock_router.put("/v2.2/numbers/2015551234/forward").mock(
        return_value=httpx.Response(
            200, json=env({"number": "2015551234", "forwardTo": "2125551234"})
        )
    )
    mock_router.get("/v2.2/numbers/2015551234/sms").mock(
        return_value=httpx.Response(
            200, json=env({"number": "2015551234", "type": "email", "resource": "x@y.com"})
        )
    )
    mock_router.put("/v2.2/numbers/2015551234/sms").mock(
        return_value=httpx.Response(
            200, json=env({"number": "2015551234", "type": "email", "resource": "x@y.com"})
        )
    )
    mock_router.get("/v2.2/numbers/2015551234/messaging").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "number": "2015551234",
                    "enabled": True,
                    "carrier": 16,
                    "routeIn": 0,
                    "resource": "https://example.com",
                    "network": "A",
                    "campaign": None,
                }
            ),
        )
    )
    mock_router.patch("/v2.2/numbers/2015551234/messaging").mock(
        return_value=httpx.Response(
            200, json=env({"number": "2015551234", "updated": ["routeIn"]})
        )
    )
    mock_router.put("/v2.2/numbers/2015551234/messaging-campaign").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "number": "2015551234",
                    "campaignId": "C123",
                    "carrier": 17,
                    "network": "A",
                    "upstreamCnpId": "SFL9UTQ",
                    "previousNetwork": None,
                    "previousNetworkCleared": False,
                }
            ),
        )
    )
    mock_router.delete("/v2.2/numbers/2015551234/messaging-campaign").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "number": "2015551234",
                    "campaignId": "C123",
                    "network": "A",
                    "upstreamCnpId": "SFL9UTQ",
                    "unassigned": True,
                }
            ),
        )
    )
    mock_router.delete("/v2.2/numbers/messaging-campaign").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "campaignId": "C123",
                    "network": "A",
                    "upstreamCnpId": "SFL9UTQ",
                    "unassignedNumbers": ["2015551234"],
                    "failed": [],
                }
            ),
        )
    )
    mock_router.patch("/v2.2/numbers/2015551234/port-out-pin").mock(
        return_value=httpx.Response(
            200, json=env({"number": "2015551234", "portOutPin": "1234"})
        )
    )

    added = client.numbers.add(NumberAddRequest(number="2015551234"))
    assert added.number == "2015551234"

    moved = client.numbers.move("2015551234", NumberMoveRequest(accountId=99, route=4))
    assert moved.accountId == 99

    route = client.numbers.set_route("2015551234", NumberRouteRequest(route=7))
    assert route.route == 7

    tr = client.numbers.set_translation(
        "2015551234", NumberTranslationRequest(translation="2015551235")
    )
    assert tr.translation == "2015551235"

    cn = client.numbers.set_cnam("2015551234", NumberCnamRequest(enabled=True))
    assert cn.cnam is True

    lidb = client.numbers.set_lidb("2015551234", NumberLidbRequest(cnam="ACME"))
    assert lidb.carrierStatus == "Success"

    fg = client.numbers.get_fax("2015551234")
    assert fg.email == "f@x.com"

    fs = client.numbers.set_fax("2015551234", NumberFaxRequest(email="f@x.com"))
    assert fs.email == "f@x.com"

    fwd = client.numbers.set_forward("2015551234", NumberForwardRequest(destination=2125551234))
    assert fwd.forwardTo == "2125551234"

    sg = client.numbers.get_sms("2015551234")
    assert sg.type == "email"

    ss = client.numbers.set_sms(
        "2015551234", NumberSmsRequest(type="email", resource="x@y.com")
    )
    assert ss.resource == "x@y.com"

    msg = client.numbers.get_messaging("2015551234")
    assert msg.network == "A"

    pm = client.numbers.patch_messaging(
        "2015551234", NumberMessagingPatchRequest(routeIn=1)
    )
    assert "routeIn" in pm.updated

    ac = client.numbers.assign_campaign(
        "2015551234", NumberCampaignAssignRequest(campaignId="C123")
    )
    assert ac.carrier == 17

    uc = client.numbers.unassign_campaign("2015551234")
    assert uc.unassigned is True

    bulk = client.numbers.bulk_unassign_campaign(["2015551234"])
    assert bulk.unassignedNumbers == ["2015551234"]

    pin = client.numbers.set_port_out_pin(
        "2015551234", PortOutPinUpdateRequest(pin="1234")
    )
    assert pin.portOutPin == "1234"


# ---------------------------------------------------------------- Support ---


def test_support_full_surface(client: Client, mock_router: respx.Router) -> None:
    ticket = {"id": 1, "status": "active", "subject": "S", "number": 1015}
    mock_router.get("/v2.2/support/tickets").mock(
        return_value=httpx.Response(200, json=env({"tickets": [ticket]}))
    )
    mock_router.post("/v2.2/support/tickets").mock(
        return_value=httpx.Response(201, json=env({"ticket": ticket}))
    )
    mock_router.get("/v2.2/support/tickets/1").mock(
        return_value=httpx.Response(200, json=env({"ticket": ticket}))
    )
    mock_router.put("/v2.2/support/tickets/1").mock(
        return_value=httpx.Response(200, json=env({"id": 1, "status": "success"}))
    )
    mock_router.delete("/v2.2/support/tickets/1").mock(return_value=httpx.Response(204))
    mock_router.get("/v2.2/support/tickets/1/messages").mock(
        return_value=httpx.Response(200, json=env({"messages": []}))
    )
    mock_router.post("/v2.2/support/tickets/1/replies").mock(
        return_value=httpx.Response(201, json=env({"message": "Reply added"}))
    )

    lst = client.support.list()
    assert lst.tickets[0].id == 1
    assert lst.tickets[0].ticket_number == 1015  # aliased from `number`

    created = client.support.create(TicketCreateRequest(subject="s", message="m"))
    assert created.ticket.subject == "S"

    got = client.support.get(1)
    assert got.ticket.id == 1

    upd = client.support.update(1, TicketUpdateRequest(status="closed"))
    assert upd.status == "success"

    assert client.support.delete(1) is None

    msgs = client.support.messages(1)
    assert msgs.messages == []

    rep = client.support.reply(1, TicketReplyRequest(message="ok"))
    assert rep.message == "Reply added"


# ------------------------------------------------------------- iNumbering ---


def test_inumbering_full_surface(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/inventory").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "numbers": [
                        {
                            "number": "2019085750",
                            "rateCenter": "CLOSTER",
                            "city": "Closter",
                            "province": "NJ",
                            "lata": "224",
                        }
                    ]
                }
            ),
        )
    )
    mock_router.get("/v2.2/inventory/coverage").mock(
        return_value=httpx.Response(200, json=env({"coverage": [{"count": 100, "npa": "201"}]}))
    )
    mock_router.post("/v2.2/orders").mock(
        return_value=httpx.Response(
            201,
            json=env(
                {
                    "orderId": "1747345200",
                    "amountCharged": 0.5,
                    "numbersOrdered": ["2015551234"],
                    "failed": [],
                }
            ),
        )
    )
    mock_router.get("/v2.2/ports").mock(
        return_value=httpx.Response(200, json=env({"ports": [{"id": "abc", "status": "Complete"}]}))
    )
    mock_router.get("/v2.2/ports/42").mock(
        return_value=httpx.Response(200, json=env({"port": {"id": "abc", "status": "Complete"}}))
    )
    mock_router.post("/v2.2/ports").mock(
        return_value=httpx.Response(
            201,
            json=env(
                {
                    "pid": "a3a2a",
                    "ticket": 2114,
                    "message": "ok",
                    "loaUrl": "https://x/loa",
                    "portUrl": "https://x/port",
                }
            ),
        )
    )
    mock_router.get("/v2.2/ports/availability/2017301000").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "number": "2017301000",
                    "portable": True,
                    "losingCarrier": "Sinch Voice-NSR-10X-Port/1",
                    "localRoutingNumber": "6463071993",
                    "rateCenterTier": "0",
                    "reason": None,
                }
            ),
        )
    )

    inv = client.inumbering.search_inventory(state="NJ", limit=10)
    assert inv.numbers[0].number == "2019085750"
    cov = client.inumbering.coverage(state="NJ")
    assert cov.coverage[0].count == 100
    order = client.inumbering.order(OrderCreateRequest(numbers=["2015551234"]))
    assert order.orderId == "1747345200"
    ports = client.inumbering.ports()
    assert ports.ports[0].id == "abc"
    port = client.inumbering.port(42)
    assert port.port.id == "abc"
    submitted = client.inumbering.submit_port(
        PortSubmitRequest(
            did=["2015551234"],
            name="Acme",
            nameType="business",
            lcBtn="2015551000",
            lcAccountNumber="acct",
            streetNumber="550",
            street="Main",
            streetType="ST",
            city="Chicago",
            state="IL",
            zip="60601",
            country="US",
            authPerson="J",
        )
    )
    assert submitted.pid == "a3a2a"
    avail = client.inumbering.port_availability("2017301000")
    assert avail.portable is True
    # v2.2.10 added these two fields:
    assert avail.localRoutingNumber == "6463071993"
    assert avail.rateCenterTier == "0"


# ----------------------------------------------------- response unwrapping ---


def test_unwrap_passes_through_non_envelope(client: Client, mock_router: respx.Router) -> None:
    """If the server returns a bare object (no `{status, data}` envelope), unwrap shouldn't choke."""
    mock_router.get("/v2.2/cnam/2015551234").mock(
        return_value=httpx.Response(200, json={"cnam": "VOICETEL", "number": "2015551234"})
    )
    result = client.lookups.cnam("2015551234")
    assert result.cnam == "VOICETEL"


# -------------------------------------------------------------- async sanity ---


@pytest.mark.asyncio
async def test_async_client_e2e(mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/account").mock(
        return_value=httpx.Response(200, json=env({"username": "1", "name": "X"}))
    )
    async with AsyncClient(api_key="k", base_url=BASE, max_retries=0) as c:
        result = await c.account.get()
        assert result.username == "1"


@pytest.mark.asyncio
async def test_async_full_resource_surface(mock_router: respx.Router) -> None:
    """Hit every async resource group at least once to cover the AsyncResource code paths."""
    cidr = {"cidr": "203.0.113.0/24"}
    mock_router.get("/v2.2/acl").mock(return_value=httpx.Response(200, json=env({"acl": [cidr]})))
    mock_router.post("/v2.2/acl").mock(return_value=httpx.Response(200, json=env({"added": [cidr]})))
    mock_router.delete("/v2.2/acl").mock(
        return_value=httpx.Response(200, json=env({"removed": [cidr]}))
    )
    mock_router.get("/v2.2/auth").mock(
        return_value=httpx.Response(
            200, json=env({"authType": 1, "authTypeDescription": "IP", "acl": [cidr]})
        )
    )
    mock_router.put("/v2.2/auth").mock(
        return_value=httpx.Response(200, json=env({"updated": [{"field": "authType", "value": 1}]}))
    )
    e911_record = {
        "dn": "12015551234",
        "callername": "ACME",
        "address1": "1",
        "city": "C",
        "state": "NJ",
        "zip": "07601",
    }
    mock_router.get("/v2.2/e911").mock(
        return_value=httpx.Response(200, json=env({"records": [e911_record]}))
    )
    mock_router.post("/v2.2/e911").mock(
        return_value=httpx.Response(201, json=env({"record": e911_record}))
    )
    mock_router.post("/v2.2/e911/validations").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {"address": {"addressid": 1, "address1": "1", "city": "C", "state": "NJ", "zip": "07601"}}
            ),
        )
    )
    mock_router.get("/v2.2/e911/2015551234").mock(
        return_value=httpx.Response(200, json=env({"record": e911_record}))
    )
    mock_router.put("/v2.2/e911/2015551234").mock(
        return_value=httpx.Response(200, json=env({"record": e911_record}))
    )
    mock_router.delete("/v2.2/e911/2015551234").mock(return_value=httpx.Response(204))
    gw = {"id": 1, "gateway": "1.2.3.4", "prefix": "9", "limit": 23, "system": False}
    mock_router.get("/v2.2/gateways").mock(
        return_value=httpx.Response(200, json=env({"gateways": [gw]}))
    )
    mock_router.post("/v2.2/gateways").mock(return_value=httpx.Response(201, json=env(gw)))
    mock_router.get("/v2.2/gateways/1").mock(return_value=httpx.Response(200, json=env(gw)))
    mock_router.put("/v2.2/gateways/1").mock(return_value=httpx.Response(200, json=env(gw)))
    mock_router.delete("/v2.2/gateways/1").mock(return_value=httpx.Response(204))
    mock_router.get("/v2.2/gateways/1/numbers").mock(
        return_value=httpx.Response(200, json=env({"numbers": []}))
    )
    mock_router.get("/v2.2/cnam/2015551234").mock(
        return_value=httpx.Response(200, json=env({"cnam": "X", "number": "2015551234"}))
    )
    mock_router.get("/v2.2/lrn/2015551234/2012548000").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "ani": "2012548000",
                    "destination": "2015551234",
                    "lrn": {"lrn": "12125550000"},
                }
            ),
        )
    )
    mock_router.get("/v2.2/messages").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {"number": "2015551234", "type": "sms", "fromTs": 0, "toTs": 0, "messages": []}
            ),
        )
    )
    mock_router.post("/v2.2/messages").mock(
        return_value=httpx.Response(
            201,
            json=env(
                {
                    "id": "x",
                    "type": "sms",
                    "fromNumber": "2012548000",
                    "toNumber": "2015551234",
                    "parts": 1,
                }
            ),
        )
    )
    mock_router.post("/v2.2/messaging/brands").mock(
        return_value=httpx.Response(
            201, json=env({"result": {"statusCode": "200", "status": "Success"}})
        )
    )
    mock_router.get("/v2.2/messaging/campaigns").mock(
        return_value=httpx.Response(200, json=env({"campaigns": []}))
    )
    mock_router.post("/v2.2/messaging/campaigns").mock(
        return_value=httpx.Response(
            201, json=env({"result": {"statusCode": "200", "status": "Success"}})
        )
    )
    mock_router.get("/v2.2/numbers/messaging").mock(
        return_value=httpx.Response(200, json=env({"numbers": []}))
    )
    mock_router.get("/v2.2/numbers").mock(
        return_value=httpx.Response(200, json=env({"numbers": [_NUMBER_DETAIL]}))
    )
    mock_router.post("/v2.2/numbers").mock(
        return_value=httpx.Response(201, json=env({"number": "2015551234", "route": 4}))
    )
    mock_router.get("/v2.2/numbers/2015551234").mock(
        return_value=httpx.Response(200, json=env(_NUMBER_DETAIL))
    )
    mock_router.delete("/v2.2/numbers/2015551234").mock(return_value=httpx.Response(204))
    mock_router.patch("/v2.2/numbers/2015551234").mock(
        return_value=httpx.Response(
            200, json=env({"number": "2015551234", "accountId": 1, "route": 4})
        )
    )
    mock_router.post("/v2.2/numbers/2015551234/release").mock(return_value=httpx.Response(204))
    mock_router.put("/v2.2/numbers/2015551234/route").mock(
        return_value=httpx.Response(200, json=env({"number": "2015551234", "route": 1}))
    )
    mock_router.put("/v2.2/numbers/2015551234/translation").mock(
        return_value=httpx.Response(
            200, json=env({"number": "2015551234", "translation": "2015551235"})
        )
    )
    mock_router.put("/v2.2/numbers/2015551234/cnam").mock(
        return_value=httpx.Response(200, json=env({"number": "2015551234", "cnam": True}))
    )
    mock_router.put("/v2.2/numbers/2015551234/lidb").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "number": "2015551234",
                    "cnam": "ACME",
                    "customerOrderReference": "x",
                    "carrierStatus": "Success",
                }
            ),
        )
    )
    mock_router.get("/v2.2/numbers/2015551234/fax").mock(
        return_value=httpx.Response(200, json=env({"number": "2015551234", "email": "f@x.com"}))
    )
    mock_router.put("/v2.2/numbers/2015551234/fax").mock(
        return_value=httpx.Response(200, json=env({"number": "2015551234", "email": "f@x.com"}))
    )
    mock_router.delete("/v2.2/numbers/2015551234/fax").mock(return_value=httpx.Response(204))
    mock_router.put("/v2.2/numbers/2015551234/forward").mock(
        return_value=httpx.Response(
            200, json=env({"number": "2015551234", "forwardTo": "2125551234"})
        )
    )
    mock_router.delete("/v2.2/numbers/2015551234/forward").mock(return_value=httpx.Response(204))
    mock_router.get("/v2.2/numbers/2015551234/sms").mock(
        return_value=httpx.Response(
            200, json=env({"number": "2015551234", "type": "email", "resource": "x@y.com"})
        )
    )
    mock_router.put("/v2.2/numbers/2015551234/sms").mock(
        return_value=httpx.Response(
            200, json=env({"number": "2015551234", "type": "email", "resource": "x@y.com"})
        )
    )
    mock_router.delete("/v2.2/numbers/2015551234/sms").mock(return_value=httpx.Response(204))
    mock_router.get("/v2.2/numbers/2015551234/messaging").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "number": "2015551234",
                    "enabled": True,
                    "carrier": 16,
                    "routeIn": 0,
                    "resource": "x",
                    "network": "A",
                    "campaign": None,
                }
            ),
        )
    )
    mock_router.patch("/v2.2/numbers/2015551234/messaging").mock(
        return_value=httpx.Response(
            200, json=env({"number": "2015551234", "updated": ["routeIn"]})
        )
    )
    mock_router.put("/v2.2/numbers/2015551234/messaging-campaign").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "number": "2015551234",
                    "campaignId": "C1",
                    "carrier": 17,
                    "network": "A",
                    "upstreamCnpId": "SFL9UTQ",
                    "previousNetwork": None,
                    "previousNetworkCleared": False,
                }
            ),
        )
    )
    mock_router.delete("/v2.2/numbers/2015551234/messaging-campaign").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "number": "2015551234",
                    "campaignId": "C1",
                    "network": "A",
                    "upstreamCnpId": "SFL9UTQ",
                    "unassigned": True,
                }
            ),
        )
    )
    mock_router.delete("/v2.2/numbers/messaging-campaign").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "campaignId": "C1",
                    "network": "A",
                    "upstreamCnpId": "SFL9UTQ",
                    "unassignedNumbers": ["2015551234"],
                    "failed": [],
                }
            ),
        )
    )
    mock_router.patch("/v2.2/numbers/2015551234/port-out-pin").mock(
        return_value=httpx.Response(
            200, json=env({"number": "2015551234", "portOutPin": "1234"})
        )
    )
    mock_router.get("/v2.2/account").mock(
        return_value=httpx.Response(200, json=env({"username": "1", "name": "X"}))
    )
    mock_router.put("/v2.2/account").mock(
        return_value=httpx.Response(200, json=env({"updated": ["timezone"]}))
    )
    mock_router.post("/v2.2/account").mock(
        return_value=httpx.Response(
            201, json=env({"username": "2", "name": "Y", "email": "y@x.com", "password": "p"})
        )
    )
    mock_router.post("/v2.2/accounts").mock(
        return_value=httpx.Response(201, json=env({"username": "2", "name": "Y"}))
    )
    mock_router.get("/v2.2/account/cdr").mock(
        return_value=httpx.Response(200, json=env({"start": 0, "end": 0, "cdr": []}))
    )
    mock_router.get("/v2.2/account/credits").mock(
        return_value=httpx.Response(200, json=env({"credits": []}))
    )
    mock_router.get("/v2.2/account/recurring-charges").mock(
        return_value=httpx.Response(200, json=env({"charges": [], "total": 0.0}))
    )
    mock_router.get("/v2.2/account/payments").mock(
        return_value=httpx.Response(200, json=env({"payments": []}))
    )
    mock_router.get("/v2.2/account/registration").mock(
        return_value=httpx.Response(200, json=env({"agent": "Z"}))
    )
    mock_router.post("/v2.2/account/recovery").mock(
        return_value=httpx.Response(200, json=env({"message": "ok"}))
    )
    ticket = {"id": 1, "status": "active", "subject": "S"}
    mock_router.get("/v2.2/support/tickets").mock(
        return_value=httpx.Response(200, json=env({"tickets": [ticket]}))
    )
    mock_router.post("/v2.2/support/tickets").mock(
        return_value=httpx.Response(201, json=env({"ticket": ticket}))
    )
    mock_router.get("/v2.2/support/tickets/1").mock(
        return_value=httpx.Response(200, json=env({"ticket": ticket}))
    )
    mock_router.put("/v2.2/support/tickets/1").mock(
        return_value=httpx.Response(200, json=env({"id": 1, "status": "success"}))
    )
    mock_router.delete("/v2.2/support/tickets/1").mock(return_value=httpx.Response(204))
    mock_router.get("/v2.2/support/tickets/1/messages").mock(
        return_value=httpx.Response(200, json=env({"messages": []}))
    )
    mock_router.post("/v2.2/support/tickets/1/replies").mock(
        return_value=httpx.Response(201, json=env({"message": "Reply added"}))
    )
    mock_router.get("/v2.2/inventory").mock(
        return_value=httpx.Response(200, json=env({"numbers": []}))
    )
    mock_router.get("/v2.2/inventory/coverage").mock(
        return_value=httpx.Response(200, json=env({"coverage": []}))
    )
    mock_router.post("/v2.2/orders").mock(
        return_value=httpx.Response(
            201,
            json=env(
                {"orderId": "1", "amountCharged": 0.0, "numbersOrdered": [], "failed": []}
            ),
        )
    )
    mock_router.get("/v2.2/ports").mock(
        return_value=httpx.Response(200, json=env({"ports": []}))
    )
    mock_router.post("/v2.2/ports").mock(
        return_value=httpx.Response(
            201,
            json=env(
                {
                    "pid": "x",
                    "ticket": 1,
                    "message": "ok",
                    "loaUrl": "https://x",
                    "portUrl": "https://x",
                }
            ),
        )
    )
    mock_router.get("/v2.2/ports/42").mock(
        return_value=httpx.Response(200, json=env({"port": {"status": "Complete"}}))
    )
    mock_router.get("/v2.2/ports/availability/2015551234").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "number": "2015551234",
                    "portable": True,
                    "losingCarrier": None,
                    "reason": None,
                }
            ),
        )
    )

    async with AsyncClient(api_key="k", base_url=BASE, max_retries=0) as c:
        await c.acl.list()
        await c.acl.add(AclModifyRequest(acl=[CidrEntry(cidr="203.0.113.0/24")]))
        await c.acl.remove(AclModifyRequest(acl=[CidrEntry(cidr="203.0.113.0/24")]))
        await c.authentication.get()
        await c.authentication.update(AuthPutRequest(authType=1))
        await c.e911.list()
        await c.e911.create(
            E911CreateRequest(
                dn="2015551234",
                callername="x",
                address1="1",
                city="C",
                state="NJ",
                zip="07601",
            )
        )
        await c.e911.validate(
            E911AddressRequest(address1="1", city="C", state="NJ", zip="07601")
        )
        await c.e911.get("2015551234")
        await c.e911.provision(
            "2015551234", E911ProvisionByIdRequest(callername="x", addressid=1)
        )
        await c.e911.remove("2015551234")
        await c.gateways.list()
        await c.gateways.add(GatewayAddRequest(gateway="1.2.3.4"))
        await c.gateways.get(1)
        await c.gateways.update(1, GatewayUpdateRequest(prefix="9"))
        await c.gateways.remove(1)
        await c.gateways.numbers(1)
        await c.lookups.cnam("2015551234")
        await c.lookups.lrn("2015551234", "2012548000")
        await c.messaging.history()
        await c.messaging.send(
            MessageSendRequest(fromNumber="2012548000", toNumber="2015551234", text="hi")
        )
        await c.messaging.brands(
            MessagingBrandCreateRequest(messagingBrandId="BABC", messagingBrandName="X")
        )
        await c.messaging.campaign_status()
        await c.messaging.campaign_create(
            MessagingCampaignCreateRequest(
                messagingBrandId="B", externalCampaignId="C", campaignDescription="d"
            )
        )
        await c.messaging.numbers_state(numbers=["2015551234"])
        await c.messaging.numbers_state()
        await c.numbers.list()
        await c.numbers.add(NumberAddRequest(number="2015551234"))
        await c.numbers.get("2015551234")
        await c.numbers.remove("2015551234")
        await c.numbers.move("2015551234", NumberMoveRequest(accountId=1, route=4))
        await c.numbers.release("2015551234")
        await c.numbers.set_route("2015551234", NumberRouteRequest(route=1))
        await c.numbers.set_translation(
            "2015551234", NumberTranslationRequest(translation="2015551235")
        )
        await c.numbers.set_cnam("2015551234", NumberCnamRequest(enabled=True))
        await c.numbers.set_lidb("2015551234", NumberLidbRequest(cnam="ACME"))
        await c.numbers.get_fax("2015551234")
        await c.numbers.set_fax("2015551234", NumberFaxRequest(email="f@x.com"))
        await c.numbers.remove_fax("2015551234")
        await c.numbers.set_forward(
            "2015551234", NumberForwardRequest(destination=2125551234)
        )
        await c.numbers.remove_forward("2015551234")
        await c.numbers.get_sms("2015551234")
        await c.numbers.set_sms(
            "2015551234", NumberSmsRequest(type="email", resource="x@y.com")
        )
        await c.numbers.remove_sms("2015551234")
        await c.numbers.get_messaging("2015551234")
        await c.numbers.patch_messaging(
            "2015551234", NumberMessagingPatchRequest(routeIn=1)
        )
        await c.numbers.assign_campaign(
            "2015551234", NumberCampaignAssignRequest(campaignId="C1")
        )
        await c.numbers.unassign_campaign("2015551234")
        await c.numbers.bulk_unassign_campaign(["2015551234"])
        await c.numbers.set_port_out_pin(
            "2015551234", PortOutPinUpdateRequest(pin="1234")
        )
        await c.account.get()
        await c.account.update(AccountPutRequest(timezone="UTC"))
        await c.account.add(AccountAddRequest(username=2, name="Y", email="y@x.com"))
        await c.account.signup(AccountSignupRequest(name="Y", email="y@x.com"))
        await c.account.cdr(start=0, end=0)
        await c.account.credits()
        await c.account.recurring_charges()
        await c.account.payments()
        await c.account.registration()
        await c.account.recover(AccountRecoverRequest(email="x@y.com"))
        await c.support.list()
        await c.support.create(TicketCreateRequest(subject="s", message="m"))
        await c.support.get(1)
        await c.support.update(1, TicketUpdateRequest(status="closed"))
        await c.support.delete(1)
        await c.support.messages(1)
        await c.support.reply(1, TicketReplyRequest(message="ok"))
        await c.inumbering.search_inventory(state="NJ")
        await c.inumbering.coverage()
        await c.inumbering.order(OrderCreateRequest(numbers=["2015551234"]))
        await c.inumbering.ports()
        await c.inumbering.port(42)
        await c.inumbering.submit_port(
            PortSubmitRequest(
                did=["2015551234"],
                name="A",
                nameType="business",
                lcBtn="2015551000",
                lcAccountNumber="x",
                streetNumber="1",
                street="M",
                streetType="ST",
                city="C",
                state="IL",
                zip="60601",
                country="US",
                authPerson="J",
            )
        )
        await c.inumbering.port_availability("2015551234")
