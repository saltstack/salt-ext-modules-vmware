"""
    Unit tests for vmc_networks execution module
"""
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_networks as vmc_networks
from saltext.vmware.utils import vmc_constants


@pytest.fixture
def network_data_by_id(mock_vmc_request_call_api):
    data = {
        "type": "ROUTED",
        "subnets": [
            {
                "gateway_address": "192.168.1.1/24",
                "dhcp_ranges": ["192.168.1.2-192.168.1.254"],
                "network": "192.168.1.0/24",
            }
        ],
        "connectivity_path": "/infra/tier-1s/cgw",
        "admin_state": "UP",
        "replication_mode": "MTEP",
        "resource_type": "Segment",
        "id": "sddc-cgw-network-1",
        "display_name": "sddc-cgw-network-1",
        "path": "/infra/tier-1s/cgw/segments/sddc-cgw-network-1",
        "relative_path": "sddc-cgw-network-1",
        "parent_path": "/infra/tier-1s/cgw",
        "unique_id": "f21c4570-c771-4923-aeb7-126691d339e7",
        "marked_for_delete": False,
        "overridden": False,
        "_create_time": 1618213319210,
        "_create_user": "admin",
        "_last_modified_time": 1618213319235,
        "_last_modified_user": "admin",
        "_system_owned": False,
        "_protection": "NOT_PROTECTED",
        "_revision": 0,
    }
    mock_vmc_request_call_api.return_value = data
    yield data


@pytest.fixture
def network_data(mock_vmc_request_call_api, network_data_by_id):
    data = {"results": [network_data_by_id], "result_count": 1}
    mock_vmc_request_call_api.return_value = data
    yield data


def test_get_networks_should_return_api_response(network_data):
    assert (
        vmc_networks.get(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
        == network_data
    )


def test_get_networks_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/tier-1s/cgw/segments"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_networks.get(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.GET_REQUEST_METHOD


def test_get_network_by_id_should_return_single_network(network_data_by_id):
    result = vmc_networks.get_by_id(
        hostname="hostname",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        org_id="org_id",
        sddc_id="sddc_id",
        network_id="network-id",
        verify_ssl=False,
    )
    assert result == network_data_by_id


def test_get_network_by_id_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/tier-1s/cgw/segments/network-id"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_networks.get_by_id(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            network_id="network-id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
