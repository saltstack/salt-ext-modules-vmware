"""
Tests for execution module of NSX-T Segment
"""

from unittest.mock import patch

import saltext.vmware.modules.nsxt_policy_segment as nsxt_policy_segment
from saltext.vmware.utils import nsxt_request

_mock_segment = {
    "type": "DISCONNECTED",
    "overlay_id": 75005,
    "transport_zone_path": "/infra/sites/default/enforcement-points/default/transport-zones/b68c4c9e-fc51-413d-81fd-aadd28f8526a",
    "admin_state": "UP",
    "replication_mode": "SOURCE",
    "evpn_tenant_config_path": "/infra/evpn-tenant-configs/Sample-Tenant",
    "evpn_segment": True,
    "resource_type": "Segment",
    "id": "Evpn-InfraSegment-Sample-Tenant-75005-J6zjQe",
    "display_name": "Check-Test-Segment",
    "path": "/infra/segments/Evpn-InfraSegment-Sample-Tenant-75005-J6zjQe",
    "relative_path": "Evpn-InfraSegment-Sample-Tenant-75005-J6zjQe",
    "parent_path": "/infra",
    "unique_id": "7bd619bd-8fda-4bc3-a928-1e43a9729c7a",
    "marked_for_delete": False,
    "overridden": False,
}

_mock_transport_zone = {
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
    "id": "Transport-Zone-101",
    "display_name": "Transport-Zone-101",
    "_create_user": "admin",
    "_create_time": 1617088301924,
    "_last_modified_user": "admin",
    "_last_modified_time": 1617088301924,
    "_system_owned": False,
    "_protection": "NOT_PROTECTED",
    "_revision": 0,
    "_schema": "/v1/schema/TransportZone",
}

_mock_tier1 = {
    "tier0_path": "/infra/tier-0s/T0GW_By_Salt",
    "failover_mode": "PREEMPTIVE",
    "enable_standby_relocation": False,
    "dhcp_config_paths": ["/infra/dhcp-server-configs/DHCPSP"],
    "route_advertisement_types": ["TIER1_IPSEC_LOCAL_ENDPOINT"],
    "force_whitelisting": False,
    "default_rule_logging": False,
    "disable_firewall": False,
    "ipv6_profile_paths": ["/infra/ipv6-ndra-profiles/default", "/infra/ipv6-dad-profiles/default"],
    "type": "ROUTED",
    "pool_allocation": "ROUTING",
    "arp_limit": 6000,
    "resource_type": "Tier1",
    "id": "Sample-Tier_1",
    "display_name": "Sample-Tier_1",
    "description": "Created_By_salt_2",
    "path": "/infra/tier-1s/T1_GW_Salt",
    "relative_path": "T1_GW_Salt",
    "parent_path": "/infra",
    "unique_id": "48424baa-9a60-45bc-b633-5f8f31ba8492",
    "marked_for_delete": False,
    "overridden": False,
    "_create_user": "admin",
    "_create_time": 1619610368160,
    "_last_modified_user": "admin",
    "_last_modified_time": 1619610368167,
    "_system_owned": False,
    "_protection": "NOT_PROTECTED",
    "_revision": 0,
}

_mock_create_response = {
    "type": "ROUTED",
    "subnets": [{"gateway_address": "10.22.12.2/23", "network": "10.22.12.0/23"}],
    "connectivity_path": "/infra/tier-0s/T0GW_By_Salt",
    "transport_zone_path": "/infra/sites/default/enforcement-points/default/transport-zones/b68c4c9e-fc51-413d-81fd-aadd28f8526a",
    "advanced_config": {
        "address_pool_paths": ["/infra/ip-pools/IP-Address-Pool-Test"],
        "hybrid": False,
        "inter_router": False,
        "local_egress": False,
        "urpf_mode": "STRICT",
        "connectivity": "ON",
    },
    "admin_state": "UP",
    "replication_mode": "MTEP",
    "resource_type": "Segment",
    "id": "Check-Segment-Post",
    "display_name": "Check-Segment-Post",
    "description": "Gateway created by salt",
    "tags": [{"scope": "world", "tag": "hello"}],
    "path": "/infra/segments/T0GW_By_Salt-Check",
    "relative_path": "T0GW_By_Salt-Check",
    "parent_path": "/infra",
    "unique_id": "a09b93d7-4fa0-4288-980c-fefb728d0323",
    "marked_for_delete": False,
    "overridden": False,
    "_create_user": "admin",
    "_create_time": 1619615838058,
    "_last_modified_user": "admin",
    "_last_modified_time": 1619615838065,
    "_system_owned": False,
    "_protection": "NOT_PROTECTED",
    "_revision": 0,
}

_mock_segment_port = {
    "id": "Check-Segment-Port",
    "display_name": "Check-Segment-Port",
    "description": "Segment Port created by salt",
    "tags": [{"scope": "world", "tag": "hello"}],
}

_error_json = {"error": "The credentials were incorrect or the account specified has been locked."}


@patch.object(nsxt_request, "call_api")
def test_get_using_basic_auth(mock_call_api):
    response = {"results": [_mock_segment]}
    mock_call_api.return_value = response

    assert (
        nsxt_policy_segment.get(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
        )
        == response
    )


@patch.object(nsxt_request, "call_api")
def test_get_with_query_params(mock_call_api):
    response = {"results": [_mock_segment]}
    mock_call_api.return_value = response

    assert (
        nsxt_policy_segment.get(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            page_size=1,
            verify_ssl=False,
        )
        == response
    )


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name_using_basic_auth(mock_call_api):
    response = {"results": [_mock_segment]}
    mock_call_api.return_value = response

    assert (
        nsxt_policy_segment.get_by_display_name(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
            display_name="Check-Test-Segment",
        )
        == response
    )


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name_when_error_from_nsxt_util(mock_call_api):
    mock_call_api.return_value = _error_json

    assert (
        nsxt_policy_segment.get_by_display_name(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
            display_name="Check-Test-Segment",
        )
        == _error_json
    )


@patch.object(nsxt_request, "call_api")
def test_create_of_segment(mock_call_api):
    response_segment = {"results": [_mock_segment]}
    response_transport_zone = {"results": [_mock_transport_zone]}
    response_tier1 = {"results": [_mock_tier1]}
    mock_call_api.side_effect = [
        response_transport_zone,
        response_tier1,
        response_segment,
        _mock_segment,
        _mock_create_response,
    ]

    result = nsxt_policy_segment.create_or_update(
        hostname="sample.nsxt-hostname.vmware",
        username="username",
        password="password",
        verify_ssl=False,
        display_name="Check-Segment-Post",
        description="Gateway created by salt",
        tags='[{"tag":"hello", "scope":"world"}]',
        tier1_display_name="Sample-Tier_1",
        transport_zone_display_name="Transport-Zone-101",
        advanced_config={"address_pool_id": "IP-Address-Pool-Test"},
        subnets=[{"gateway_address": "10.22.12.2/23", "network": "10.22.12.0/23"}],
    )
    assert result[0].get("resourceType") == "segments"
    assert result[0].get("results") == _mock_create_response


@patch.object(nsxt_request, "call_api")
def test_create_of_segment_with_error(mock_call_api):
    mock_call_api.side_effect = [_error_json]

    result = nsxt_policy_segment.create_or_update(
        hostname="sample.nsxt-hostname.vmware",
        username="username",
        password="password",
        verify_ssl=False,
        display_name="Check-Segment-Post",
        description="Gateway created by salt",
        tags='[{"tag":"hello", "scope":"world"}]',
        tier1_display_name="Sample-Tier_1",
        transport_zone_display_name="b68c4c9e-fc51-413d-81fd-aadd28f8526a",
        advanced_config={"address_pool_id": "IP-Address-Pool-Test"},
        subnets=[{"gateway_address": "10.22.12.2/23", "network": "10.22.12.0/23"}],
    )

    assert "error" in result[0].get("error")


@patch.object(nsxt_request, "call_api")
def test_create_of_segment_with_segment_port(mock_call_api):

    response_segment = {"results": [_mock_segment]}
    response_segment_port = {"results": [_mock_segment_port]}
    response_transport_zone = {"results": [_mock_transport_zone]}
    response_tier1 = {"results": [_mock_tier1]}

    mock_call_api.side_effect = [
        response_transport_zone,
        response_tier1,
        response_segment,
        _mock_segment,
        _mock_segment,
        response_segment_port,
        _mock_segment_port,
        _mock_segment_port,
    ]

    result = nsxt_policy_segment.create_or_update(
        hostname="sample.nsxt-hostname.vmware",
        username="username",
        password="password",
        verify_ssl=False,
        display_name="Check-Segment-Post",
        description="Gateway created by salt",
        tags='[{"tag":"hello", "scope":"world"}]',
        tier1_display_name="Sample-Tier_1",
        transport_zone_display_name="Transport-Zone-101",
        advanced_config={"address_pool_id": "IP-Address-Pool-Test"},
        subnets=[{"gateway_address": "10.22.12.2/23", "network": "10.22.12.0/23"}],
        segment_ports=[{"display_name": "Check-Segment-Port-New"}],
    )

    assert result[0].get("resourceType") == "segments"
    assert result[0].get("results") == _mock_segment
    assert result[1].get("resourceType") == "segment_ports"
    assert result[1].get("results") == _mock_segment_port


@patch.object(nsxt_request, "call_api")
def test_create_of_segment_with_segment_port_with_error(mock_call_api):
    response_segment = {"results": [_mock_segment]}
    response_segment_port = {"results": [_mock_segment_port]}
    response_transport_zone = {"results": [_mock_transport_zone]}
    response_tier1 = {"results": [_mock_tier1]}

    mock_call_api.side_effect = [
        response_transport_zone,
        response_tier1,
        response_segment,
        _mock_segment,
        _mock_segment,
        response_segment_port,
        _error_json,
    ]

    result = nsxt_policy_segment.create_or_update(
        hostname="sample.nsxt-hostname.vmware",
        username="username",
        password="password",
        verify_ssl=False,
        display_name="Check-Segment-Post",
        description="Gateway created by salt",
        tags='[{"tag":"hello", "scope":"world"}]',
        tier1_display_name="Sample-Tier_1",
        transport_zone_display_name="Transport-Zone-101",
        advanced_config={"address_pool_id": "IP-Address-Pool-Test"},
        subnets=[{"gateway_address": "10.22.12.2/23", "network": "10.22.12.0/23"}],
        segment_ports=[{"display_name": "Check-Segment-Port-New"}],
    )

    assert result[0].get("resourceType") == "segments"
    assert result[0].get("results") == _mock_segment
    assert "error" in result[1].get("error")


@patch.object(nsxt_request, "call_api")
def test_delete_segment(mock_call_api):
    response_segment_port = {"results": [_mock_segment_port]}
    response_segment = {"results": [_mock_segment]}

    mock_call_api.side_effect = [response_segment_port, None, response_segment, None]

    result = nsxt_policy_segment.delete(
        hostname="hostname",
        username="username",
        password="pass",
        segment_id="Check-Segment-Post",
        verify_ssl=False,
    )

    assert result[0].get("resourceType") == "segment_ports"
    assert result[1].get("resourceType") == "segments"
    assert result[0].get("results") == "Check-Segment-Port deleted successfully"
    assert result[1].get("results") == "Check-Segment-Post deleted successfully"


@patch.object(nsxt_request, "call_api")
def test_delete_segment_with_error(mock_call_api):
    response_segment_port = {"results": [_mock_segment_port]}
    response_segment = {"results": [_mock_segment]}

    mock_call_api.side_effect = [response_segment_port, _error_json]

    result = nsxt_policy_segment.delete(
        hostname="hostname",
        username="username",
        password="pass",
        segment_id="Check-Segment-Post",
        verify_ssl=False,
    )

    assert "error" in result[0].get("error")


@patch.object(nsxt_request, "call_api")
def test_get_hierarchy(mock_call_api):
    segment_obj = {"id": "segment"}
    segment_port_obj1 = {"id": "sp1"}
    segment_port_obj2 = {"id": "sp2"}
    segment_port_list = {"results": [segment_port_obj1, segment_port_obj2]}
    mock_call_api.side_effect = [
        segment_obj,
        segment_port_list,
        segment_port_obj1,
        segment_port_obj2,
    ]

    expected_response = {
        "segments": {"id": "segment", "segment_ports": [{"id": "sp1"}, {"id": "sp2"}]}
    }
    result = nsxt_policy_segment.get_hierarchy(
        hostname="hostname",
        username="username",
        password="pass",
        segment_id=segment_obj["id"],
        verify_ssl=False,
    )

    assert result == expected_response


@patch.object(nsxt_request, "call_api")
def test_get_hierarchy_with_error(api_mock):
    segment_response = _error_json
    api_mock.side_effect = [segment_response]

    module_response = nsxt_policy_segment.get_hierarchy(
        hostname="hostname",
        username="username",
        password="pass",
        segment_id="segment-id",
        verify_ssl=False,
    )

    assert module_response == _error_json
