"""
    :codeauthor: VMware
"""
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_vpn_statistics as vmc_vpn_statistics


@pytest.fixture
def ipsec_statistics_data(mock_vmc_request_call_api):
    data = {
        "local": {
            "results": [
                {
                    "ike_status": {"ike_session_state": "UP", "fail_reason": ""},
                    "policy_statistics": [
                        {
                            "rule_path": "/infra/tier-0s/vmc/locale-services/default/ipsec-vpn-services/default/sessions/1c23ed10-9662-11eb-9513-1519b5d0d3b0/rules/c62bef2f-085b-46d2-8738-7916e2686b08-l3vpn-rule",
                            "tunnel_statistics": [
                                {
                                    "tunnel_status": "UP",
                                    "tunnel_down_reason": "",
                                    "packets_in": 29552277,
                                    "packets_out": 19682099,
                                    "bytes_in": 23194341799,
                                    "bytes_out": 10180276728,
                                    "packets_received_other_error": 0,
                                    "replay_errors": 0,
                                    "integrity_failures": 0,
                                    "decryption_failures": 0,
                                    "packets_sent_other_error": 0,
                                    "seq_number_overflow_error": 0,
                                    "encryption_failures": 0,
                                    "sa_mismatch_errors_in": 0,
                                    "nomatching_policy_errors": 0,
                                    "sa_mismatch_errors_out": 0,
                                    "peer_subnet": "10.0.0.0/8",
                                    "local_subnet": "10.73.216.0/23",
                                    "dropped_packets_in": 0,
                                    "dropped_packets_out": 155114,
                                },
                                {
                                    "tunnel_status": "UP",
                                    "tunnel_down_reason": "",
                                    "packets_in": 21223687,
                                    "packets_out": 10370050,
                                    "bytes_in": 22884432847,
                                    "bytes_out": 2054428080,
                                    "packets_received_other_error": 0,
                                    "replay_errors": 0,
                                    "integrity_failures": 0,
                                    "decryption_failures": 0,
                                    "packets_sent_other_error": 0,
                                    "seq_number_overflow_error": 0,
                                    "encryption_failures": 0,
                                    "sa_mismatch_errors_in": 0,
                                    "nomatching_policy_errors": 0,
                                    "sa_mismatch_errors_out": 0,
                                    "peer_subnet": "10.0.0.0/8",
                                    "local_subnet": "10.72.115.0/24",
                                    "dropped_packets_in": 0,
                                    "dropped_packets_out": 1648,
                                },
                            ],
                            "aggregate_traffic_counters": {
                                "packets_in": 50775964,
                                "packets_out": 30052149,
                                "bytes_in": 46078774646,
                                "bytes_out": 12234704808,
                                "dropped_packets_in": 0,
                                "dropped_packets_out": 156762,
                            },
                        }
                    ],
                    "aggregate_traffic_counters": {
                        "packets_in": 50775964,
                        "packets_out": 30052149,
                        "bytes_in": 46078774646,
                        "bytes_out": 12234704808,
                        "dropped_packets_in": 0,
                        "dropped_packets_out": 156762,
                    },
                    "last_update_timestamp": 1619760302126,
                    "display_name": "IT_VPN",
                    "enforcement_point_path": "/infra/sites/default/enforcement-points/vmc-enforcementpoint",
                    "resource_type": "IPSecVpnSessionStatisticsNsxT",
                }
            ],
            "intent_path": "/infra/tier-0s/vmc/locale-services/default/ipsec-vpn-services/default/sessions/1c23ed10-9662-11eb-9513-1519b5d0d3b0",
        }
    }
    mock_vmc_request_call_api.return_value = data
    yield data


@pytest.fixture
def ipsec_session_data(mock_vmc_request_call_api):
    data = {
        "local": {
            "results": [
                {
                    "rules": [
                        {
                            "sources": [{"subnet": "10.72.115.0/24"}, {"subnet": "10.73.216.0/23"}],
                            "destinations": [{"subnet": "10.0.0.0/8"}],
                            "logged": False,
                            "enabled": True,
                            "action": "PROTECT",
                            "sequence_number": 0,
                            "resource_type": "IPSecVpnRule",
                            "id": "c62bef2f-085b-46d2-8738-7916e2686b08-l3vpn-rule",
                            "display_name": "c62bef2f-085b-46d2-8738-7916e2686b08-l3vpn-rule",
                            "path": "/infra/tier-0s/vmc/locale-services/default/ipsec-vpn-services/default/sessions/1c23ed10-9662-11eb-9513-1519b5d0d3b0/rules/c62bef2f-085b-46d2-8738-7916e2686b08-l3vpn-rule",
                            "relative_path": "c62bef2f-085b-46d2-8738-7916e2686b08-l3vpn-rule",
                            "parent_path": "/infra/tier-0s/vmc/locale-services/default/ipsec-vpn-services/default/sessions/1c23ed10-9662-11eb-9513-1519b5d0d3b0",
                            "unique_id": "12dad242-7a47-43fa-97cb-2203dae74681",
                            "marked_for_delete": False,
                            "overridden": False,
                            "_create_time": 1617663508552,
                            "_create_user": "mmakhija@vmware.com",
                            "_last_modified_time": 1617663508553,
                            "_last_modified_user": "mmakhija@vmware.com",
                            "_system_owned": False,
                            "_protection": "NOT_PROTECTED",
                            "_revision": 0,
                        }
                    ],
                    "resource_type": "PolicyBasedIPSecVpnSession",
                    "id": "1c23ed10-9662-11eb-9513-1519b5d0d3b0",
                    "display_name": "IT_VPN",
                    "path": "/infra/tier-0s/vmc/locale-services/default/ipsec-vpn-services/default/sessions/1c23ed10-9662-11eb-9513-1519b5d0d3b0",
                    "relative_path": "1c23ed10-9662-11eb-9513-1519b5d0d3b0",
                    "parent_path": "/infra/tier-0s/vmc/locale-services/default/ipsec-vpn-services/default",
                    "unique_id": "2813c56f-c472-44aa-975a-73743ef5dd6f",
                    "marked_for_delete": False,
                    "overridden": False,
                    "enabled": True,
                    "local_endpoint_path": "/infra/tier-0s/vmc/locale-services/default/ipsec-vpn-services/default/local-endpoints/Public-IP1",
                    "authentication_mode": "PSK",
                    "ike_profile_path": "/infra/ipsec-vpn-ike-profiles/1c23ed10-9662-11eb-9513-1519b5d0d3b0",
                    "tunnel_profile_path": "/infra/ipsec-vpn-tunnel-profiles/1c23ed10-9662-11eb-9513-1519b5d0d3b0",
                    "dpd_profile_path": "/infra/ipsec-vpn-dpd-profiles/nsx-default-l3vpn-dpd-profile",
                    "compliance_suite": "NONE",
                    "connection_initiation_mode": "INITIATOR",
                    "peer_address": "66.170.110.80",
                    "peer_id": "66.170.110.80",
                    "_create_time": 1617663508245,
                    "_create_user": "mmakhija@vmware.com",
                    "_last_modified_time": 1617665249205,
                    "_last_modified_user": "mmakhija@vmware.com",
                    "_system_owned": False,
                    "_protection": "NOT_PROTECTED",
                    "_revision": 1,
                }
            ],
            "result_count": 1,
            "sort_by": "display_name",
            "sort_ascending": True,
        }
    }
    mock_vmc_request_call_api.return_value = data
    yield data


@pytest.fixture
def l2vpn_statistics_data(mock_vmc_request_call_api):
    data = {
        "local": {
            "results": [
                {
                    "traffic_statistics_per_segment": [
                        {
                            "segment_path": "/infra/tier-1s/cgw/segments/514bccba-5803-4afd-935f-57ae86cb5a02",
                            "packets_out": 48886,
                            "bytes_out": 3435386,
                            "packets_in": 9426,
                            "bytes_in": 935246,
                            "packets_receive_error": 0,
                            "packets_sent_error": 0,
                            "bum_packets_in": 0,
                            "bum_bytes_in": 0,
                            "bum_bytes_out": 0,
                        }
                    ],
                    "tap_traffic_counters": [
                        {
                            "packets_out": 29097,
                            "bytes_out": 2985849,
                            "packets_in": 9426,
                            "bytes_in": 973022,
                            "packets_receive_error": 0,
                            "packets_sent_error": 0,
                        }
                    ],
                    "display_name": "L2VPN",
                    "enforcement_point_path": "/infra/sites/default/enforcement-points/vmc-enforcementpoint",
                    "resource_type": "L2VPNSessionStatisticsNsxT",
                }
            ],
            "intent_path": "/infra/tier-0s/vmc/locale-services/default/l2vpn-services/default/sessions/c1373cd0-b2f0-11eb-80f4-d1a84667de41",
        }
    }
    mock_vmc_request_call_api.return_value = data
    yield data


@pytest.fixture
def l2vpn_sessions_data(mock_vmc_request_call_api):
    data = {
        "local": {
            "results": [
                {
                    "transport_tunnels": [
                        "/infra/tier-0s/vmc/locale-services/default/ipsec-vpn-services/default/sessions/c1373cd0-b2f0-11eb-80f4-d1a84667de41"
                    ],
                    "enabled": False,
                    "tunnel_encapsulation": {"protocol": "GRE"},
                    "resource_type": "L2VPNSession",
                    "id": "c1373cd0-b2f0-11eb-80f4-d1a84667de41",
                    "display_name": "L2VPN",
                    "path": "/infra/tier-0s/vmc/locale-services/default/l2vpn-services/default/sessions/c1373cd0-b2f0-11eb-80f4-d1a84667de41",
                    "relative_path": "c1373cd0-b2f0-11eb-80f4-d1a84667de41",
                    "parent_path": "/infra/tier-0s/vmc/locale-services/default/l2vpn-services/default",
                    "unique_id": "ebf72202-2ae6-4f1f-afd6-a9db080e3121",
                    "marked_for_delete": False,
                    "overridden": False,
                    "_create_time": 1620803450863,
                    "_create_user": "pnaval@vmware.com",
                    "_last_modified_time": 1621083806392,
                    "_last_modified_user": "pnaval@vmware.com",
                    "_system_owned": False,
                    "_protection": "NOT_PROTECTED",
                    "_revision": 1,
                }
            ],
            "result_count": 1,
            "sort_by": "display_name",
            "sort_ascending": True,
        }
    }
    mock_vmc_request_call_api.return_value = data
    yield data


def test_get_l2vpn_statistics_should_return_api_response(l2vpn_statistics_data):
    assert (
        vmc_vpn_statistics.get_l2vpn_statistics(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            locale_service_id="locale_service_id",
            service_id="service_id",
            session_id="session_id",
            tier0_id="tier0_id",
            verify_ssl=False,
        )
        == l2vpn_statistics_data
    )


def test_get_l2vpn_statistics_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/v1/infra/tier-0s/tier0_id/"
        "locale-services/locale_service_id/l2vpn-services/service_id/sessions/session_id/statistics"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_vpn_statistics.get_l2vpn_statistics(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            locale_service_id="locale_service_id",
            service_id="service_id",
            session_id="session_id",
            tier0_id="tier0_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url


def test_get_l2vpn_sessions_should_return_api_response(l2vpn_sessions_data):
    assert (
        vmc_vpn_statistics.get_l2vpn_sessions(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            locale_service_id="locale_service_id",
            service_id="service_id",
            tier0_id="tier0_id",
            verify_ssl=False,
        )
        == l2vpn_sessions_data
    )


def test_get_l2vpn_sessions_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/v1/infra/tier-0s/tier0_id/"
        "locale-services/locale_service_id/l2vpn-services/service_id/sessions"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_vpn_statistics.get_l2vpn_sessions(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            locale_service_id="locale_service_id",
            service_id="service_id",
            tier0_id="tier0_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url


def test_get_ipsec_statistics_should_return_api_response(ipsec_statistics_data):
    assert (
        vmc_vpn_statistics.get_ipsec_statistics(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            locale_service_id="locale_service_id",
            service_id="service_id",
            session_id="session_id",
            tier0_id="tier0_id",
            verify_ssl=False,
        )
        == ipsec_statistics_data
    )


def test_get_ipsec_statistics_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/v1/infra/tier-0s/tier0_id/"
        "locale-services/locale_service_id/ipsec-vpn-services/service_id/sessions/session_id/statistics"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_vpn_statistics.get_ipsec_statistics(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            locale_service_id="locale_service_id",
            service_id="service_id",
            session_id="session_id",
            tier0_id="tier0_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url


def test_get_ipsec_statistics_fail_with_error_1(ipsec_statistics_data):
    """ Error when tier0_id or tier1_id is not specified """
    result = vmc_vpn_statistics.get_ipsec_statistics(
        hostname="hostname",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        org_id="org_id",
        sddc_id="sddc_id",
        locale_service_id="locale_service_id",
        service_id="service_id",
        session_id="session_id",
        verify_ssl=False,
    )

    assert "error" in result


def test_get_ipsec_statistics_fail_with_error_2(ipsec_statistics_data):
    """ Error when both tier0_id and tier1_id are specified """
    result = vmc_vpn_statistics.get_ipsec_statistics(
        hostname="hostname",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        org_id="org_id",
        sddc_id="sddc_id",
        locale_service_id="locale_service_id",
        service_id="service_id",
        session_id="session_id",
        tier0_id="tier0_id",
        tier1_id="tier1_id",
        verify_ssl=False,
    )

    assert "error" in result


def test_get_ipsec_session__should_return_api_response(ipsec_session_data):
    assert (
        vmc_vpn_statistics.get_ipsec_sessions(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            locale_service_id="locale_service_id",
            service_id="service_id",
            tier0_id="tier0_id",
            verify_ssl=False,
        )
        == ipsec_session_data
    )


def test_get_ipsec_sessions_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/v1/infra/tier-0s/tier0_id/"
        "locale-services/locale_service_id/ipsec-vpn-services/service_id/sessions"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_vpn_statistics.get_ipsec_sessions(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            locale_service_id="locale_service_id",
            service_id="service_id",
            tier0_id="tier0_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
