"""
Tests for execution module of NSX-T transport node profiles
"""
from unittest.mock import patch

import saltext.vmware.modules.nsxt_transport_node_profiles as nsxt_transport_node_profiles
from saltext.vmware.utils import nsxt_request

_mock_transport_node_profile = {
    "transport_zone_endpoints": [],
    "host_switch_spec": {
        "host_switches": [
            {
                "host_switch_name": "nvds1",
                "host_switch_id": "2664b483-6451-4503-82f3-3be639f3ea64",
                "host_switch_type": "NVDS",
                "host_switch_mode": "STANDARD",
                "host_switch_profile_ids": [
                    {
                        "key": "UplinkHostSwitchProfile",
                        "value": "6b31dd86-ae4d-46fb-a945-958e44e28566",
                    },
                    {"key": "NiocProfile", "value": "8cb3de94-2834-414c-b07d-c034d878db56"},
                    {
                        "key": "LldpHostSwitchProfile",
                        "value": "306c9a2a-7c3d-47f2-a1e1-0b27ce4c3914",
                    },
                ],
                "pnics": [],
                "is_migrate_pnics": "false",
                "ip_assignment_spec": {"resource_type": "AssignedByDhcp"},
                "cpu_config": [],
                "transport_zone_endpoints": [
                    {
                        "transport_zone_id": "7cca0aa6-8dbc-463e-a770-dea686656582",
                        "transport_zone_profile_ids": [
                            {
                                "resource_type": "BfdHealthMonitoringProfile",
                                "profile_id": "52035bb3-ab02-4a08-9884-18631312e50a",
                            }
                        ],
                    }
                ],
                "vmk_install_migration": [],
                "pnics_uninstall_migration": [],
                "vmk_uninstall_migration": [],
            }
        ],
        "resource_type": "StandardHostSwitchSpec",
    },
    "ignore_overridden_hosts": "false",
    "resource_type": "TransportNodeProfile",
    "id": "a068c2bd-ae9b-4454-bd9c-b3acc24a5fe3",
    "display_name": "Sample TNP",
    "description": "",
    "tags": [],
    "_revision": 0,
}


@patch.object(nsxt_request, "call_api")
def test_get(api_mock):
    response = {
        "results": [_mock_transport_node_profile],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    api_mock.return_value = response

    assert (
        nsxt_transport_node_profiles.get(
            hostname="hostname",
            username="username",
            password="pass",
            verify_ssl=False,
        )
        == response
    )


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name(api_mock):
    response = {
        "results": [_mock_transport_node_profile],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    api_mock.return_value = response
    assert (
        nsxt_transport_node_profiles.get_by_display_name(
            hostname="hostname",
            username="username",
            password="pass",
            verify_ssl=False,
            display_name=_mock_transport_node_profile["display_name"],
        )
        == {"results": [_mock_transport_node_profile]}
    )


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name_with_error_response(api_mock):
    response = {"error": "Http error occurred."}
    api_mock.return_value = response
    assert (
        nsxt_transport_node_profiles.get_by_display_name(
            hostname="hostname",
            username="username",
            password="pass",
            display_name=_mock_transport_node_profile["display_name"],
            verify_ssl=False,
        )
        == response
    )


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name_paginated(api_mock):
    response_with_cursor = {
        "results": [_mock_transport_node_profile],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
        "cursor": "cursor_1",
    }
    transport_node_profile_page_2 = _mock_transport_node_profile.copy()
    transport_node_profile_page_2["display_name"] = "new display name"
    response_without_cursor = {
        "results": [transport_node_profile_page_2],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    api_mock.side_effect = [response_with_cursor, response_without_cursor]
    assert (
        nsxt_transport_node_profiles.get_by_display_name(
            hostname="hostname",
            username="username",
            password="pass",
            display_name=_mock_transport_node_profile["display_name"],
            verify_ssl=False,
        )
        == {"results": [_mock_transport_node_profile]}
    )


@patch.object(nsxt_request, "call_api")
def test_create(api_mock):
    api_mock.return_value = _mock_transport_node_profile
    assert (
        nsxt_transport_node_profiles.create(
            hostname="hostname",
            username="username",
            password="pass",
            verify_ssl=False,
            display_name=_mock_transport_node_profile["display_name"],
            host_switch_spec=_mock_transport_node_profile["host_switch_spec"],
            description=_mock_transport_node_profile["description"],
        )
        == _mock_transport_node_profile
    )


@patch.object(nsxt_request, "call_api")
def test_update(api_mock):
    api_mock.return_value = _mock_transport_node_profile
    assert (
        nsxt_transport_node_profiles.update(
            hostname="hostname",
            username="username",
            password="pass",
            verify_ssl=False,
            display_name=_mock_transport_node_profile["display_name"],
            host_switch_spec=_mock_transport_node_profile["host_switch_spec"],
            description=_mock_transport_node_profile["description"],
            revision=_mock_transport_node_profile["_revision"] - 1,
            transport_node_profile_id=_mock_transport_node_profile["id"],
        )
        == _mock_transport_node_profile
    )


@patch.object(nsxt_request, "call_api")
def test_delete(api_mock):
    result = {"message": "Deleted transport node profile successfully"}
    api_mock.return_value = result
    assert (
        nsxt_transport_node_profiles.delete(
            hostname="hostname",
            username="username",
            password="pass",
            verify_ssl=False,
            transport_node_profile_id=_mock_transport_node_profile["id"],
        )
        == result
    )


@patch.object(nsxt_request, "call_api")
def test_delete_with_error(api_mock):
    result = {"error": "Http error occurred."}
    api_mock.return_value = result
    assert (
        nsxt_transport_node_profiles.delete(
            hostname="hostname",
            username="username",
            password="pass",
            verify_ssl=False,
            transport_node_profile_id=_mock_transport_node_profile["id"],
        )
        == result
    )
