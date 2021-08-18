"""
    Tests for nsxt_transport_zone modules
"""
import logging
from unittest.mock import patch

from saltext.vmware.modules import nsxt_transport_zone
from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)

_mock_transport_zones = {
    "results": [
        {
            "transport_type": "OVERLAY",
            "host_switch_name": "nsxDefaultHostSwitch",
            "host_switch_id": "0d6411e2-8c82-4e37-9fca-7082e2bff4c1",
            "transport_zone_profile_ids": [
                {
                    "resource_type": "BfdHealthMonitoringProfile",
                    "profile_id": "52035bb3-ab02-4a08-9884-18631312e50a",
                }
            ],
            "host_switch_mode": "STANDARD",
            "nested_nsx": False,
            "is_default": False,
            "resource_type": "TransportZone",
            "id": "980fdc81-6d34-4396-8a4a-889c70f0a9c4",
            "display_name": "Check-New-Transport-Zone-edit-edit-test2",
            "_create_user": "admin",
            "_create_time": 1616590912873,
            "_last_modified_user": "admin",
            "_last_modified_time": 1617198791225,
            "_system_owned": False,
            "_protection": "NOT_PROTECTED",
            "_revision": 4,
            "_schema": "/v1/schema/TransportZone",
        },
        {
            "transport_type": "OVERLAY",
            "host_switch_name": "nsxDefaultHostSwitch",
            "host_switch_id": "0d6411e2-8c82-4e37-9fca-7082e2bff4c1",
            "transport_zone_profile_ids": [
                {
                    "resource_type": "BfdHealthMonitoringProfile",
                    "profile_id": "52035bb3-ab02-4a08-9884-18631312e50a",
                }
            ],
            "host_switch_mode": "STANDARD",
            "nested_nsx": False,
            "is_default": False,
            "resource_type": "TransportZone",
            "id": "b68c4c9e-fc51-413d-81fd-aadd28f8526a",
            "display_name": "Transport-Zone-101",
            "_create_user": "admin",
            "_create_time": 1617088301924,
            "_last_modified_user": "admin",
            "_last_modified_time": 1617088301924,
            "_system_owned": False,
            "_protection": "NOT_PROTECTED",
            "_revision": 0,
            "_schema": "/v1/schema/TransportZone",
        },
    ]
}

_mock_transport_zones_by_display_name = {
    "results": [
        {
            "transport_type": "OVERLAY",
            "host_switch_name": "nsxDefaultHostSwitch",
            "host_switch_id": "0d6411e2-8c82-4e37-9fca-7082e2bff4c1",
            "transport_zone_profile_ids": [
                {
                    "resource_type": "BfdHealthMonitoringProfile",
                    "profile_id": "52035bb3-ab02-4a08-9884-18631312e50a",
                }
            ],
            "host_switch_mode": "STANDARD",
            "nested_nsx": False,
            "is_default": False,
            "resource_type": "TransportZone",
            "id": "980fdc81-6d34-4396-8a4a-889c70f0a9c4",
            "display_name": "Create-Transport-Zone",
            "_create_user": "admin",
            "_create_time": 1616590912873,
            "_last_modified_user": "admin",
            "_last_modified_time": 1617198791225,
            "_system_owned": False,
            "_protection": "NOT_PROTECTED",
            "_revision": 4,
            "_schema": "/v1/schema/TransportZone",
        }
    ]
}

_mock_create_response = {
    "transport_type": "OVERLAY",
    "host_switch_name": "nsxDefaultHostSwitch",
    "host_switch_id": "0d6411e2-8c82-4e37-9fca-7082e2bff4c1",
    "transport_zone_profile_ids": [
        {
            "resource_type": "BfdHealthMonitoringProfile",
            "profile_id": "52035bb3-ab02-4a08-9884-18631312e50a",
        }
    ],
    "host_switch_mode": "STANDARD",
    "nested_nsx": False,
    "is_default": False,
    "resource_type": "TransportZone",
    "id": "7779df74-a1b4-4804-bbcc-316b7195cd53",
    "display_name": "Create-Transport-Zone",
}

_mock_update_response = {
    "transport_type": "OVERLAY",
    "host_switch_name": "nsxDefaultHostSwitch",
    "host_switch_id": "0d6411e2-8c82-4e37-9fca-7082e2bff4c1",
    "transport_zone_profile_ids": [
        {
            "resource_type": "BfdHealthMonitoringProfile",
            "profile_id": "52035bb3-ab02-4a08-9884-18631312e50a",
        }
    ],
    "host_switch_mode": "STANDARD",
    "nested_nsx": False,
    "is_default": False,
    "resource_type": "TransportZone",
    "id": "7779df74-a1b4-4804-bbcc-316b7195cd53",
    "display_name": "Create-Transport-Zone",
    "description": "Transport Zone 112",
}

error_json = {"error": "The credentials were incorrect or the account specified has been locked."}


@patch.object(nsxt_request, "call_api")
def test_get_using_basic_auth(mock_call_api):

    mock_call_api.return_value = _mock_transport_zones

    assert (
        nsxt_transport_zone.get(
            hostname="sample-hostname", username="username", password="password", verify_ssl=False
        )
        == _mock_transport_zones
    )


@patch.object(nsxt_request, "call_api")
def test_get_using_query_param(mock_call_api):

    mock_call_api.return_value = _mock_transport_zones

    assert (
        nsxt_transport_zone.get(
            hostname="sample-hostname",
            username="username",
            password="password",
            page_size=1,
            verify_ssl=False,
        )
        == _mock_transport_zones
    )


@patch.object(nsxt_request, "call_api")
def test_get_when_error_from_nsxt_util(mock_call_api):

    mock_call_api.return_value = error_json

    resposne = nsxt_transport_zone.get(
        hostname="sample-hostname", username="username", password="password", verify_ssl=False
    )
    assert resposne == error_json


@patch.object(nsxt_request, "call_api")
def test_get_by_display_when_error_in_response(mock_call_api):

    mock_call_api.return_value = error_json

    assert (
        nsxt_transport_zone.get_by_display_name(
            hostname="sample-hostname",
            username="username",
            password="password",
            verify_ssl=False,
            display_name="sample display name",
        )
        == error_json
    )


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name_using_basic_auth(mock_call_api):

    mock_call_api.return_value = _mock_transport_zones_by_display_name

    assert (
        nsxt_transport_zone.get_by_display_name(
            hostname="sample-hostname",
            username="username",
            password="password",
            verify_ssl=False,
            display_name="Create-Transport-Zone",
        )
        == _mock_transport_zones_by_display_name
    )


@patch.object(nsxt_request, "call_api")
def test_create(mock_call_api):

    mock_call_api.return_value = _mock_create_response

    assert (
        nsxt_transport_zone.create(
            hostname="sample-hostname",
            username="username",
            password="password",
            host_switch_name="Check-Test",
            transport_type="OVERLAY",
            display_name="Create-Transport-Zone",
            verify_ssl=False,
        )
        == _mock_create_response
    )


@patch.object(nsxt_request, "call_api")
def test_create_with_error(mock_call_api):

    mock_call_api.return_value = error_json

    assert (
        nsxt_transport_zone.create(
            hostname="sample-hostname",
            username="username",
            password="password",
            host_switch_name="Check-Test",
            transport_type="OVERLAY",
            display_name="Create-Transport-Zone",
        )
        == error_json
    )


@patch.object(nsxt_request, "call_api")
def test_update(mock_call_api):

    mock_call_api.return_value = _mock_update_response

    assert (
        nsxt_transport_zone.update(
            hostname="sample-hostname",
            username="username",
            password="password",
            transport_zone_id="display-id",
            host_switch_name="Check-Test",
            transport_type="OVERLAY",
            display_name="Create-Transport-Zone",
            revision="1",
            description="Transport Zone 112",
        )
        == _mock_update_response
    )


@patch.object(nsxt_request, "call_api")
def test_update_with_error(mock_call_api):

    mock_call_api.return_value = error_json

    assert (
        nsxt_transport_zone.update(
            hostname="sample-hostname",
            username="username",
            password="password",
            transport_zone_id="display-id",
            host_switch_name="Check-Test",
            transport_type="OVERLAY",
            display_name="Create-Transport-Zone",
            revision="1",
            description="Transport Zone 112",
        )
        == error_json
    )


@patch.object(nsxt_request, "call_api")
def test_delete(mock_call_api):

    result = {"message": "Deleted transport zone successfully"}
    mock_call_api.return_value = result

    assert (
        nsxt_transport_zone.delete(
            hostname="sample-hostname",
            username="username",
            password="password",
            transport_zone_id="sample-node-id",
        )
        == result
    )


@patch.object(nsxt_request, "call_api")
def test_delete_with_error(mock_call_api):

    result = {"error": "Error occured while doing delete operation"}
    mock_call_api.return_value = result

    assert (
        nsxt_transport_zone.delete(
            hostname="sample-hostname",
            username="username",
            password="password",
            transport_zone_id="sample-node-id",
        )
        == result
    )
