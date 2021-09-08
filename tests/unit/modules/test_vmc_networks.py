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
    assert call_kwargs["method"] == vmc_constants.GET_REQUEST_METHOD


def test_delete_network_when_api_should_return_successfully_deleted_message(
    mock_vmc_request_call_api,
):
    expected_response = {"message": "Network deleted successfully"}
    mock_vmc_request_call_api.return_value = expected_response
    assert (
        vmc_networks.delete(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            network_id="network_id",
            verify_ssl=False,
        )
        == expected_response
    )


def test_delete_network_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/tier-1s/cgw/segments/network_id"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_networks.delete(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            network_id="network_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.DELETE_REQUEST_METHOD


def test_update_network_when_api_should_return_api_response(
    mock_vmc_request_call_api,
):
    expected_response = {"message": "Network updated successfully"}
    mock_vmc_request_call_api.return_value = expected_response
    assert (
        vmc_networks.update(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            network_id="network_id",
            verify_ssl=False,
        )
        == expected_response
    )


def test_update_network_when_api_returns_no_network_with_given_id(mock_vmc_request_call_api):
    expected_response = {"error": "Given Network does not exist"}
    mock_vmc_request_call_api.return_value = expected_response
    assert (
        vmc_networks.update(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            network_id="network_id",
            verify_ssl=False,
        )
        == expected_response
    )


def test_update_network_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/tier-1s/cgw/segments/network_id"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_networks.update(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            network_id="network_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[5][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.PATCH_REQUEST_METHOD


@pytest.mark.parametrize(
    "actual_args, expected_payload",
    [
        # all actual args are None
        (
            {},
            {
                "subnets": None,
                "admin_state": None,
                "description": None,
                "domain_name": None,
                "tags": None,
                "advanced_config": None,
                "l2_extension": None,
                "dhcp_config_path": None,
                "display_name": None,
            },
        ),
        # allow none have values
        (
            {
                "tags": [{"tag": "tag1", "scope": "scope1"}],
                "subnets": [{"gateway_address": "40.1.1.1/16", "dhcp_ranges": ["40.1.2.0/24"]}],
            },
            {
                "subnets": [{"gateway_address": "40.1.1.1/16", "dhcp_ranges": ["40.1.2.0/24"]}],
                "admin_state": None,
                "description": None,
                "domain_name": None,
                "tags": [{"tag": "tag1", "scope": "scope1"}],
                "advanced_config": None,
                "l2_extension": None,
                "dhcp_config_path": None,
                "display_name": None,
            },
        ),
        # all args have values
        (
            {
                "subnets": [{"gateway_address": "40.1.1.1/16", "dhcp_ranges": ["40.1.2.0/24"]}],
                "admin_state": "UP",
                "description": "network segment",
                "domain_name": "net.eng.vmware.com",
                "tags": [{"tag": "tag1", "scope": "scope1"}],
                "advanced_config": {"address_pool_paths": [], "connectivity": "ON"},
                "l2_extension": None,
                "dhcp_config_path": "/infra/dhcp-server-configs/default",
                "display_name": "network_id",
            },
            {
                "subnets": [{"gateway_address": "40.1.1.1/16", "dhcp_ranges": ["40.1.2.0/24"]}],
                "admin_state": "UP",
                "description": "network segment",
                "domain_name": "net.eng.vmware.com",
                "tags": [{"tag": "tag1", "scope": "scope1"}],
                "advanced_config": {"address_pool_paths": [], "connectivity": "ON"},
                "l2_extension": None,
                "dhcp_config_path": "/infra/dhcp-server-configs/default",
                "display_name": "network_id",
            },
        ),
    ],
)
def test_assert_networks_update_should_correctly_filter_args(actual_args, expected_payload):
    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "network_id": "network_id",
        "verify_ssl": False,
    }
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        actual_args.update(common_actual_args)
        vmc_networks.update(**actual_args)

    call_kwargs = vmc_call_api.mock_calls[5][-1]
    assert call_kwargs["data"] == expected_payload
