"""
Tests for execution module of NSX-T uplink profiles
"""

from unittest.mock import patch

import saltext.vmware.modules.nsxt_uplink_profiles as nsxt_uplink_profiles
from saltext.vmware.utils import nsxt_request

_mock_uplink_profile = {
    "lags": [
        {
            "name": "lag-1",
            "id": "33497",
            "mode": "ACTIVE",
            "load_balance_algorithm": "SRCDESTIPVLAN",
            "number_of_uplinks": 2,
            "uplinks": [
                {"uplink_name": "lag-1-0", "uplink_type": "PNIC"},
                {"uplink_name": "lag-1-1", "uplink_type": "PNIC"},
            ],
            "timeout_type": "SLOW",
        }
    ],
    "teaming": {
        "policy": "LOADBALANCE_SRC_MAC",
        "active_list": [{"uplink_name": "uplink-1", "uplink_type": "PNIC"}],
    },
    "named_teamings": [],
    "transport_vlan": 0,
    "overlay_encap": "GENEVE",
    "mtu": 1600,
    "resource_type": "UplinkHostSwitchProfile",
    "id": "d3804574-de10-4b2f-b92b-a5a29def128b",
    "display_name": "Sample_uplink_profile",
    "description": "",
    "tags": [],
    "_create_user": "admin",
    "_create_time": 1616998460566,
    "_last_modified_user": "admin",
    "_last_modified_time": 1616999479405,
    "_protection": "NOT_PROTECTED",
    "_revision": 1,
}


@patch.object(nsxt_request, "call_api")
def test_get(api_mock):
    response = {
        "results": [_mock_uplink_profile],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    api_mock.return_value = response

    assert (
        nsxt_uplink_profiles.get(
            hostname="hostname",
            username="username",
            password="pass",
            verify_ssl=False,
            hostswitch_profile_type="UplinkHostSwitchProfile",
        )
        == response
    )


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name(api_mock):
    response = {
        "results": [_mock_uplink_profile],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    api_mock.return_value = response
    assert nsxt_uplink_profiles.get_by_display_name(
        hostname="hostname",
        username="username",
        password="pass",
        display_name=_mock_uplink_profile["display_name"],
        verify_ssl=False,
    ) == {"results": [_mock_uplink_profile]}


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name_with_error_response(api_mock):
    response = {"error": "Http error occurred."}
    api_mock.return_value = response
    assert (
        nsxt_uplink_profiles.get_by_display_name(
            hostname="hostname",
            username="username",
            password="pass",
            display_name=_mock_uplink_profile["display_name"],
            verify_ssl=False,
        )
        == response
    )


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name_paginated(api_mock):
    response_with_cursor = {
        "results": [_mock_uplink_profile],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
        "cursor": "cursor_1",
    }
    uplink_profile_page_2 = _mock_uplink_profile.copy()
    uplink_profile_page_2["display_name"] = "new display name"
    response_without_cursor = {
        "results": [uplink_profile_page_2],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    api_mock.side_effect = [response_with_cursor, response_without_cursor]
    assert nsxt_uplink_profiles.get_by_display_name(
        hostname="hostname",
        username="username",
        password="pass",
        display_name=_mock_uplink_profile["display_name"],
        verify_ssl=False,
    ) == {"results": [_mock_uplink_profile]}


@patch.object(nsxt_request, "call_api")
def test_create(api_mock):
    api_mock.return_value = _mock_uplink_profile
    assert (
        nsxt_uplink_profiles.create(
            hostname="hostname",
            username="username",
            password="pass",
            display_name=_mock_uplink_profile["display_name"],
            teaming=_mock_uplink_profile["teaming"],
            named_teamings=_mock_uplink_profile["named_teamings"],
            mtu=_mock_uplink_profile["mtu"],
            verify_ssl=False,
        )
        == _mock_uplink_profile
    )


@patch.object(nsxt_request, "call_api")
def test_update(api_mock):
    api_mock.return_value = _mock_uplink_profile
    assert (
        nsxt_uplink_profiles.update(
            hostname="hostname",
            username="username",
            password="pass",
            verify_ssl=False,
            display_name=_mock_uplink_profile["display_name"],
            teaming=_mock_uplink_profile["teaming"],
            named_teamings=_mock_uplink_profile["named_teamings"],
            mtu=_mock_uplink_profile["mtu"],
            revision=_mock_uplink_profile["_revision"] - 1,
            uplink_profile_id=_mock_uplink_profile["id"],
        )
        == _mock_uplink_profile
    )


@patch.object(nsxt_request, "call_api")
def test_delete(api_mock):
    result = {"message": "Deleted uplink profile successfully"}
    api_mock.return_value = result
    assert (
        nsxt_uplink_profiles.delete(
            hostname="hostname",
            username="username",
            password="pass",
            verify_ssl=False,
            uplink_profile_id=_mock_uplink_profile["id"],
        )
        == result
    )


@patch.object(nsxt_request, "call_api")
def test_delete_with_error(api_mock):
    result = {"error": "Http error occurred."}
    api_mock.return_value = result
    assert (
        nsxt_uplink_profiles.delete(
            hostname="hostname",
            username="username",
            password="pass",
            verify_ssl=False,
            uplink_profile_id=_mock_uplink_profile["id"],
        )
        == result
    )
