"""Wire-shape tests for the v2.2.20 additions, asserted against the v2.2 spec.

Covers:
- GET/PUT/DELETE /v2.2/numbers/{number}/directory-listing (202 on writes)
- GET /v2.2/carrier/{number}
- e911 addressid is a string on the wire
- POST /v2.2/orders 201 includes routes: [{number, route}]
- POST /v2.2/messages without text (media-only MMS)
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest
import respx

from voicetel import AsyncClient, Client
from voicetel.models import (
    CarrierData,
    DirectoryListingData,
    DirectoryListingRequest,
    E911AddressRequest,
    E911ProvisionByIdRequest,
    MessageSendRequest,
    OrderCreateData,
)

from .test_resources import BASE, env

LISTING = {
    "type": "B",
    "name": "Acme Corp",
    "streetNumber": "100",
    "streetName": "Broadway",
    "streetType": "St",
    "streetSuffix": "",
    "location": "Suite 900",
    "city": "New York",
    "state": "NY",
    "zip": "10005",
    "complex": False,
}


def test_directory_listing_get(client: Client, mock_router: respx.Router) -> None:
    route = mock_router.get("/v2.2/numbers/2015550123/directory-listing").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "number": "2015550123",
                    "status": "listed",
                    "eligible": True,
                    "listing": LISTING,
                    "pending": None,
                }
            ),
        )
    )
    result = client.numbers.get_directory_listing("2015550123")
    assert isinstance(result, DirectoryListingData)
    assert result.status == "listed"
    assert result.eligible is True
    assert result.listing is not None and result.listing.name == "Acme Corp"
    assert result.listing.complex is False
    assert result.pending is None
    assert route.called


def test_directory_listing_put(client: Client, mock_router: respx.Router) -> None:
    route = mock_router.put("/v2.2/numbers/2015550123/directory-listing").mock(
        return_value=httpx.Response(
            202,
            json=env(
                {
                    "number": "2015550123",
                    "status": "pending",
                    "orderId": "1026472",
                    "listing": {k: v for k, v in LISTING.items() if k != "complex"},
                }
            ),
        )
    )
    result = client.numbers.set_directory_listing(
        "2015550123",
        DirectoryListingRequest(
            type="business",
            name="Acme Corp",
            streetNumber="100",
            streetName="Broadway",
            streetType="St",
            location="Suite 900",
            city="New York",
            state="NY",
            zip="10005",
        ),
    )
    assert result.status == "pending"
    assert result.orderId == "1026472"
    sent = json_body(route)
    assert sent["type"] == "business"
    assert sent["city"] == "New York"
    # only fields the caller set are emitted
    assert "firstName" not in sent and "complex" not in sent


def test_directory_listing_delete(client: Client, mock_router: respx.Router) -> None:
    route = mock_router.delete("/v2.2/numbers/2015550123/directory-listing").mock(
        return_value=httpx.Response(
            202, json=env({"number": "2015550123", "status": "removing", "orderId": "1026473"})
        )
    )
    result = client.numbers.remove_directory_listing("2015550123")
    assert result.status == "removing"
    assert result.orderId == "1026473"
    assert route.called


def test_directory_listing_cancel_returns_not_listed(
    client: Client, mock_router: respx.Router
) -> None:
    mock_router.delete("/v2.2/numbers/2015550123/directory-listing").mock(
        return_value=httpx.Response(202, json=env({"number": "2015550123", "status": "not_listed"}))
    )
    result = client.numbers.remove_directory_listing("2015550123")
    assert result.status == "not_listed"
    assert result.orderId is None


def test_directory_listing_residence_request(client: Client, mock_router: respx.Router) -> None:
    route = mock_router.put("/v2.2/numbers/2015550123/directory-listing").mock(
        return_value=httpx.Response(
            202, json=env({"number": "2015550123", "status": "pending", "orderId": "1026474"})
        )
    )
    client.numbers.set_directory_listing(
        "2015550123",
        DirectoryListingRequest(
            type="residence",
            firstName="Jane",
            lastName="Doe",
            city="New York",
            state="NY",
            zip="10005-1234",
        ),
    )
    sent = json_body(route)
    assert sent["type"] == "residence"
    assert sent["firstName"] == "Jane" and sent["lastName"] == "Doe"


@pytest.mark.parametrize(
    "bad",
    [
        {"type": "business", "city": "New York", "state": "ZZ", "zip": "10005"},
        {"type": "business", "city": "New York", "state": "NY", "zip": "1000"},
        {"type": "business", "name": "Acme Corp", "city": "New York", "state": "NY"},
        {"type": "business", "name": "Acme <Corp>", "city": "New York", "state": "NY", "zip": "10005"},
    ],
)
def test_directory_listing_request_rejects_invalid(bad: dict[str, Any]) -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        DirectoryListingRequest.model_validate(bad)


def test_lookups_carrier(client: Client, mock_router: respx.Router) -> None:
    route = mock_router.get("/v2.2/carrier/2015550123").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "number": "2015550123",
                    "carrier": {
                        "name": "EXAMPLE CARRIER",
                        "type": "voip",
                        "mobile_country_code": None,
                        "mobile_network_code": None,
                        "error_code": None,
                    },
                }
            ),
        )
    )
    result = client.lookups.carrier("2015550123")
    assert isinstance(result, CarrierData)
    assert result.carrier.name == "EXAMPLE CARRIER"
    assert result.carrier.type == "voip"
    assert result.carrier.mobile_country_code is None
    assert route.called


def test_e911_addressid_is_a_string(client: Client, mock_router: respx.Router) -> None:
    """v2.2.20: the validated-address id is a hex string, not an integer."""
    mock_router.post("/v2.2/e911/validations").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "address": {
                        "addressid": "123a45b678c9d012e3f45a67b890c123",
                        "address1": "100 Broadway",
                        "city": "New York",
                        "state": "NY",
                        "zip": "10005",
                    }
                }
            ),
        )
    )
    validated = client.e911.validate(
        E911AddressRequest(address1="100 Broadway", city="New York", state="NY", zip="10005")
    )
    assert validated.address.addressid == "123a45b678c9d012e3f45a67b890c123"

    route = mock_router.put("/v2.2/e911/2015550123").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "record": {
                        "dn": "12015550123",
                        "callername": "Acme",
                        "address1": "100 Broadway",
                        "city": "New York",
                        "state": "NY",
                        "zip": "10005",
                    }
                }
            ),
        )
    )
    client.e911.provision(
        "2015550123",
        E911ProvisionByIdRequest(
            callername="Acme", addressid=validated.address.addressid
        ),
    )
    assert json_body(route)["addressid"] == "123a45b678c9d012e3f45a67b890c123"


def test_orders_201_includes_routes(client: Client, mock_router: respx.Router) -> None:
    mock_router.post("/v2.2/orders").mock(
        return_value=httpx.Response(
            201,
            json=env(
                {
                    "orderId": "ORD-1",
                    "amountCharged": 1.0,
                    "numbersOrdered": ["2015550100"],
                    "failed": [],
                    "routes": [{"number": "2015550100", "route": 4}],
                }
            ),
        )
    )
    from voicetel.models import OrderCreateRequest

    result = client.inumbering.order(
        OrderCreateRequest(numbers=["2015550100"])
    )
    assert isinstance(result, OrderCreateData)
    assert result.routes[0].number == "2015550100"
    assert result.routes[0].route == 4


def test_message_send_media_only_mms(client: Client, mock_router: respx.Router) -> None:
    """v2.2.20: text is optional (media-only MMS); subject is deprecated but accepted."""
    route = mock_router.post("/v2.2/messages").mock(
        return_value=httpx.Response(
            202,
            json=env(
                {
                    "id": "m-1",
                    "fromNumber": "2015550123",
                    "toNumber": "2015550100",
                    "type": "mms",
                    "parts": 1,
                }
            ),
        )
    )
    client.messaging.send(
        MessageSendRequest(
            fromNumber="2015550123",
            toNumber="2015550100",
            mediaUrls=["https://example.com/photo.jpg"],
        )
    )
    sent = json_body(route)
    assert "text" not in sent
    assert sent["mediaUrls"] == ["https://example.com/photo.jpg"]


@pytest.mark.asyncio
async def test_directory_listing_async(mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/numbers/2015550123/directory-listing").mock(
        return_value=httpx.Response(
            200, json=env({"number": "2015550123", "status": "unavailable", "eligible": False})
        )
    )
    async with AsyncClient(api_key="a" * 32, base_url=BASE, max_retries=0) as c:
        result = await c.numbers.get_directory_listing("2015550123")
    assert result.status == "unavailable"
    assert result.eligible is False
    assert result.listing is None


def json_body(route: respx.Route) -> dict[str, Any]:
    import json as _json

    assert route.calls.last.request.content
    return _json.loads(route.calls.last.request.content)
