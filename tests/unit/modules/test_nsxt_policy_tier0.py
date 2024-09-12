"""
Tests for execution module of NSX-T tier 0
"""
from unittest.mock import patch

import saltext.vmware.modules.nsxt_policy_tier0 as nsxt_policy_tier0
from saltext.vmware.utils import nsxt_request

_mock_tier0_gateway = {
    "transit_subnets": ["100.64.0.0/16"],
    "internal_transit_subnets": ["169.254.0.0/24"],
    "ha_mode": "ACTIVE_ACTIVE",
    "failover_mode": "NON_PREEMPTIVE",
    "dhcp_config_paths": ["/infra/dhcp-server-configs/DHCPSP"],
    "ipv6_profile_paths": ["/infra/ipv6-ndra-profiles/default", "/infra/ipv6-dad-profiles/default"],
    "force_whitelisting": False,
    "default_rule_logging": False,
    "disable_firewall": False,
    "rd_admin_field": "10.10.10.10",
    "advanced_config": {"forwarding_up_timer": 0, "connectivity": "ON"},
    "resource_type": "Tier0",
    "id": "Check-Gateway",
    "display_name": "T0GW_By_Salt",
    "description": "Check Create Of Gateway",
    "path": "/infra/tier-0s/Check-Gateway",
    "relative_path": "Check-Gateway",
    "parent_path": "/infra",
    "unique_id": "561bfd1c-e2ec-4527-b00d-2b1769d789ad",
    "marked_for_delete": False,
    "overridden": False,
    "_create_user": "admin",
    "_create_time": 1615200000469,
    "_last_modified_user": "admin",
    "_last_modified_time": 1618396613346,
    "_system_owned": False,
    "_protection": "NOT_PROTECTED",
    "_revision": 4,
}

_mock_locale_services = {
    "route_redistribution_config": {"bgp_enabled": True, "ospf_enabled": False},
    "edge_cluster_path": "/infra/sites/default/enforcement-points/default/edge-clusters/5a59778c-47d4-4444-a529-3f0652f3d422",
    "preferred_edge_paths": [
        "/infra/sites/default/enforcement-points/default/edge-clusters/5a59778c-47d4-4444-a529-3f0652f3d422/edge-nodes/3d2d0e0c-dc2c-4db7-9c52-0245600103a8"
    ],
    "bfd_profile_path": "/infra/bfd-profiles/default",
    "resource_type": "LocaleServices",
    "id": "ls-1",
    "display_name": "ls-1",
    "path": "/infra/tier-0s/T0GW_By_Salt/locale-services/ls-1",
    "relative_path": "ls-1",
    "parent_path": "/infra/tier-0s/T0GW_By_Salt",
    "unique_id": "699dd902-0aac-40c3-b685-b74fff6e6400",
    "marked_for_delete": False,
    "overridden": False,
    "_create_user": "admin",
    "_create_time": 1618579625089,
    "_last_modified_user": "admin",
    "_last_modified_time": 1618987408952,
    "_system_owned": False,
    "_protection": "NOT_PROTECTED",
    "_revision": 1,
}

_mock_interfaces = {
    "display_name": "interfaces-1",
    "description": "Created_by_API",
    "ipv6_ndra_profile_id": "default",
    "segment_id": "Segment_101",
    "edge_node_info": {
        "site_id": "default",
        "enforcementpoint_id": "default",
        "edge_cluster_id": "5a59778c-47d4-4444-a529-3f0652f3d422",
        "edge_node_id": "3d2d0e0c-dc2c-4db7-9c52-0245600103a8",
    },
    "subnets": [{"ip_addresses": ["35.1.1.1"], "prefix_len": 24}],
    "mtu": 100,
    "multicast": {"enabled": True, "hello_interval": 30, "hold_interval": 100},
}

_mock_bgp = {
    "display_name": "bgp-1",
    "description": "Created_by_API",
    "ecmp": True,
    "enabled": True,
    "graceful_restart_config": {
        "mode": "HELPER_ONLY",
        "timer": {"restart_timer": 180, "stale_route_timer": 600},
    },
    "inter_sr_ibgp": True,
    "local_as_num": 65546,
    "multipath_relax": True,
    "neighbors": [
        {
            "source_addresses": [],
            "description": "Created_by_API",
            "bfd": {"enabled": True, "interval": 500, "multiple": 3},
            "display_name": "bgp-neighbor-1",
            "graceful_restart_mode": "HELPER_ONLY",
            "hold_down_time": 180,
            "keep_alive_time": 60,
            "maximum_hop_limit": 1,
            "neighbor_address": "10.0.0.1",
            "remote_as_num": 65536,
        }
    ],
}

_mock_neighbour = {
    "source_addresses": [],
    "description": "Created_by_API",
    "bfd": {"enabled": True, "interval": 500, "multiple": 3},
    "display_name": "bgp-neighbor-1",
    "graceful_restart_mode": "HELPER_ONLY",
    "hold_down_time": 180,
    "keep_alive_time": 60,
    "maximum_hop_limit": 1,
    "neighbor_address": "10.0.0.1",
    "remote_as_num": 65536,
}

_mock_static_routes = [
    {
        "network": "10.10.10.0/23",
        "next_hops": [{"ip_address": "10.1.2.3", "admin_distance": 4}],
        "enabled_on_secondary": True,
        "resource_type": "StaticRoutes",
        "id": "sr-1",
        "display_name": "sr-1",
        "description": "Created_by_API",
        "path": "/infra/tier-0s/T0GW_By_Salt/static-routes/sr-1",
        "relative_path": "sr-1",
        "parent_path": "/infra/tier-0s/T0GW_By_Salt",
        "unique_id": "fd7f690c-666a-49a5-88b3-461eab3ac5a1",
        "marked_for_delete": False,
        "overridden": False,
        "_create_user": "admin",
        "_create_time": 1618579619938,
        "_last_modified_user": "admin",
        "_last_modified_time": 1618987276957,
        "_system_owned": False,
        "_protection": "NOT_PROTECTED",
        "_revision": 1,
    }
]

_mock_bfd_peers = {
    "enabled": True,
    "peer_address": "10.1.1.2",
    "bfd_profile_path": "/infra/bfd-profiles/default",
    "scope": [],
    "resource_type": "StaticRouteBfdPeer",
    "id": "srbfdp-1",
    "display_name": "srbfdp-1",
    "path": "/infra/tier-0s/T0GW_By_Salt/static-routes/bfd-peers/srbfdp-1",
    "relative_path": "srbfdp-1",
    "parent_path": "/infra/tier-0s/T0GW_By_Salt",
    "unique_id": "bd13c708-cc12-4a2c-b3ae-acd452300cfb",
    "marked_for_delete": False,
    "overridden": False,
    "_create_user": "admin",
    "_create_time": 1618579622883,
    "_last_modified_user": "admin",
    "_last_modified_time": 1618987339321,
    "_system_owned": False,
    "_protection": "NOT_PROTECTED",
    "_revision": 0,
}

_error_json = {"error": "The credentials were incorrect or the account specified has been locked."}


@patch.object(nsxt_request, "call_api")
def test_get_using_basic_auth(mock_call_api):
    response = {"results": [_mock_tier0_gateway]}
    mock_call_api.return_value = response

    assert (
        nsxt_policy_tier0.get(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
        )
        == response
    )


@patch.object(nsxt_request, "call_api")
def test_get_with_query_params(mock_call_api):
    response = {"results": [_mock_tier0_gateway]}
    mock_call_api.return_value = response

    assert (
        nsxt_policy_tier0.get(
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
    response = {"results": [_mock_tier0_gateway]}
    mock_call_api.return_value = response

    assert (
        nsxt_policy_tier0.get_by_display_name(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
            display_name="T0GW_By_Salt",
        )
        == response
    )


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name_when_error_from_nsxt_util(mock_call_api):
    mock_call_api.return_value = _error_json

    assert (
        nsxt_policy_tier0.get_by_display_name(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
            display_name="T0GW_By_Salt",
        )
        == _error_json
    )


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name_tier0_gateway(mock_call_api):
    response = {"results": []}
    mock_call_api.return_value = response

    assert (
        nsxt_policy_tier0.get_by_display_name(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
            display_name="T0GW_By_Salt",
        )
        == response
    )


@patch.object(nsxt_request, "call_api")
def test_create_of_tier0_gateway(mock_call_api):
    response_tier0 = {"results": [_mock_tier0_gateway]}
    mock_call_api.side_effect = [response_tier0, _mock_tier0_gateway, _mock_tier0_gateway]

    result = nsxt_policy_tier0.create_or_update(
        hostname="nsx-t.vmware.com",
        username="username",
        password="password",
        verify_ssl=False,
        display_name="T0GW_By_Salt",
        description="Gateway created by salt",
        tags='[{"tag":"hello", "scope":"world"}]',
        ha_mode="ACTIVE_ACTIVE",
        internal_transit_subnets=["169.254.0.0/24"],
        transit_subnets=["100.64.0.0/16"],
        failover_mode="PREEMPTIVE",
        rd_admin_field="10.10.10.10",
        dhcp_config_id="DHCP-Relay",
        arp_limit="5000",
        force_whitelisting=False,
        default_rule_logging=False,
        disable_firewall=True,
        ipv6_ndra_profile_id="default",
        ipv6_dad_profile_id="default",
    )

    assert result[0].get("resourceType") == "tier0"
    assert result[0].get("results") == _mock_tier0_gateway


@patch.object(nsxt_request, "call_api")
def test_create_of_tier0_gateway_with_error_in_get_display_name(mock_call_api):
    mock_call_api.side_effect = [_error_json]

    result = nsxt_policy_tier0.create_or_update(
        hostname="nsx-t.vmware.com",
        username="username",
        password="password",
        verify_ssl=False,
        display_name="T0GW_By_Salt",
        description="Gateway created by salt",
        tags='[{"tag":"hello", "scope":"world"}]',
        ha_mode="ACTIVE_ACTIVE",
        internal_transit_subnets=["169.254.0.0/24"],
        transit_subnets=["100.64.0.0/16"],
        failover_mode="PREEMPTIVE",
        rd_admin_field="10.10.10.10",
        dhcp_config_id="DHCP-Relay",
        arp_limit="5000",
        force_whitelisting=False,
        default_rule_logging=False,
        disable_firewall=True,
        ipv6_ndra_profile_id="default",
        ipv6_dad_profile_id="default",
    )

    assert "error" in result[0].get("error")


@patch.object(nsxt_request, "call_api")
def test_create_of_tier0_gateway_with_error_in_get(mock_call_api):
    response_tier0 = {"results": [_mock_tier0_gateway]}
    mock_call_api.side_effect = [response_tier0, _mock_tier0_gateway, _error_json]

    result = nsxt_policy_tier0.create_or_update(
        hostname="nsx-t.vmware.com",
        username="username",
        password="password",
        verify_ssl=False,
        display_name="T0GW_By_Salt",
        description="Gateway created by salt",
        tags='[{"tag":"hello", "scope":"world"}]',
        ha_mode="ACTIVE_ACTIVE",
        internal_transit_subnets=["169.254.0.0/24"],
        transit_subnets=["100.64.0.0/16"],
        failover_mode="PREEMPTIVE",
        rd_admin_field="10.10.10.10",
        dhcp_config_id="DHCP-Relay",
        arp_limit="5000",
        force_whitelisting=False,
        default_rule_logging=False,
        disable_firewall=True,
        ipv6_ndra_profile_id="default",
        ipv6_dad_profile_id="default",
    )

    assert "error" in result[0]["error"]


@patch.object(nsxt_request, "call_api")
def test_create_of_tier0_gateway_with_static_routes(mock_call_api):
    response_tier0 = {"results": [_mock_tier0_gateway]}
    response_static_routes = {"results": _mock_static_routes}

    mock_call_api.side_effect = [
        response_tier0,
        _mock_tier0_gateway,
        _mock_tier0_gateway,
        response_static_routes,
        _mock_static_routes,
        _mock_static_routes,
    ]

    result = nsxt_policy_tier0.create_or_update(
        hostname="nsx-t.vmware.com",
        username="username",
        password="password",
        verify_ssl=False,
        display_name="T0GW_By_Salt",
        description="Gateway created by salt",
        tags='[{"tag":"hello", "scope":"world"}]',
        ha_mode="ACTIVE_ACTIVE",
        internal_transit_subnets=["169.254.0.0/24"],
        transit_subnets=["100.64.0.0/16"],
        failover_mode="PREEMPTIVE",
        rd_admin_field="10.10.10.10",
        dhcp_config_id="DHCP-Relay",
        arp_limit="5000",
        force_whitelisting=False,
        default_rule_logging=False,
        disable_firewall=True,
        ipv6_ndra_profile_id="default",
        ipv6_dad_profile_id="default",
        static_routes=[
            {
                "display_name": "sr-1",
                "description": "Created_by_API-Update",
                "enabled_on_secondary": True,
                "network": "10.10.10.0/23",
                "next_hops": [{"admin_distance": 4, "ip_address": "10.1.2.3"}],
            }
        ],
    )

    assert result[0].get("resourceType") == "tier0"
    assert result[0].get("results") == _mock_tier0_gateway
    assert result[1].get("resourceType") == "static_routes"
    assert result[1].get("results") == _mock_static_routes


@patch.object(nsxt_request, "call_api")
def test_create_of_tier0_gateway_with_bfd_peers(mock_call_api):
    response_tier0 = {"results": [_mock_tier0_gateway]}

    response_bfd_peers = {"results": [_mock_bfd_peers]}
    mock_call_api.side_effect = [
        response_tier0,
        _mock_tier0_gateway,
        _mock_tier0_gateway,
        response_bfd_peers,
        _mock_bfd_peers,
        _mock_bfd_peers,
    ]

    result = nsxt_policy_tier0.create_or_update(
        hostname="nsx-t.vmware.com",
        username="username",
        password="password",
        verify_ssl=False,
        display_name="T0GW_By_Salt",
        description="Gateway created by salt",
        tags='[{"tag":"hello", "scope":"world"}]',
        ha_mode="ACTIVE_ACTIVE",
        internal_transit_subnets=["169.254.0.0/24"],
        transit_subnets=["100.64.0.0/16"],
        failover_mode="PREEMPTIVE",
        rd_admin_field="10.10.10.10",
        dhcp_config_id="DHCP-Relay",
        arp_limit="5000",
        force_whitelisting=False,
        default_rule_logging=False,
        disable_firewall=True,
        ipv6_ndra_profile_id="default",
        ipv6_dad_profile_id="default",
        vrf_config={"tier0_id": "ls-1", "route_targets": []},
        bfd_peers=[
            {"display_name": "srbfdp-1", "peer_address": "10.1.1.2", "bfd_profile_id": "default-id"}
        ],
    )

    assert result[0].get("resourceType") == "tier0"
    assert result[1].get("resourceType") == "bfd_peers"


@patch.object(nsxt_request, "call_api")
def test_create_of_tier0_gateway_with_local_services_edge_cluster_info(mock_call_api):
    response_tier0 = {"results": [_mock_tier0_gateway]}

    response_locale_response = {"results": [_mock_locale_services]}

    mock_call_api.side_effect = [
        response_tier0,
        _mock_tier0_gateway,
        _mock_tier0_gateway,
        response_locale_response,
        _mock_locale_services,
        _mock_locale_services,
    ]

    result = nsxt_policy_tier0.create_or_update(
        hostname="nsx-t.vmware.com",
        username="username",
        password="password",
        verify_ssl=False,
        display_name="T0GW_By_Salt",
        description="Gateway created by salt",
        tags='[{"tag":"hello", "scope":"world"}]',
        ha_mode="ACTIVE_ACTIVE",
        internal_transit_subnets=["169.254.0.0/24"],
        transit_subnets=["100.64.0.0/16"],
        failover_mode="PREEMPTIVE",
        rd_admin_field="10.10.10.10",
        dhcp_config_id="DHCP-Relay",
        arp_limit="5000",
        force_whitelisting=False,
        default_rule_logging=False,
        disable_firewall=True,
        ipv6_ndra_profile_id="default",
        ipv6_dad_profile_id="default",
        locale_services=[
            {
                "bfd_profile_name": "default",
                "display_name": "ls-1",
                "description": "Check-Update-Description",
                "edge_cluster_info": {
                    "site_id": "default",
                    "enforcementpoint_id": "default",
                    "edge_cluster_id": "5a59778c-47d4-4444-a529-3f0652f3d422",
                },
            }
        ],
    )

    assert result[0].get("resourceType") == "tier0"
    assert result[1].get("resourceType") == "locale_services"


@patch.object(nsxt_request, "call_api")
def test_create_of_tier0_gateway_with_local_services_interfaces(mock_call_api):
    response_tier0 = {"results": [_mock_tier0_gateway]}

    response_locale_response = {"results": [_mock_locale_services]}

    response_locale_interface_response = {"results": [_mock_interfaces]}

    mock_call_api.side_effect = [
        response_tier0,
        _mock_tier0_gateway,
        _mock_tier0_gateway,
        response_locale_response,
        _mock_locale_services,
        _mock_locale_services,
        response_locale_interface_response,
        _mock_interfaces,
        _mock_interfaces,
    ]

    result = nsxt_policy_tier0.create_or_update(
        hostname="nsx-t.vmware.com",
        username="username",
        password="password",
        verify_ssl=False,
        display_name="T0GW_By_Salt",
        description="Gateway created by salt",
        tags='[{"tag":"hello", "scope":"world"}]',
        ha_mode="ACTIVE_ACTIVE",
        internal_transit_subnets=["169.254.0.0/24"],
        transit_subnets=["100.64.0.0/16"],
        failover_mode="PREEMPTIVE",
        rd_admin_field="10.10.10.10",
        dhcp_config_id="DHCP-Relay",
        arp_limit="5000",
        force_whitelisting=False,
        default_rule_logging=False,
        disable_firewall=True,
        ipv6_ndra_profile_id="default",
        ipv6_dad_profile_id="default",
        locale_services=[
            {
                "bfd_profile_name": "default",
                "display_name": "ls-1",
                "description": "edit-locale-services",
                "interfaces": [
                    {
                        "display_name": "interfaces-1",
                        "description": "Created_by_API",
                        "ipv6_ndra_profile_id": "default",
                        "segment_id": "Segment_101",
                        "edge_node_info": {
                            "site_id": "default",
                            "enforcementpoint_id": "default",
                            "edge_cluster_id": "5a59778c-47d4-4444-a529-3f0652f3d422",
                            "edge_node_id": "3d2d0e0c-dc2c-4db7-9c52-0245600103a8",
                        },
                        "subnets": [{"ip_addresses": ["35.1.1.1"], "prefix_len": 24}],
                        "mtu": 100,
                        "multicast": {"enabled": True, "hello_interval": 30, "hold_interval": 100},
                    }
                ],
            }
        ],
    )

    assert result[0].get("resourceType") == "tier0"
    assert result[1].get("resourceType") == "locale_services"
    assert result[2].get("resourceType") == "interfaces"


@patch.object(nsxt_request, "call_api")
def test_create_of_tier0_gateway_with_local_services_BGP(mock_call_api):
    response_tier0 = {"results": [_mock_tier0_gateway]}

    response_locale_response = {"results": [_mock_locale_services]}

    response_locale_bgp_response = {"results": [_mock_bgp]}

    response_locale_bgp_neighbour = {"results": [_mock_neighbour]}

    mock_call_api.side_effect = [
        response_tier0,
        _mock_tier0_gateway,
        _mock_tier0_gateway,
        response_locale_response,
        _mock_locale_services,
        _mock_locale_services,
        response_locale_bgp_response,
        _mock_bgp,
        _mock_bgp,
        response_locale_bgp_neighbour,
        _mock_neighbour,
        _mock_neighbour,
    ]

    result = nsxt_policy_tier0.create_or_update(
        hostname="nsx-t.vmware.com",
        username="username",
        password="password",
        verify_ssl=False,
        display_name="T0GW_By_Salt",
        description="Gateway created by salt",
        tags='[{"tag":"hello", "scope":"world"}]',
        ha_mode="ACTIVE_ACTIVE",
        internal_transit_subnets=["169.254.0.0/24"],
        transit_subnets=["100.64.0.0/16"],
        failover_mode="PREEMPTIVE",
        rd_admin_field="10.10.10.10",
        dhcp_config_id="DHCP-Relay",
        arp_limit="5000",
        force_whitelisting=False,
        default_rule_logging=False,
        disable_firewall=True,
        ipv6_ndra_profile_id="default",
        ipv6_dad_profile_id="default",
        locale_services=[
            {
                "bfd_profile_name": "default",
                "display_name": "ls-1",
                "description": "edit-locale-services",
                "bgp": {
                    "display_name": "bgp-1",
                    "description": "Created_by_API-Edit",
                    "ecmp": True,
                    "enabled": True,
                    "graceful_restart_config": {
                        "mode": "HELPER_ONLY",
                        "timer": {"restart_timer": 180, "stale_route_timer": 600},
                    },
                    "inter_sr_ibgp": True,
                    "local_as_num": 65546,
                    "multipath_relax": True,
                    "neighbors": [
                        {
                            "source_addresses": [],
                            "description": "Created_by_API-Edit",
                            "bfd": {"enabled": True, "interval": 500, "multiple": 3},
                            "display_name": "bgp-neighbor-1",
                            "graceful_restart_mode": "HELPER_ONLY",
                            "hold_down_time": 180,
                            "keep_alive_time": 60,
                            "maximum_hop_limit": 1,
                            "neighbor_address": "10.0.0.1",
                            "remote_as_num": 65536,
                        }
                    ],
                },
            }
        ],
    )

    assert result[0].get("resourceType") == "tier0"
    assert result[1].get("resourceType") == "locale_services"
    assert result[2].get("resourceType") == "BGP"
    assert result[3].get("resourceType") == "neighbors"


@patch.object(nsxt_request, "call_api")
def test_create_of_tier0_gateway_with_local_services_with_complete_payload(mock_call_api):
    response_tier0 = {"results": [_mock_tier0_gateway]}

    response_locale_response = {"results": [_mock_locale_services]}

    response_locale_interface_response = {"results": [_mock_interfaces]}

    response_locale_bgp_response = {"results": [_mock_bgp]}

    response_locale_bgp_neighbour = {"results": [_mock_neighbour]}

    mock_call_api.side_effect = [
        response_tier0,
        _mock_tier0_gateway,
        _mock_tier0_gateway,
        response_locale_response,
        _mock_locale_services,
        _mock_locale_services,
        response_locale_interface_response,
        _mock_interfaces,
        _mock_interfaces,
        response_locale_bgp_response,
        _mock_bgp,
        _mock_bgp,
        response_locale_bgp_neighbour,
        _mock_neighbour,
        _mock_neighbour,
    ]

    result = nsxt_policy_tier0.create_or_update(
        hostname="nsx-t.vmware.com",
        username="username",
        password="password",
        verify_ssl=False,
        display_name="T0GW_By_Salt",
        description="Gateway created by salt",
        tags='[{"tag":"hello", "scope":"world"}]',
        ha_mode="ACTIVE_ACTIVE",
        internal_transit_subnets=["169.254.0.0/24"],
        transit_subnets=["100.64.0.0/16"],
        failover_mode="PREEMPTIVE",
        rd_admin_field="10.10.10.10",
        dhcp_config_id="DHCP-Relay",
        arp_limit="5000",
        force_whitelisting=False,
        default_rule_logging=False,
        disable_firewall=True,
        ipv6_ndra_profile_id="default",
        ipv6_dad_profile_id="default",
        locale_services=[
            {
                "bfd_profile_name": "default",
                "display_name": "ls-1",
                "description": "check-description-edit",
                "edge_cluster_info": {
                    "site_id": "default",
                    "enforcementpoint_id": "default",
                    "edge_cluster_id": "5a59778c-47d4-4444-a529-3f0652f3d422",
                },
                "route_redistribution_config": {"bgp_enabled": True, "ospf_enabled": False},
                "preferred_edge_nodes_info": [
                    {
                        "site_id": "default",
                        "enforcementpoint_id": "default",
                        "edge_cluster_id": "5a59778c-47d4-4444-a529-3f0652f3d422",
                        "edge_node_id": "3d2d0e0c-dc2c-4db7-9c52-0245600103a8",
                    }
                ],
                "interfaces": [
                    {
                        "display_name": "interfaces-1",
                        "description": "Created_by_API-edit",
                        "ipv6_ndra_profile_id": "default",
                        "segment_id": "Segment_101",
                        "edge_node_info": {
                            "site_id": "default",
                            "enforcementpoint_id": "default",
                            "edge_cluster_id": "5a59778c-47d4-4444-a529-3f0652f3d422",
                            "edge_node_id": "3d2d0e0c-dc2c-4db7-9c52-0245600103a8",
                        },
                        "subnets": [{"ip_addresses": ["35.1.1.1"], "prefix_len": 24}],
                        "mtu": 100,
                        "multicast": {"enabled": True, "hello_interval": 30, "hold_interval": 100},
                    }
                ],
                "bgp": {
                    "display_name": "bgp-1",
                    "description": "Created_by_API-edit",
                    "ecmp": True,
                    "enabled": True,
                    "graceful_restart_config": {
                        "mode": "HELPER_ONLY",
                        "timer": {"restart_timer": 180, "stale_route_timer": 600},
                    },
                    "inter_sr_ibgp": True,
                    "local_as_num": 65546,
                    "multipath_relax": True,
                    "neighbors": [
                        {
                            "source_addresses": [],
                            "description": "Created_by_API-edit",
                            "bfd": {"enabled": True, "interval": 500, "multiple": 3},
                            "display_name": "bgp-neighbor-1",
                            "graceful_restart_mode": "HELPER_ONLY",
                            "hold_down_time": 180,
                            "keep_alive_time": 60,
                            "maximum_hop_limit": 1,
                            "neighbor_address": "10.0.0.1",
                            "remote_as_num": 65536,
                        }
                    ],
                },
            }
        ],
    )

    assert result[0].get("resourceType") == "tier0"
    assert result[1].get("resourceType") == "locale_services"
    assert result[2].get("resourceType") == "interfaces"
    assert result[3].get("resourceType") == "BGP"
    assert result[4].get("resourceType") == "neighbors"


@patch.object(nsxt_request, "call_api")
def test_delete(api_mock):
    tier0_id = "tier0_id_1"
    static_routes_response = {"results": [{"id": "sr_id_1"}]}
    bfd_peers_response = {"results": [{"id": "bfd_peers_id_1"}]}
    locale_services_response = {"results": [{"id": "ls_id_1"}]}
    bgp_response = {"id": "bgp"}
    interfaces_response = {"results": [{"id": "interface_id_1"}, {"id": "interface_id_2"}]}
    bgp_neighbours_response = {"results": [{"id": "neighbour_id_1"}]}

    expected_response = [
        {"resourceType": "static_routes", "results": "sr_id_1 deleted successfully"},
        {"resourceType": "bfd_peers", "results": "bfd_peers_id_1 deleted successfully"},
        {"resourceType": "interfaces", "results": "interface_id_1 deleted successfully"},
        {"resourceType": "interfaces", "results": "interface_id_2 deleted successfully"},
        {"resourceType": "neighbors", "results": "neighbour_id_1 deleted successfully"},
        {"resourceType": "locale_services", "results": "ls_id_1 deleted successfully"},
        {"resourceType": "tier0", "results": "tier0_id_1 deleted successfully"},
    ]

    api_mock.side_effect = [
        static_routes_response,
        None,  # static route delete response
        bfd_peers_response,
        None,  # bfd peers delete response
        locale_services_response,
        interfaces_response,
        None,
        None,  # delete response for interface 1 and 2
        bgp_response,
        bgp_neighbours_response,
        None,  # delete response of bgp neighbour
        None,  # delete response of locale_service
        None,  # delete response of tier0
    ]

    assert (
        nsxt_policy_tier0.delete(
            hostname="hostname",
            username="username",
            password="pass",
            tier0_id=tier0_id,
            verify_ssl=False,
        )
        == expected_response
    )


@patch.object(nsxt_request, "call_api")
def test_delete_with_get_error(api_mock):
    tier0_id = "tier0_id_1"
    err_msg = "Generic error occurred"
    static_routes_error_response = {"error": err_msg}

    api_mock.return_value = static_routes_error_response

    module_response = nsxt_policy_tier0.delete(
        hostname="hostname",
        username="username",
        password="pass",
        tier0_id=tier0_id,
        verify_ssl=False,
    )
    assert (
        module_response[len(module_response) - 1]["error"]
        == "{'resourceType': 'static_routes', 'error': '" + err_msg + "'}"
    )


@patch.object(nsxt_request, "call_api")
def test_delete_error_while_delete(api_mock):
    tier0_id = "tier0_id_1"
    err_msg = "Generic error occurred"
    static_routes_error_response = {"error": err_msg}
    static_routes_response = {"results": [{"id": "sr_id_1"}]}
    api_mock.side_effect = [static_routes_response, static_routes_error_response]

    module_response = nsxt_policy_tier0.delete(
        hostname="hostname",
        username="username",
        password="pass",
        tier0_id=tier0_id,
        verify_ssl=False,
    )
    assert (
        module_response[len(module_response) - 1]["error"]
        == "{'resourceType': 'static_routes', 'error': '" + err_msg + "'}"
    )


@patch.object(nsxt_request, "call_api")
def test_get_hierarchy(api_mock):
    tier0_obj = {"id": "tier01"}
    static_route_obj1 = {"id": "sr1"}
    static_route_obj2 = {"id": "sr2"}
    static_routes_list = {"results": [static_route_obj1, static_route_obj2]}
    bfd_peers_obj = {"id": "bfdp1"}
    bfd_peers_list = {"results": [bfd_peers_obj]}
    local_services_obj = {"id": "ls1"}
    local_services_list = {"results": [local_services_obj]}
    interface_obj1 = {"id": "interface1"}
    interface_obj2 = {"id": "interface2"}
    interfaces_list = {"results": [interface_obj1, interface_obj2]}
    bgp_obj = {"id": "bgp"}
    bgp_response = {"id": "bgp"}
    neighbour_obj1 = {"id": "neighbour1"}
    neighbour_obj2 = {"id": "neighbour2"}
    neighbours_list = {"results": [neighbour_obj1, neighbour_obj2]}

    api_mock.side_effect = [
        tier0_obj,
        static_routes_list,
        static_route_obj1,
        static_route_obj2,
        bfd_peers_list,
        bfd_peers_obj,
        local_services_list,
        local_services_obj,
        interfaces_list,
        interface_obj1,
        interface_obj2,
        bgp_response,
        bgp_obj,
        neighbours_list,
        neighbour_obj1,
        neighbour_obj2,
    ]

    expected_hierarchy_response = {
        "tier0": {
            "id": "tier01",
            "static_routes": [static_route_obj1, static_route_obj2],
            "bfd_peers": bfd_peers_obj,
            "locale_services": {
                "id": "ls1",
                "interfaces": [interface_obj1, interface_obj2],
                "BGP": {"id": "bgp", "neighbors": [neighbour_obj1, neighbour_obj2]},
            },
        }
    }
    module_response = nsxt_policy_tier0.get_hierarchy(
        hostname="hostname",
        username="username",
        password="pass",
        tier0_id=tier0_obj["id"],
        verify_ssl=False,
    )
    assert expected_hierarchy_response == module_response


@patch.object(nsxt_request, "call_api")
def test_get_hierarchy_with_error_while_getting_list_response(api_mock):
    tier0_obj = {"id": "tier01"}
    err_msg = "Generic error"
    static_routes_list_response = {"error": err_msg}
    api_mock.side_effect = [tier0_obj, static_routes_list_response]
    assert (
        nsxt_policy_tier0.get_hierarchy(
            hostname="hostname",
            username="username",
            password="pass",
            tier0_id=tier0_obj["id"],
            verify_ssl=False,
        )["error"]
        == f"Failure while querying static_routes: {err_msg}"
    )


@patch.object(nsxt_request, "call_api")
def test_get_hierarchy_with_error_while_getting_object_response(api_mock):
    tier0_obj = {"id": "tier01"}
    err_msg = "Generic error"
    static_route_obj1 = {"id": "sr1"}
    static_route_obj2 = {"id": "sr2"}
    static_route_obj2_err = {"error": err_msg}
    static_routes_list = {"results": [static_route_obj1, static_route_obj2]}
    api_mock.side_effect = [tier0_obj, static_routes_list, static_route_obj1, static_route_obj2_err]
    assert (
        nsxt_policy_tier0.get_hierarchy(
            hostname="hostname",
            username="username",
            password="pass",
            tier0_id=tier0_obj["id"],
            verify_ssl=False,
        )["error"]
        == err_msg
    )
