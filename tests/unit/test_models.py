from __future__ import annotations

import pytest
from pydantic import ValidationError

from voicetel.models import (
    AccountAddRequest,
    AclModifyRequest,
    CidrEntry,
    GatewayAddRequest,
    MessageSendRequest,
    NumberAddRequest,
    NumberCampaignAssignRequest,
    NumberLidbRequest,
    OrderCreateRequest,
    PortFeature,
    PortFeatureRouting,
    PortOutPinUpdateRequest,
    PortSubmitRequest,
    SupportConversation,
)

# ----------------------------------------------------------- to_payload ---


def test_to_payload_omits_unset_fields() -> None:
    req = NumberAddRequest(number="2015551234")
    assert req.to_payload() == {"number": "2015551234"}


def test_to_payload_includes_explicitly_set_fields() -> None:
    req = GatewayAddRequest(gateway="1.2.3.4", prefix="9")
    assert req.to_payload() == {"gateway": "1.2.3.4", "prefix": "9"}


def test_to_payload_excludes_unset_optional_fields() -> None:
    req = AccountAddRequest(username=1234567890, name="Acme", email="x@y.com")
    payload = req.to_payload()
    assert "masterAccount" not in payload
    assert payload == {"username": 1234567890, "name": "Acme", "email": "x@y.com"}


# ---------------------------------------- wire-field name conventions ---


def test_message_send_request_uses_from_number_and_to_number() -> None:
    """``from``/``to`` are reserved-word collisions; the spec uses ``fromNumber``/``toNumber``.

    Our model uses those field names directly — no Pydantic alias needed.
    """
    msg = MessageSendRequest(fromNumber="2012548000", toNumber="2015551234", text="hi")
    payload = msg.to_payload()
    assert payload == {"fromNumber": "2012548000", "toNumber": "2015551234", "text": "hi"}
    assert "from" not in payload and "to" not in payload


def test_lidb_request_is_correctly_spelled() -> None:
    """LIDB = Line Information Database — verify the spelling is `Lidb` (the operationId
    and schema name; earlier spec drafts had the typo `Libd`)."""
    req = NumberLidbRequest(cnam="ACME CORP")
    assert req.to_payload() == {"cnam": "ACME CORP"}


# --------------------------------------------------- pattern enforcement ---


def test_phone_number_pattern_enforced_on_message_send() -> None:
    with pytest.raises(ValidationError):
        MessageSendRequest(fromNumber="short", toNumber="2015551234", text="x")
    with pytest.raises(ValidationError):
        MessageSendRequest(fromNumber="2012548000", toNumber="123", text="x")


def test_campaign_id_pattern_enforced() -> None:
    NumberCampaignAssignRequest(campaignId="ABC123")
    with pytest.raises(ValidationError):
        NumberCampaignAssignRequest(campaignId="lowercase")


def test_pin_pattern_enforced() -> None:
    PortOutPinUpdateRequest(pin="1234")
    with pytest.raises(ValidationError):
        PortOutPinUpdateRequest(pin="12")  # too short
    with pytest.raises(ValidationError):
        PortOutPinUpdateRequest(pin="abcd")  # not digits


# --------------------------------------------------------- nesting ---


def test_acl_modify_request_nested() -> None:
    req = AclModifyRequest(acl=[CidrEntry(cidr="203.0.113.0/24")])
    assert req.to_payload() == {"acl": [{"cidr": "203.0.113.0/24"}]}


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
        did=["2015551234"],
        name="Acme Corp",
        nameType="business",
        lcBtn="2015551000",
        lcAccountNumber="acct-1",
        streetNumber="550",
        street="Main",
        streetType="ST",
        city="Chicago",
        state="IL",
        zip="60601",
        country="US",
        authPerson="Jane Smith",
        features=[
            PortFeature(
                number="2015551234",
                routing=PortFeatureRouting(gatewayId=4),
            )
        ],
    )
    payload = req.to_payload()
    assert payload["features"][0]["routing"] == {"gatewayId": 4}


# --------------------------------------------------------- bounds ---


def test_gateway_limit_bounds() -> None:
    GatewayAddRequest(gateway="x", limit=1)
    GatewayAddRequest(gateway="x", limit=1000)
    with pytest.raises(ValidationError):
        GatewayAddRequest(gateway="x", limit=0)
    with pytest.raises(ValidationError):
        GatewayAddRequest(gateway="x", limit=1001)


# ------------------------------------------- extra fields tolerated in ---


def test_models_allow_extra_fields_in() -> None:
    """Server may add new fields; we shouldn't reject them."""
    NumberAddRequest.model_validate({"number": "2015551234", "future_field": "ok"})


# ----------------------------------------- supportConversation alias ---


def test_support_conversation_number_aliased_to_ticket_number() -> None:
    """`number` in the spec is the ticket sequence number (e.g. 1015), not a phone TN.
    We expose it as `ticket_number` to avoid confusion with phone-number fields."""
    c = SupportConversation.model_validate({"status": "active", "number": 1015, "id": 99})
    assert c.ticket_number == 1015
    assert c.id == 99
    # Round-trip preserves the wire-format field name.
    payload = c.model_dump(by_alias=True, exclude_unset=True)
    assert payload["number"] == 1015
    assert "ticket_number" not in payload
