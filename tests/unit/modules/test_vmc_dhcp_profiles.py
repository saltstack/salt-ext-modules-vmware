"""
    Unit tests for vmc_dhcp_profiles execution module
"""
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_dhcp_profiles as vmc_dhcp_profiles


@pytest.fixture
def dhcp_profile_data_by_id(mock_vmc_request_call_api):
    data = {
        "server_address": "100.96.1.1/30",
        "server_addresses": ["100.96.1.1/30"],
        "lease_time": 7650,
        "edge_cluster_path": "/infra/sites/default/enforcement-points/vmc-enforcementpoint/edge-clusters/f23d3148-69c4-44e2-a6b8-0dbb6b221f1d",
        "preferred_edge_paths": [
            "/infra/sites/default/enforcement-points/vmc-enforcementpoint/edge-clusters/f23d3148-69c4-44e2-a6b8-0dbb6b221f1d/edge-nodes/ce770cf4-a062-11eb-873e-000c29e1f185",
            "/infra/sites/default/enforcement-points/vmc-enforcementpoint/edge-clusters/f23d3148-69c4-44e2-a6b8-0dbb6b221f1d/edge-nodes/cf3310c0-a062-11eb-8483-000c29d1a046",
        ],
        "resource_type": "DhcpServerConfig",
        "id": "default",
        "display_name": "default",
        "path": "/infra/dhcp-server-configs/default",
        "relative_path": "default",
        "parent_path": "/infra",
        "unique_id": "21f54bcb-ab20-4a39-9a20-a9098eb7500a",
        "marked_for_delete": False,
        "overridden": False,
        "_create_time": 1618763394434,
        "_create_user": "admin",
        "_last_modified_time": 1618763394442,
        "_last_modified_user": "admin",
        "_system_owned": False,
        "_protection": "NOT_PROTECTED",
        "_revision": 0,
    }
    mock_vmc_request_call_api.return_value = data
    yield data


@pytest.fixture
def dhcp_profile_data(mock_vmc_request_call_api, dhcp_profile_data_by_id):
    data = {
        "results": [dhcp_profile_data_by_id],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": True,
    }
    mock_vmc_request_call_api.return_value = data
    yield data


def test_get_dhcp_profiles_should_return_api_response(dhcp_profile_data):
    assert (
        vmc_dhcp_profiles.get(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            type="server",
            verify_ssl=False,
        )
        == dhcp_profile_data
    )


def test_get_dhcp_profiles_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/dhcp-server-configs"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_dhcp_profiles.get(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            type="server",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url


def test_get_dhcp_profile_by_id_should_return_single_dhcp_profile(dhcp_profile_data_by_id):
    assert (
        vmc_dhcp_profiles.get_by_id(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            type="server",
            dhcp_profile_id="dhcp_profile_id",
            verify_ssl=False,
        )
        == dhcp_profile_data_by_id
    )


def test_get_dhcp_profile_by_id_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/dhcp-server-configs/dhcp_profile_id"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_dhcp_profiles.get_by_id(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            type="server",
            dhcp_profile_id="dhcp_profile_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url


def test_delete_dhcp_profile_when_api_should_return_successfully_deleted_message(
    mock_vmc_request_call_api,
):
    expected_response = {"message": "DHCP profile deleted successfully"}
    mock_vmc_request_call_api.return_value = expected_response
    assert (
        vmc_dhcp_profiles.delete(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            type="server",
            dhcp_profile_id="dhcp_profile_id",
            verify_ssl=False,
        )
        == expected_response
    )


def test_delete_dhcp_profile_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/dhcp-relay-configs/dhcp_profile_id"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_dhcp_profiles.delete(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            type="relay",
            dhcp_profile_id="dhcp_profile_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
