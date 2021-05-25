from unittest.mock import patch

import saltext.vmware.modules.nsxt_policy_tier1 as nsxt_policy_tier1
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

_mock_tier1_gateway = {
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
    "id": "T1_GW_Salt",
    "display_name": "T1_GW_Salt",
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

_mock_locale_services = {
    "route_redistribution_config": {
        "bgp_enabled": True,
        "ospf_enabled": False,
        "redistribution_rules": [
            {"name": "rule-1", "route_redistribution_types": ["TIER1_CONNECTED"]}
        ],
    },
    "edge_cluster_path": "/infra/sites/default/enforcement-points/default/edge-clusters/5a59778c-47d4-4444-a529"
    "-3f0652f3d422",
    "preferred_edge_paths": [
        "/infra/sites/default/enforcement-points/default/edge-clusters/5a59778c-47d4-4444-a529-3f0652f3d422/edge"
        "-nodes/3d2d0e0c-dc2c-4db7-9c52-0245600103a8 "
    ],
    "bfd_profile_path": "/infra/bfd-profiles/default",
    "resource_type": "LocaleServices",
    "id": "LS-T1",
    "display_name": "LS-T1",
    "description": "LS_By_Salt",
    "path": "/infra/tier-1s/T1_GW_Salt/locale-services/LS-T1",
    "relative_path": "LS-T1",
    "parent_path": "/infra/tier-1s/T1_GW_Salt",
    "unique_id": "72357e0b-0202-459b-8557-d43dce8f8481",
    "marked_for_delete": False,
    "overridden": False,
    "_create_user": "admin",
    "_create_time": 1619610376920,
    "_last_modified_user": "admin",
    "_last_modified_time": 1619610376925,
    "_system_owned": False,
    "_protection": "NOT_PROTECTED",
    "_revision": 0,
}

_mock_interfaces = {
    "segment_path": "/infra/segments/T0GW_By_Salt1",
    "mtu": 100,
    "urpf_mode": "NONE",
    "ipv6_profile_paths": ["/infra/ipv6-ndra-profiles/default"],
    "resource_type": "Tier1Interface",
    "id": "T1_Inf",
    "display_name": "T1_Inf",
    "description": "Created_By_Salt",
    "path": "/infra/tier-1s/T1_GW_Salt/locale-services/LS-T1/interfaces/T1_Inf",
    "relative_path": "T1_Inf",
    "parent_path": "/infra/tier-1s/T1_GW_Salt/locale-services/LS-T1",
    "unique_id": "56abb622-9ce2-4bdc-b556-7c1ed35327d1",
    "marked_for_delete": False,
    "overridden": False,
    "subnets": [{"ip_addresses": ["35.1.1.1"], "prefix_len": 24}],
    "_create_user": "admin",
    "_create_time": 1619610382264,
    "_last_modified_user": "admin",
    "_last_modified_time": 1619610382274,
    "_system_owned": False,
    "_protection": "NOT_PROTECTED",
    "_revision": 0,
}

_mock_static_routes = [
    {
        "network": "172.16.10.0/24",
        "next_hops": [{"ip_address": "10.1.2.3", "admin_distance": 4}],
        "enabled_on_secondary": True,
        "resource_type": "StaticRoutes",
        "id": "SR-T1",
        "display_name": "SR-T1",
        "description": "SR_By_Salt",
        "path": "/infra/tier-1s/T1_GW_Salt/static-routes/SR-T1",
        "relative_path": "SR-T1",
        "parent_path": "/infra/tier-1s/T1_GW_Salt",
        "unique_id": "a8c60df5-ade3-4f0f-8261-31f3d67aa274",
        "marked_for_delete": False,
        "overridden": False,
        "_create_user": "admin",
        "_create_time": 1619610371904,
        "_last_modified_user": "admin",
        "_last_modified_time": 1619610371906,
        "_system_owned": False,
        "_protection": "NOT_PROTECTED",
        "_revision": 0,
    }
]

_mock_ipv6_ndra_profile = {
    "ra_mode": "SLAAC_DNS_THROUGH_RA",
    "ra_config": {
        "ra_interval": 600,
        "hop_limit": 64,
        "router_lifetime": 1800,
        "prefix_lifetime": 2592000,
        "prefix_preferred_time": 604800,
        "prefix_onlink_flag": True,
        "address_configuration_flag": True,
    },
    "dns_config": {
        "domain_name": [],
        "domain_name_lifetime": 1800,
        "dns_server": [],
        "dns_server_lifetime": 1800,
    },
    "reachable_timer": 0,
    "retransmit_interval": 1000,
    "resource_type": "Ipv6NdraProfile",
    "id": "default",
    "display_name": "default",
    "path": "/infra/ipv6-ndra-profiles/default",
    "relative_path": "default",
    "parent_path": "/infra",
    "unique_id": "9c658da4-0c87-4b0e-b882-6fca501c8f78",
    "marked_for_delete": False,
    "overridden": False,
    "_create_user": "system",
    "_create_time": 1614963657013,
    "_last_modified_user": "system",
    "_last_modified_time": 1614963657016,
    "_system_owned": True,
    "_protection": "NOT_PROTECTED",
    "_revision": 0,
}

_mock_ipv6_dad_profile = {
    "dad_mode": "LOOSE",
    "wait_time": 1,
    "ns_retries": 3,
    "resource_type": "Ipv6DadProfile",
    "id": "default",
    "display_name": "default",
    "path": "/infra/ipv6-dad-profiles/default",
    "relative_path": "default",
    "parent_path": "/infra",
    "unique_id": "869fa532-9c27-4dc9-84d7-ec4729d90aac",
    "marked_for_delete": False,
    "overridden": False,
    "_create_user": "system",
    "_create_time": 1614963657037,
    "_last_modified_user": "system",
    "_last_modified_time": 1614963657040,
    "_system_owned": True,
    "_protection": "NOT_PROTECTED",
    "_revision": 0,
}

_mock_bfd_profiles = {
    "interval": 500,
    "multiple": 3,
    "resource_type": "BfdProfile",
    "id": "default",
    "display_name": "default",
    "path": "/infra/bfd-profiles/default",
    "relative_path": "default",
    "parent_path": "/infra",
    "unique_id": "a24e173c-978b-4adc-936a-a32eb6d601b9",
    "marked_for_delete": False,
    "overridden": False,
    "_create_user": "system",
    "_create_time": 1614963657058,
    "_last_modified_user": "system",
    "_last_modified_time": 1614963657062,
    "_system_owned": True,
    "_protection": "NOT_PROTECTED",
    "_revision": 0,
}

_mock_dhcp_relay = {
    "server_addresses": ["10.10.10.10"],
    "resource_type": "DhcpRelayConfig",
    "id": "DHCP-Relay",
    "display_name": "DHCP-Relay",
    "path": "/infra/dhcp-relay-configs/DHCP-Relay",
    "relative_path": "DHCP-Relay",
    "parent_path": "/infra",
    "unique_id": "218ff128-af48-4d3c-a96a-21ffed1dde95",
    "marked_for_delete": False,
    "overridden": False,
    "_create_user": "admin",
    "_create_time": 1618397631756,
    "_last_modified_user": "admin",
    "_last_modified_time": 1618397631760,
    "_system_owned": False,
    "_protection": "NOT_PROTECTED",
    "_revision": 0,
}

_mock_segment = {
    "type": "DISCONNECTED",
    "transport_zone_path": "/infra/sites/default/enforcement-points/default/transport-zones/b68c4c9e-fc51-413d-81fd-aadd28f8526a",
    "advanced_config": {
        "address_pool_paths": ["/infra/ip-pools/IP-Address-Pool-Test"],
        "hybrid": False,
        "inter_router": False,
        "local_egress": False,
        "urpf_mode": "STRICT",
        "connectivity": "OFF",
    },
    "admin_state": "DOWN",
    "replication_mode": "MTEP",
    "resource_type": "Segment",
    "id": "T0GW_By_Salt1",
    "display_name": "Check",
    "description": "Gateway created by salt",
    "tags": [{"scope": "world", "tag": "hello"}],
    "path": "/infra/segments/T0GW_By_Salt1",
    "relative_path": "T0GW_By_Salt1",
    "parent_path": "/infra",
    "unique_id": "7e53219f-fc73-4fd0-ba8d-4b74edfaefe1",
    "marked_for_delete": False,
    "overridden": False,
    "_create_user": "admin",
    "_create_time": 1619537817084,
    "_last_modified_user": "admin",
    "_last_modified_time": 1619615626925,
    "_system_owned": False,
    "_protection": "NOT_PROTECTED",
    "_revision": 2,
}

_mock_edge_cluster = {
    "nsx_id": "5a59778c-47d4-4444-a529-3f0652f3d422",
    "inter_site_forwarding_enabled": False,
    "resource_type": "PolicyEdgeCluster",
    "id": "5a59778c-47d4-4444-a529-3f0652f3d422",
    "display_name": "Edge_cluster_101",
    "description": "",
    "path": "/infra/sites/default/enforcement-points/default/edge-clusters/5a59778c-47d4-4444-a529-3f0652f3d422",
    "relative_path": "5a59778c-47d4-4444-a529-3f0652f3d422",
    "parent_path": "/infra/sites/default/enforcement-points/default",
    "unique_id": "54232618-1ff1-45b7-b521-589bc40ead6e",
    "marked_for_delete": False,
    "overridden": False,
    "_create_user": "system",
    "_create_time": 1617089100475,
    "_last_modified_user": "system",
    "_last_modified_time": 1617873764472,
    "_system_owned": False,
    "_protection": "NOT_PROTECTED",
    "_revision": 1,
}

_error_json = {"error": "The credentials were incorrect or the account specified has been locked."}


@patch.object(nsxt_request, "call_api")
def test_get_using_basic_auth(mock_call_api):
    response = {"results": [_mock_tier1_gateway]}
    mock_call_api.return_value = response

    assert (
        nsxt_policy_tier1.get(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
        )
        == response
    )


@patch.object(nsxt_request, "call_api")
def test_get_with_query_params(mock_call_api):
    response = {"results": [_mock_tier1_gateway]}
    mock_call_api.return_value = response

    assert (
        nsxt_policy_tier1.get(
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
    response = {"results": [_mock_tier1_gateway]}
    mock_call_api.return_value = response

    assert (
        nsxt_policy_tier1.get_by_display_name(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
            display_name="T1_GW_Salt",
        )
        == response
    )


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name_when_error_from_nsxt_util(mock_call_api):
    mock_call_api.return_value = _error_json

    assert (
        nsxt_policy_tier1.get_by_display_name(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
            display_name="T1GW_By_Salt",
        )
        == _error_json
    )


@patch.object(nsxt_request, "call_api")
def test_create_of_tier1_gateway(mock_call_api):
    response_tier0_get = {"results": [_mock_tier0_gateway]}
    response_tier1_get = {"results": []}
    mock_call_api.side_effect = [
        response_tier0_get,
        response_tier1_get,
        _mock_tier1_gateway,
        _mock_tier1_gateway,
    ]

    result = nsxt_policy_tier1.create_or_update(
        hostname="nsx-t.vmware.com",
        username="username",
        password="password",
        verify_ssl=False,
        arp_limit=6000,
        default_rule_logging=False,
        description="Created_By_salt_2",
        dhcp_config_id="DHCPSP",
        disable_firewall=False,
        display_name="T1_GW_Salt",
        enable_standby_relocation=False,
        failover_mode="PREEMPTIVE",
        force_whitelisting=False,
        ipv6_ndra_profile_id="default",
        ipv6_dad_profile_id="default",
        tier0_display_name="T0GW_By_Salt",
        pool_allocation="ROUTING",
        type="ROUTED",
    )

    assert result[0].get("resourceType") == "tier1"
    assert result[0].get("results") == _mock_tier1_gateway


@patch.object(nsxt_request, "call_api")
def test_create_of_tier1_gateway_with_error_in_get_id_by_display_name(mock_call_api):
    mock_call_api.side_effect = [_error_json]

    result = nsxt_policy_tier1.create_or_update(
        hostname="nsx-t.vmware.com",
        username="username",
        password="password",
        verify_ssl=False,
        arp_limit=6000,
        default_rule_logging=False,
        description="Created_By_salt_2",
        dhcp_config_id="DHCPSP",
        disable_firewall=False,
        display_name="T1_GW_Salt",
        enable_standby_relocation=False,
        failover_mode="PREEMPTIVE",
        force_whitelisting=False,
        ipv6_ndra_profile_id="default",
        ipv6_dad_profile_id="default",
        tier0_display_name="T0GW_By_Salt",
        pool_allocation="ROUTING",
        type="ROUTED",
    )

    assert (
        result[0].get("error")
        == "{'resourceType': 'tier1', 'error': 'The credentials were incorrect or the account specified has been locked.'}"
    )


@patch.object(nsxt_request, "call_api")
def test_create_of_tier1_gateway_with_more_than_one_error_in_get_id_by_display_name(mock_call_api):
    mock_call_api.side_effect = [{"results": [_mock_tier0_gateway, _mock_tier0_gateway]}]

    result = nsxt_policy_tier1.create_or_update(
        hostname="nsx-t.vmware.com",
        username="username",
        password="password",
        verify_ssl=False,
        arp_limit=6000,
        default_rule_logging=False,
        description="Created_By_salt_2",
        dhcp_config_id="DHCPSP",
        disable_firewall=False,
        display_name="T1_GW_Salt",
        enable_standby_relocation=False,
        failover_mode="PREEMPTIVE",
        force_whitelisting=False,
        ipv6_ndra_profile_id="default",
        ipv6_dad_profile_id="default",
        tier0_display_name="T0GW_By_Salt",
        pool_allocation="ROUTING",
        type="ROUTED",
    )

    assert (
        result[0].get("error")
        == "{'resourceType': 'tier1', 'error': 'Multiple objects found with display name T0GW_By_Salt at path https://nsx-t.vmware.com/policy/api/v1/infra/tier-0s, please provide id'}"
    )


@patch.object(nsxt_request, "call_api")
def test_create_of_tier1_gateway_with_no_object_error_in_get_id_by_display_name(mock_call_api):
    mock_call_api.side_effect = [{"results": []}]

    result = nsxt_policy_tier1.create_or_update(
        hostname="nsx-t.vmware.com",
        username="username",
        password="password",
        verify_ssl=False,
        arp_limit=6000,
        default_rule_logging=False,
        description="Created_By_salt_2",
        dhcp_config_id="DHCPSP",
        disable_firewall=False,
        display_name="T1_GW_Salt",
        enable_standby_relocation=False,
        failover_mode="PREEMPTIVE",
        force_whitelisting=False,
        ipv6_ndra_profile_id="default",
        ipv6_dad_profile_id="default",
        tier0_display_name="T0GW_By_Salt",
        pool_allocation="ROUTING",
        type="ROUTED",
    )

    assert (
        result[0].get("error")
        == "{'resourceType': 'tier1', 'error': 'No object found with display name T0GW_By_Salt at path https://nsx-t.vmware.com/policy/api/v1/infra/tier-0s'}"
    )


@patch.object(nsxt_request, "call_api")
def test_create_of_tier1_gateway_with_static_routes(mock_call_api):
    response_tier0 = {"results": [_mock_tier0_gateway]}
    response_tier1 = {"results": [_mock_tier1_gateway]}
    response_static_routes = {"results": []}

    mock_call_api.side_effect = [
        response_tier0,
        response_tier1,
        _mock_tier1_gateway,
        _mock_tier1_gateway,
        response_static_routes,
        _mock_static_routes,
        _mock_static_routes,
    ]

    result = nsxt_policy_tier1.create_or_update(
        hostname="nsx-t.vmware.com",
        username="username",
        password="password",
        verify_ssl=False,
        arp_limit=6000,
        default_rule_logging=False,
        description="Created_By_salt_2",
        dhcp_config_id="DHCPSP",
        disable_firewall=False,
        display_name="T1_GW_Salt",
        enable_standby_relocation=False,
        failover_mode="PREEMPTIVE",
        force_whitelisting=False,
        ipv6_ndra_profile_id="default",
        ipv6_dad_profile_id="default",
        tier0_display_name="T0GW_By_Salt",
        pool_allocation="ROUTING",
        type="ROUTED",
        static_routes=[
            {
                "network": "172.16.10.0/24",
                "display_name": "SR-T1",
                "description": "SR_By_Salt",
                "enabled_on_secondary": True,
                "next_hops": [{"admin_distance": 4, "ip_address": "10.1.2.3"}],
            }
        ],
    )

    assert result[0].get("resourceType") == "tier1"
    assert result[0].get("results") == _mock_tier1_gateway
    assert result[1].get("resourceType") == "static_routes"
    assert result[1].get("results") == _mock_static_routes


@patch.object(nsxt_request, "call_api")
def test_create_of_tier1_gateway_with_local_services_interfaces(mock_call_api):
    response_tier0 = {"results": [_mock_tier0_gateway]}
    response_tier1 = {"results": [_mock_tier1_gateway]}
    response_locale_response = {"results": []}

    response_locale_interface_response = {"results": []}

    mock_call_api.side_effect = [
        response_tier0,
        response_tier1,
        _mock_tier1_gateway,
        _mock_tier1_gateway,
        response_locale_response,
        _mock_locale_services,
        _mock_locale_services,
        response_locale_interface_response,
        _mock_interfaces,
        _mock_interfaces,
    ]

    result = nsxt_policy_tier1.create_or_update(
        hostname="nsx-t.vmware.com",
        username="username",
        password="password",
        verify_ssl=False,
        arp_limit=6000,
        default_rule_logging=False,
        description="Created_By_salt_2",
        dhcp_config_id="DHCPSP",
        disable_firewall=False,
        display_name="T1_GW_Salt",
        enable_standby_relocation=False,
        failover_mode="PREEMPTIVE",
        force_whitelisting=False,
        ipv6_ndra_profile_id="default",
        ipv6_dad_profile_id="default",
        tier0_display_name="T0GW_By_Salt",
        pool_allocation="ROUTING",
        type="ROUTED",
        locale_services=[
            {
                "display_name": "LS-T1",
                "description": "LS_By_Salt",
                "route_redistribution_config": {
                    "bgp_enabled": True,
                    "ospf_enabled": True,
                    "redistribution_rules": [
                        {"name": "rule-1", "route_redistribution_types": ["TIER1_CONNECTED"]}
                    ],
                },
                "bfd_profile_id": "default",
                "edge_cluster_info": {
                    "site_id": "default",
                    "enforcementpoint_id": "default",
                    "edge_cluster_id": "5a59778c-47d4-4444-a529-3f0652f3d422",
                },
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
                        "segment_id": "T0GW_By_Salt1",
                        "ipv6_ndra_profile_id": "default",
                        "dhcp_config_id": "DHCP-Relay",
                        "display_name": "T1_Inf",
                        "description": "Created_By_Salt",
                        "mtu": 100,
                        "subnets": [{"ip_addresses": ["35.1.1.1"], "prefix_len": 24}],
                        "urpf_mode": "NONE",
                    }
                ],
            }
        ],
    )

    assert result[0].get("resourceType") == "tier1"
    assert result[1].get("resourceType") == "locale_services"
    assert result[2].get("resourceType") == "interfaces"


@patch.object(nsxt_request, "call_api")
def test_update_of_tier1_gateway_with_full_payload(mock_call_api):
    response_tier0 = {"results": [_mock_tier0_gateway]}
    response_tier1 = {"results": [_mock_tier1_gateway]}
    response_bfd_profile = {"results": [_mock_bfd_profiles]}
    response_dhcp_relay = {"results": [_mock_dhcp_relay]}
    response_edge_cluster = {"results": [_mock_edge_cluster]}
    response_segment = {"results": [_mock_segment]}
    response_static_routes = {"results": []}
    response_ipv6_ndra_profile = {"results": [_mock_ipv6_ndra_profile]}
    response_ipv6_dad_profile = {"results": [_mock_ipv6_dad_profile]}
    response_locale_response = {"results": []}

    response_locale_interface_response = {"results": []}

    mock_call_api.side_effect = [
        response_ipv6_ndra_profile,
        response_ipv6_dad_profile,
        response_tier0,
        response_tier1,
        _mock_tier1_gateway,
        _mock_tier1_gateway,
        response_static_routes,
        _mock_static_routes,
        _mock_static_routes,
        response_edge_cluster,
        response_bfd_profile,
        response_locale_response,
        _mock_locale_services,
        _mock_locale_services,
        response_segment,
        response_ipv6_ndra_profile,
        response_dhcp_relay,
        response_locale_interface_response,
        _mock_interfaces,
        _mock_interfaces,
    ]

    result = nsxt_policy_tier1.create_or_update(
        hostname="nsx-t.vmware.com",
        username="username",
        password="password",
        verify_ssl=False,
        arp_limit=6000,
        default_rule_logging=False,
        description="Created_By_salt_2",
        dhcp_config_id="DHCPSP",
        disable_firewall=False,
        display_name="T1_GW_Salt",
        enable_standby_relocation=False,
        failover_mode="PREEMPTIVE",
        force_whitelisting=False,
        ipv6_ndra_profile_display_name="default",
        ipv6_dad_profile_display_name="default",
        tier0_display_name="T0GW_By_Salt",
        pool_allocation="ROUTING",
        type="ROUTED",
        static_routes=[
            {
                "network": "172.16.10.0/24",
                "display_name": "SR-T1",
                "description": "SR_By_Salt",
                "enabled_on_secondary": True,
                "next_hops": [{"admin_distance": 4, "ip_address": "10.1.2.3"}],
            }
        ],
        locale_services=[
            {
                "display_name": "LS-T1",
                "description": "LS_By_Salt",
                "route_redistribution_config": {
                    "bgp_enabled": True,
                    "ospf_enabled": True,
                    "redistribution_rules": [
                        {"name": "rule-1", "route_redistribution_types": ["TIER1_CONNECTED"]}
                    ],
                },
                "bfd_profile_display_name": "default",
                "edge_cluster_info": {
                    "site_id": "default",
                    "enforcementpoint_id": "default",
                    "edge_cluster_id": "5a59778c-47d4-4444-a529-3f0652f3d422",
                },
                "preferred_edge_nodes_info": [
                    {
                        "site_id": "default",
                        "enforcementpoint_id": "default",
                        "edge_cluster_display_name": "Edge_cluster_101",
                        "edge_node_id": "3d2d0e0c-dc2c-4db7-9c52-0245600103a8",
                    }
                ],
                "interfaces": [
                    {
                        "segment_display_name": "Check",
                        "ipv6_ndra_profile_display_name": "default",
                        "dhcp_config_display_name": "DHCP-Relay",
                        "display_name": "T1_Inf",
                        "description": "Created_By_Salt",
                        "mtu": 100,
                        "subnets": [{"ip_addresses": ["35.1.1.1"], "prefix_len": 24}],
                        "urpf_mode": "NONE",
                    }
                ],
            }
        ],
    )

    assert result[0].get("resourceType") == "tier1"
    assert result[1].get("resourceType") == "static_routes"
    assert result[2].get("resourceType") == "locale_services"
    assert result[3].get("resourceType") == "interfaces"


@patch.object(nsxt_request, "call_api")
def test_delete(api_mock):
    tier1_id = "tier1_id_1"
    static_routes_response = {"results": [{"id": "sr_id_1"}]}
    locale_services_response = {"results": [{"id": "ls_id_1"}]}
    interfaces_response = {"results": [{"id": "interface_id_1"}, {"id": "interface_id_2"}]}

    expected_response = [
        {"resourceType": "static_routes", "results": "sr_id_1 deleted successfully"},
        {"resourceType": "interfaces", "results": "interface_id_1 deleted successfully"},
        {"resourceType": "interfaces", "results": "interface_id_2 deleted successfully"},
        {"resourceType": "locale_services", "results": "ls_id_1 deleted successfully"},
        {"resourceType": "tier1", "results": "tier1_id_1 deleted successfully"},
    ]

    api_mock.side_effect = [
        static_routes_response,
        None,  # static route delete response
        locale_services_response,
        interfaces_response,
        None,
        None,  # delete response for interface 1 and 2
        None,  # delete response of locale_service
        None,  # delete response of tier1
    ]

    assert (
        nsxt_policy_tier1.delete(
            hostname="hostname",
            username="username",
            password="pass",
            tier1_id=tier1_id,
            verify_ssl=False,
        )
        == expected_response
    )


@patch.object(nsxt_request, "call_api")
def test_delete_error_while_delete(api_mock):
    tier1_id = "tier1_id_1"
    err_msg = "Generic error occurred"
    static_routes_error_response = {"error": err_msg}
    static_routes_response = {"results": [{"id": "sr_id_1"}]}
    api_mock.side_effect = [static_routes_response, static_routes_error_response]

    module_response = nsxt_policy_tier1.delete(
        hostname="hostname",
        username="username",
        password="pass",
        tier1_id=tier1_id,
        verify_ssl=False,
    )
    assert (
        module_response[len(module_response) - 1]["error"]
        == "{'resourceType': 'static_routes', 'error': '" + err_msg + "'}"
    )


@patch.object(nsxt_request, "call_api")
def test_get_hierarchy(api_mock):
    tier1_obj = {"id": "tier1"}
    static_route_obj1 = {"id": "sr1"}
    static_route_obj2 = {"id": "sr2"}
    static_routes_list = {"results": [static_route_obj1, static_route_obj2]}
    local_services_obj = {"id": "ls1"}
    local_services_list = {"results": [local_services_obj]}
    interface_obj1 = {"id": "interface1"}
    interface_obj2 = {"id": "interface2"}
    interfaces_list = {"results": [interface_obj1, interface_obj2]}

    api_mock.side_effect = [
        tier1_obj,
        static_routes_list,
        static_route_obj1,
        static_route_obj2,
        local_services_list,
        local_services_obj,
        interfaces_list,
        interface_obj1,
        interface_obj2,
    ]

    expected_hierarchy_response = {
        "tier1": {
            "id": "tier1",
            "static_routes": [static_route_obj1, static_route_obj2],
            "locale_services": {
                "id": "ls1",
                "interfaces": [interface_obj1, interface_obj2],
            },
        }
    }
    module_response = nsxt_policy_tier1.get_hierarchy(
        hostname="hostname",
        username="username",
        password="pass",
        tier1_id=tier1_obj["id"],
        verify_ssl=False,
    )
    assert expected_hierarchy_response == module_response


@patch.object(nsxt_request, "call_api")
def test_get_hierarchy_with_error(api_mock):
    tier_1_response = _error_json
    api_mock.side_effect = [tier_1_response]

    module_response = nsxt_policy_tier1.get_hierarchy(
        hostname="hostname",
        username="username",
        password="pass",
        tier1_id="tier1_id",
        verify_ssl=False,
    )

    assert module_response == _error_json
