from __future__ import annotations

import pytest
from pydantic import ValidationError

from voicetel.models import (
    AclModifyRequest,
    CidrEntry,
    GatewayAddRequest,
    MessageSendRequest,
    NumberAddRequest,
    NumberCampaignAssignRequest,
    OrderCreateRequest,
    PortFeature,
    PortFeatureRouting,
    PortOutPinUpdateRequest,
    PortSubmitRequest,
)


def test_to_payload_omits_unset_fields() -> None:
    req = NumberAddRequest(number=2015551234)
    assert req.to_payload() == {"number": 2015551234}


def test_to_payload_includes_explicitly_none_fields_but_not_unset() -> None:
    req = GatewayAddRequest(gateway="1.2.3.4", prefix="9")
    payload = req.to_payload()
    assert payload == {"gateway": "1.2.3.4", "prefix": "9"}


def test_message_send_request_aliases_from() -> None:
    msg = MessageSendRequest.model_validate(
        {"from": "2012548000", "to": "2015551234", "text": "hi"}
    )
    payload = msg.to_payload()
    assert payload["from"] == "2012548000"
    assert "from_" not in payload


def test_phone_number_pattern_enforced() -> None:
    with pytest.raises(ValidationError):
        MessageSendRequest.model_validate({"from": "short", "to": "2015551234", "text": "x"})


def test_campaign_id_pattern_enforced() -> None:
    NumberCampaignAssignRequest(campaignId="ABC123")
    with pytest.raises(ValidationError):
        NumberCampaignAssignRequest(campaignId="lowercase")


def test_pin_pattern_enforced() -> None:
    PortOutPinUpdateRequest(pin="1234")
    with pytest.raises(ValidationError):
        PortOutPinUpdateRequest(pin="12")
    with pytest.raises(ValidationError):
        PortOutPinUpdateRequest(pin="abcd")


def test_acl_modify_request_nested() -> None:
    req = AclModifyRequest(acl=[CidrEntry(cidr="203.0.113.0/24")])
    payload = req.to_payload()
    assert payload == {"acl": [{"cidr": "203.0.113.0/24"}]}


def test_order_accepts_string_or_object_numbers() -> None:
    req = OrderCreateRequest.model_validate(
        {"numbers": ["2015551234", {"number": "2015551235", "route": 4}]}
    )
    payload = req.to_payload()
    assert payload["numbers"][0] == "2015551234"
    assert payload["numbers"][1] == {"number": "2015551235", "route": 4}


def test_order_max_100() -> None:
    with pytest.raises(ValidationError):
        OrderCreateRequest(numbers=["2015551234"] * 101)


def test_order_min_1() -> None:
    with pytest.raises(ValidationError):
        OrderCreateRequest(numbers=[])


def test_port_submit_with_features() -> None:
    req = PortSubmitRequest(
        lcAccountNumber="acct-1",
        streetNumber="550",
        street="Main",
        city="Chicago",
        state="IL",
        features=[
            PortFeature(
                number="2015551234",
                routing=PortFeatureRouting(gatewayId=4),
            )
        ],
    )
    payload = req.to_payload()
    assert payload["features"][0]["routing"] == {"gatewayId": 4}


def test_gateway_limit_bounds() -> None:
    GatewayAddRequest(gateway="x", limit=1)
    GatewayAddRequest(gateway="x", limit=1000)
    with pytest.raises(ValidationError):
        GatewayAddRequest(gateway="x", limit=0)
    with pytest.raises(ValidationError):
        GatewayAddRequest(gateway="x", limit=1001)


def test_models_allow_extra_fields_in() -> None:
    # Server might add fields; we should not reject them on the way in.
    NumberAddRequest.model_validate({"number": 2015551234, "future_field": "ok"})
