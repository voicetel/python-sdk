"""Resource-method tests.

We map each public method to (HTTP method, path, body?) and assert the wire is correct. The
transport itself is covered separately; here we only verify the resource layer translates
calls correctly.
"""

from __future__ import annotations

import httpx
import pytest
import respx

from voicetel import AsyncClient, Client
from voicetel.models import (
    AccountAddRequest,
    AccountPutRequest,
    AccountRecoverRequest,
    AccountSignupRequest,
    AclModifyRequest,
    AuthPutRequest,
    CidrEntry,
    E911AddressRequest,
    E911CreateRequest,
    E911ProvisionByIdRequest,
    GatewayAddRequest,
    GatewayUpdateRequest,
    MessageSendRequest,
    MessagingBrandCreateRequest,
    MessagingCampaignCreateRequest,
    NumberAddRequest,
    NumberCampaignAssignRequest,
    NumberCnamRequest,
    NumberFaxRequest,
    NumberForwardRequest,
    NumberLibdRequest,
    NumberMessagingPatchRequest,
    NumberMoveRequest,
    NumberRouteRequest,
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


def env(data: object) -> dict[str, object]:
    return {"status": "success", "data": data}


# ----------------------------------------------------------- Account ---


def test_account_get(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/account").mock(return_value=httpx.Response(200, json=env({"id": 1})))
    assert client.account.get() == {"id": 1}


def test_account_update(client: Client, mock_router: respx.Router) -> None:
    route = mock_router.put("/v2.2/account").mock(
        return_value=httpx.Response(200, json=env({"updated": True}))
    )
    assert client.account.update(AccountPutRequest(timezone="UTC")) == {"updated": True}
    import json

    assert json.loads(route.calls.last.request.content) == {"timezone": "UTC"}


def test_account_add(client: Client, mock_router: respx.Router) -> None:
    mock_router.post("/v2.2/account").mock(return_value=httpx.Response(200, json=env({"ok": 1})))
    client.account.add(AccountAddRequest(username=1, name="x", email="x@y.com"))


def test_account_list(client: Client, mock_router: respx.Router) -> None:
    mock_router.post("/v2.2/accounts").mock(return_value=httpx.Response(200, json=env([1, 2])))
    assert client.account.list() == [1, 2]


def test_account_signup(client: Client, mock_router: respx.Router) -> None:
    mock_router.post("/v2.2/accounts").mock(return_value=httpx.Response(200, json=env({})))
    client.account.signup(AccountSignupRequest(name="x", email="x@y.com"))


def test_account_cdr_passes_query(client: Client, mock_router: respx.Router) -> None:
    route = mock_router.get("/v2.2/account/cdr").mock(
        return_value=httpx.Response(200, json=env([]))
    )
    client.account.cdr(start=100, end=200)
    url = str(route.calls.last.request.url)
    assert "start=100" in url and "end=200" in url


def test_account_credits(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/account/credits").mock(
        return_value=httpx.Response(200, json=env([]))
    )
    client.account.credits()


def test_account_recurring_charges(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/account/recurring-charges").mock(
        return_value=httpx.Response(200, json=env([]))
    )
    client.account.recurring_charges()


def test_account_payments(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/account/payments").mock(
        return_value=httpx.Response(200, json=env([]))
    )
    client.account.payments()


def test_account_registration(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/account/registration").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    client.account.registration()


def test_account_recover_does_not_send_auth(mock_router: respx.Router) -> None:
    route = mock_router.post("/v2.2/account/recovery").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    Client(api_key=None, base_url=BASE, max_retries=0).account.recover(
        AccountRecoverRequest(email="x@y.com")
    )
    assert "Authorization" not in route.calls.last.request.headers


# ------------------------------------------------------------- ACL ---


def test_acl_list_add_remove(client: Client, mock_router: respx.Router) -> None:
    body = AclModifyRequest(acl=[CidrEntry(cidr="203.0.113.0/24")])
    mock_router.get("/v2.2/acl").mock(return_value=httpx.Response(200, json=env([])))
    mock_router.post("/v2.2/acl").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.delete("/v2.2/acl").mock(return_value=httpx.Response(200, json=env({})))
    client.acl.list()
    client.acl.add(body)
    client.acl.remove(body)


# ----------------------------------------------------- Authentication ---


def test_authentication_get_update(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/auth").mock(return_value=httpx.Response(200, json=env({"t": 1})))
    mock_router.put("/v2.2/auth").mock(return_value=httpx.Response(200, json=env({})))
    assert client.authentication.get() == {"t": 1}
    client.authentication.update(AuthPutRequest(authType=1))


# -------------------------------------------------------------- E911 ---


def test_e911_full_surface(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/e911").mock(return_value=httpx.Response(200, json=env([])))
    mock_router.post("/v2.2/e911").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.post("/v2.2/e911/validations").mock(
        return_value=httpx.Response(200, json=env({"addressid": 1}))
    )
    mock_router.get("/v2.2/e911/2015551234").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/e911/2015551234").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.delete("/v2.2/e911/2015551234").mock(
        return_value=httpx.Response(200, json=env({}))
    )

    client.e911.list()
    client.e911.create(
        E911CreateRequest(
            dn="2015551234",
            callername="x",
            address1="1 Main",
            city="C",
            state="NJ",
            zip="07601",
        )
    )
    client.e911.validate(
        E911AddressRequest(address1="1 Main", city="C", state="NJ", zip="07601")
    )
    client.e911.get("2015551234")
    client.e911.provision("2015551234", E911ProvisionByIdRequest(callername="x", addressid=1))
    client.e911.remove("2015551234")


# ---------------------------------------------------------- Gateways ---


def test_gateways_full_surface(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/gateways").mock(return_value=httpx.Response(200, json=env([])))
    mock_router.post("/v2.2/gateways").mock(
        return_value=httpx.Response(200, json=env({"id": 1}))
    )
    mock_router.get("/v2.2/gateways/1").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.put("/v2.2/gateways/1").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.delete("/v2.2/gateways/1").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.get("/v2.2/gateways/1/numbers").mock(
        return_value=httpx.Response(200, json=env([]))
    )

    client.gateways.list()
    client.gateways.add(GatewayAddRequest(gateway="1.2.3.4"))
    client.gateways.get(1)
    client.gateways.update(1, GatewayUpdateRequest(prefix="9"))
    client.gateways.remove(1)
    client.gateways.numbers(1)


# ----------------------------------------------------------- Lookups ---


def test_lookups(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/cnam/2015551234").mock(
        return_value=httpx.Response(200, json=env({"name": "x"}))
    )
    mock_router.get("/v2.2/lrn/2015551234/2012548000").mock(
        return_value=httpx.Response(200, json=env({"lrn": "y"}))
    )
    assert client.lookups.cnam("2015551234") == {"name": "x"}
    assert client.lookups.lrn("2015551234", "2012548000") == {"lrn": "y"}


# --------------------------------------------------------- Messaging ---


def test_messaging_full_surface(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/messages").mock(return_value=httpx.Response(200, json=env([])))
    mock_router.post("/v2.2/messages").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.post("/v2.2/messaging/brands").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.get("/v2.2/messaging/campaigns").mock(
        return_value=httpx.Response(200, json=env([]))
    )
    mock_router.post("/v2.2/messaging/campaigns").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.get("/v2.2/numbers/messaging").mock(
        return_value=httpx.Response(200, json=env([]))
    )

    client.messaging.history(number="2015551234")
    client.messaging.send(
        MessageSendRequest.model_validate(
            {"from": "2012548000", "to": "2015551234", "text": "hi"}
        )
    )
    client.messaging.brands(
        MessagingBrandCreateRequest(messagingBrandId="BABC123", messagingBrandName="X")
    )
    client.messaging.campaign_status()
    client.messaging.campaign_create(
        MessagingCampaignCreateRequest(
            messagingBrandId="B1", externalCampaignId="C1", campaignDescription="d"
        )
    )
    client.messaging.numbers_state(numbers=["2015551234", "2015551235"])


def test_messaging_numbers_state_no_args(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/numbers/messaging").mock(
        return_value=httpx.Response(200, json=env([]))
    )
    client.messaging.numbers_state()


# ----------------------------------------------------------- Numbers ---


@pytest.mark.parametrize(
    ("call", "method", "path"),
    [
        (lambda c: c.numbers.list(), "GET", "/v2.2/numbers"),
        (lambda c: c.numbers.get("2015551234"), "GET", "/v2.2/numbers/2015551234"),
        (lambda c: c.numbers.remove("2015551234"), "DELETE", "/v2.2/numbers/2015551234"),
        (lambda c: c.numbers.release("2015551234"), "POST", "/v2.2/numbers/2015551234/release"),
        (lambda c: c.numbers.get_fax("2015551234"), "GET", "/v2.2/numbers/2015551234/fax"),
        (
            lambda c: c.numbers.remove_fax("2015551234"),
            "DELETE",
            "/v2.2/numbers/2015551234/fax",
        ),
        (
            lambda c: c.numbers.remove_forward("2015551234"),
            "DELETE",
            "/v2.2/numbers/2015551234/forward",
        ),
        (lambda c: c.numbers.get_sms("2015551234"), "GET", "/v2.2/numbers/2015551234/sms"),
        (
            lambda c: c.numbers.remove_sms("2015551234"),
            "DELETE",
            "/v2.2/numbers/2015551234/sms",
        ),
        (
            lambda c: c.numbers.get_messaging("2015551234"),
            "GET",
            "/v2.2/numbers/2015551234/messaging",
        ),
        (
            lambda c: c.numbers.unassign_campaign("2015551234"),
            "DELETE",
            "/v2.2/numbers/2015551234/messaging-campaign",
        ),
        (
            lambda c: c.numbers.bulk_unassign_campaign(["2015551234"]),
            "DELETE",
            "/v2.2/numbers/messaging-campaign",
        ),
    ],
)
def test_numbers_simple_calls(
    client: Client, mock_router: respx.Router, call, method: str, path: str
) -> None:
    mock_router.route(method=method, url__regex=f".*{path}$").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    call(client)


def test_numbers_with_bodies(client: Client, mock_router: respx.Router) -> None:
    mock_router.post("/v2.2/numbers").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.patch("/v2.2/numbers/2015551234").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/numbers/2015551234/route").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/numbers/2015551234/translation").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/numbers/2015551234/cnam").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/numbers/2015551234/lidb").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/numbers/2015551234/fax").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/numbers/2015551234/forward").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/numbers/2015551234/sms").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.patch("/v2.2/numbers/2015551234/messaging").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/numbers/2015551234/messaging-campaign").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.patch("/v2.2/numbers/2015551234/port-out-pin").mock(
        return_value=httpx.Response(200, json=env({}))
    )

    client.numbers.add(NumberAddRequest(number=2015551234))
    client.numbers.move("2015551234", NumberMoveRequest(accountId=1, route=4))
    client.numbers.set_route("2015551234", NumberRouteRequest(route=1))
    client.numbers.set_translation(
        "2015551234", NumberTranslationRequest(translation="2015551235")
    )
    client.numbers.set_cnam("2015551234", NumberCnamRequest(enabled=True))
    client.numbers.set_lidb("2015551234", NumberLibdRequest(cnam="ACME"))
    client.numbers.set_fax("2015551234", NumberFaxRequest(email="f@x.com"))
    client.numbers.set_forward("2015551234", NumberForwardRequest(destination=2125551234))
    client.numbers.set_sms("2015551234", NumberSmsRequest(type="email", resource="x@y.com"))
    client.numbers.patch_messaging(
        "2015551234", NumberMessagingPatchRequest(routeIn=1, routeOut=2)
    )
    client.numbers.assign_campaign(
        "2015551234", NumberCampaignAssignRequest(campaignId="ABC123")
    )
    client.numbers.set_port_out_pin("2015551234", PortOutPinUpdateRequest(pin="1234"))


# ----------------------------------------------------------- Support ---


def test_support_full_surface(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/support/tickets").mock(
        return_value=httpx.Response(200, json=env([]))
    )
    mock_router.post("/v2.2/support/tickets").mock(
        return_value=httpx.Response(200, json=env({"id": 1}))
    )
    mock_router.get("/v2.2/support/tickets/1").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/support/tickets/1").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.delete("/v2.2/support/tickets/1").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.get("/v2.2/support/tickets/1/messages").mock(
        return_value=httpx.Response(200, json=env([]))
    )
    mock_router.post("/v2.2/support/tickets/1/replies").mock(
        return_value=httpx.Response(200, json=env({}))
    )

    client.support.list()
    client.support.create(TicketCreateRequest(subject="s", message="m"))
    client.support.get(1)
    client.support.update(1, TicketUpdateRequest(status="closed"))
    client.support.delete(1)
    client.support.messages(1)
    client.support.reply(1, TicketReplyRequest(message="ok"))


# --------------------------------------------------------- iNumbering ---


def test_inumbering_full_surface(client: Client, mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/inventory").mock(return_value=httpx.Response(200, json=env([])))
    mock_router.get("/v2.2/inventory/coverage").mock(
        return_value=httpx.Response(200, json=env([]))
    )
    mock_router.post("/v2.2/orders").mock(
        return_value=httpx.Response(200, json=env({"orderId": 1}))
    )
    mock_router.get("/v2.2/ports").mock(return_value=httpx.Response(200, json=env([])))
    mock_router.post("/v2.2/ports").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.get("/v2.2/ports/42").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.get("/v2.2/ports/availability/2015551234").mock(
        return_value=httpx.Response(200, json=env({}))
    )

    client.inumbering.search_inventory(state="NJ", limit=5)
    client.inumbering.coverage(state="NJ")
    client.inumbering.order(OrderCreateRequest(numbers=["2015551234"]))
    client.inumbering.ports()
    client.inumbering.port(42)
    client.inumbering.submit_port(
        PortSubmitRequest(
            lcAccountNumber="acct",
            streetNumber="550",
            street="Main",
            city="Chicago",
            state="IL",
        )
    )
    client.inumbering.port_availability("2015551234")


# ---------------------------------------------------- response unwrap ---


def test_unwrap_passes_through_non_envelope(client: Client, mock_router: respx.Router) -> None:
    # Some endpoints might return a bare list/dict — make sure unwrap doesn't choke.
    mock_router.get("/v2.2/cnam/2015551234").mock(
        return_value=httpx.Response(200, json=["bare", "list"])
    )
    assert client.lookups.cnam("2015551234") == ["bare", "list"]


# ------------------------------------------------------ async sanity ---


@pytest.mark.asyncio
async def test_async_client_e2e(mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/account").mock(
        return_value=httpx.Response(200, json=env({"id": 1}))
    )
    async with AsyncClient(api_key="k", base_url=BASE, max_retries=0) as c:
        assert await c.account.get() == {"id": 1}


@pytest.mark.asyncio
async def test_async_full_resource_surface(mock_router: respx.Router) -> None:
    """One call per async resource group, to drive coverage on the AsyncResource side."""
    mock_router.get("/v2.2/acl").mock(return_value=httpx.Response(200, json=env([])))
    mock_router.post("/v2.2/acl").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.delete("/v2.2/acl").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.get("/v2.2/auth").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.put("/v2.2/auth").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.get("/v2.2/e911").mock(return_value=httpx.Response(200, json=env([])))
    mock_router.post("/v2.2/e911").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.post("/v2.2/e911/validations").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.get("/v2.2/e911/2015551234").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/e911/2015551234").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.delete("/v2.2/e911/2015551234").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.get("/v2.2/gateways").mock(return_value=httpx.Response(200, json=env([])))
    mock_router.post("/v2.2/gateways").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.get("/v2.2/gateways/1").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.put("/v2.2/gateways/1").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.delete("/v2.2/gateways/1").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.get("/v2.2/gateways/1/numbers").mock(
        return_value=httpx.Response(200, json=env([]))
    )
    mock_router.get("/v2.2/cnam/2015551234").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.get("/v2.2/lrn/2015551234/2012548000").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.get("/v2.2/messages").mock(return_value=httpx.Response(200, json=env([])))
    mock_router.post("/v2.2/messages").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.post("/v2.2/messaging/brands").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.get("/v2.2/messaging/campaigns").mock(
        return_value=httpx.Response(200, json=env([]))
    )
    mock_router.post("/v2.2/messaging/campaigns").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.get("/v2.2/numbers/messaging").mock(
        return_value=httpx.Response(200, json=env([]))
    )
    mock_router.get("/v2.2/numbers").mock(return_value=httpx.Response(200, json=env([])))
    mock_router.post("/v2.2/numbers").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.get("/v2.2/numbers/2015551234").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.delete("/v2.2/numbers/2015551234").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.patch("/v2.2/numbers/2015551234").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.post("/v2.2/numbers/2015551234/release").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/numbers/2015551234/route").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/numbers/2015551234/translation").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/numbers/2015551234/cnam").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/numbers/2015551234/lidb").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.get("/v2.2/numbers/2015551234/fax").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/numbers/2015551234/fax").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.delete("/v2.2/numbers/2015551234/fax").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/numbers/2015551234/forward").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.delete("/v2.2/numbers/2015551234/forward").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.get("/v2.2/numbers/2015551234/sms").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/numbers/2015551234/sms").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.delete("/v2.2/numbers/2015551234/sms").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.get("/v2.2/numbers/2015551234/messaging").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.patch("/v2.2/numbers/2015551234/messaging").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/numbers/2015551234/messaging-campaign").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.delete("/v2.2/numbers/2015551234/messaging-campaign").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.delete("/v2.2/numbers/messaging-campaign").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.patch("/v2.2/numbers/2015551234/port-out-pin").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.get("/v2.2/account").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.put("/v2.2/account").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.post("/v2.2/account").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.post("/v2.2/accounts").mock(return_value=httpx.Response(200, json=env([])))
    mock_router.get("/v2.2/account/cdr").mock(return_value=httpx.Response(200, json=env([])))
    mock_router.get("/v2.2/account/credits").mock(
        return_value=httpx.Response(200, json=env([]))
    )
    mock_router.get("/v2.2/account/recurring-charges").mock(
        return_value=httpx.Response(200, json=env([]))
    )
    mock_router.get("/v2.2/account/payments").mock(
        return_value=httpx.Response(200, json=env([]))
    )
    mock_router.get("/v2.2/account/registration").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.post("/v2.2/account/recovery").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.get("/v2.2/support/tickets").mock(
        return_value=httpx.Response(200, json=env([]))
    )
    mock_router.post("/v2.2/support/tickets").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.get("/v2.2/support/tickets/1").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.put("/v2.2/support/tickets/1").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.delete("/v2.2/support/tickets/1").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.get("/v2.2/support/tickets/1/messages").mock(
        return_value=httpx.Response(200, json=env([]))
    )
    mock_router.post("/v2.2/support/tickets/1/replies").mock(
        return_value=httpx.Response(200, json=env({}))
    )
    mock_router.get("/v2.2/inventory").mock(return_value=httpx.Response(200, json=env([])))
    mock_router.get("/v2.2/inventory/coverage").mock(
        return_value=httpx.Response(200, json=env([]))
    )
    mock_router.post("/v2.2/orders").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.get("/v2.2/ports").mock(return_value=httpx.Response(200, json=env([])))
    mock_router.post("/v2.2/ports").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.get("/v2.2/ports/42").mock(return_value=httpx.Response(200, json=env({})))
    mock_router.get("/v2.2/ports/availability/2015551234").mock(
        return_value=httpx.Response(200, json=env({}))
    )

    async with AsyncClient(api_key="k", base_url=BASE, max_retries=0) as c:
        # ACL
        await c.acl.list()
        await c.acl.add(AclModifyRequest(acl=[CidrEntry(cidr="203.0.113.0/24")]))
        await c.acl.remove(AclModifyRequest(acl=[CidrEntry(cidr="203.0.113.0/24")]))
        # Auth
        await c.authentication.get()
        await c.authentication.update(AuthPutRequest(authType=1))
        # E911
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
        # Gateways
        await c.gateways.list()
        await c.gateways.add(GatewayAddRequest(gateway="1.2.3.4"))
        await c.gateways.get(1)
        await c.gateways.update(1, GatewayUpdateRequest(prefix="9"))
        await c.gateways.remove(1)
        await c.gateways.numbers(1)
        # Lookups
        await c.lookups.cnam("2015551234")
        await c.lookups.lrn("2015551234", "2012548000")
        # Messaging
        await c.messaging.history()
        await c.messaging.send(
            MessageSendRequest.model_validate(
                {"from": "2012548000", "to": "2015551234", "text": "hi"}
            )
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
        await c.messaging.numbers_state()  # no args branch
        # Numbers
        await c.numbers.list()
        await c.numbers.add(NumberAddRequest(number=2015551234))
        await c.numbers.get("2015551234")
        await c.numbers.remove("2015551234")
        await c.numbers.move("2015551234", NumberMoveRequest(accountId=1, route=4))
        await c.numbers.release("2015551234")
        await c.numbers.set_route("2015551234", NumberRouteRequest(route=1))
        await c.numbers.set_translation(
            "2015551234", NumberTranslationRequest(translation="2015551235")
        )
        await c.numbers.set_cnam("2015551234", NumberCnamRequest(enabled=True))
        await c.numbers.set_lidb("2015551234", NumberLibdRequest(cnam="ACME"))
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
            "2015551234", NumberMessagingPatchRequest(routeIn=1, routeOut=2)
        )
        await c.numbers.assign_campaign(
            "2015551234", NumberCampaignAssignRequest(campaignId="ABC123")
        )
        await c.numbers.unassign_campaign("2015551234")
        await c.numbers.bulk_unassign_campaign(["2015551234"])
        await c.numbers.set_port_out_pin("2015551234", PortOutPinUpdateRequest(pin="1234"))
        # Account
        await c.account.get()
        await c.account.update(AccountPutRequest(timezone="UTC"))
        await c.account.add(AccountAddRequest(username=1, name="x", email="x@y.com"))
        await c.account.list()
        await c.account.signup(AccountSignupRequest(name="x", email="x@y.com"))
        await c.account.cdr(start=0, end=0)
        await c.account.credits()
        await c.account.recurring_charges()
        await c.account.payments()
        await c.account.registration()
        await c.account.recover(AccountRecoverRequest(email="x@y.com"))
        # Support
        await c.support.list()
        await c.support.create(TicketCreateRequest(subject="s", message="m"))
        await c.support.get(1)
        await c.support.update(1, TicketUpdateRequest(status="closed"))
        await c.support.delete(1)
        await c.support.messages(1)
        await c.support.reply(1, TicketReplyRequest(message="ok"))
        # iNumbering
        await c.inumbering.search_inventory(state="NJ")
        await c.inumbering.coverage()
        await c.inumbering.order(OrderCreateRequest(numbers=["2015551234"]))
        await c.inumbering.ports()
        await c.inumbering.port(42)
        await c.inumbering.submit_port(
            PortSubmitRequest(
                lcAccountNumber="acct",
                streetNumber="550",
                street="Main",
                city="Chicago",
                state="IL",
            )
        )
        await c.inumbering.port_availability("2015551234")
