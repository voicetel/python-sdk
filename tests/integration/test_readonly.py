"""Live read-only checks against api.voicetel.com.

Strict rules in this file:
- No state mutations. No POST/PUT/PATCH/DELETE.
- ``account/cdr``, ``account/recurring_charges``, ``account/payments``, and ``account/registration``
  count against the 6 req/hour/IP rate limit shared with ``api-key`` — we exercise them lightly.
- Lookups (CNAM/LRN) cost money per call; we hit each at most once.
"""

from __future__ import annotations

from voicetel import Client
from voicetel.models.account import AccountData, AccountRegistrationData
from voicetel.models.acl import AclListData
from voicetel.models.authentication import AuthGetData
from voicetel.models.e911 import E911AllData
from voicetel.models.gateways import GatewaysListData
from voicetel.models.inumbering import InventoryCoverageData, PortListData
from voicetel.models.messaging import MessagingCampaignStatusData
from voicetel.models.numbers import NumbersListData
from voicetel.models.support import TicketsListData


def test_account_get_returns_envelope_data(client: Client) -> None:
    me = client.account.get()
    assert isinstance(me, AccountData)


def test_numbers_list_is_iterable(client: Client) -> None:
    numbers = client.numbers.list()
    assert isinstance(numbers, NumbersListData)


def test_gateways_list_is_iterable(client: Client) -> None:
    gw = client.gateways.list()
    assert isinstance(gw, GatewaysListData)


def test_acl_list_is_iterable(client: Client) -> None:
    acl = client.acl.list()
    assert isinstance(acl, AclListData)


def test_e911_list_is_iterable(client: Client) -> None:
    records = client.e911.list()
    assert isinstance(records, E911AllData)


def test_support_tickets_list_is_iterable(client: Client) -> None:
    tickets = client.support.list()
    assert isinstance(tickets, TicketsListData)


def test_inventory_coverage_is_iterable(client: Client) -> None:
    coverage = client.inumbering.coverage()
    assert isinstance(coverage, InventoryCoverageData)


def test_ports_list_is_iterable(client: Client) -> None:
    ports = client.inumbering.ports()
    assert isinstance(ports, PortListData)


def test_authentication_get_returns_dict(client: Client) -> None:
    auth = client.authentication.get()
    assert isinstance(auth, AuthGetData)


def test_messaging_campaign_status_is_iterable(client: Client) -> None:
    campaigns = client.messaging.campaign_status()
    assert isinstance(campaigns, MessagingCampaignStatusData)


# --- Rate-limited (6/hr/IP). Run sparingly; CI should gate these behind a separate marker. ---


def test_account_registration(client: Client) -> None:
    reg = client.account.registration()
    assert isinstance(reg, AccountRegistrationData)
