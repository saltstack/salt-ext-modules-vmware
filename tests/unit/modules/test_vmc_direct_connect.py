"""
    Unit tests for vmc_direct_connect execution module
"""
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_direct_connect as vmc_direct_connect


@pytest.fixture
def direct_connect_account_data(mock_vmc_request_call_api):
    data = {"shadow_account": "891734487752"}
    mock_vmc_request_call_api.return_value = data
    yield data


@pytest.fixture
def direct_connect_associated_groups_data(mock_vmc_request_call_api):
    data = {"results": [], "result_count": 0}
    mock_vmc_request_call_api.return_value = data
    yield data


@pytest.fixture
def direct_connect_bgp_info(mock_vmc_request_call_api):
    data = {"local_as_num": "7224", "route_preference": "VPN_PREFERRED_OVER_DIRECT_CONNECT"}
    mock_vmc_request_call_api.return_value = data
    yield data


@pytest.fixture
def direct_connect_bgp_status(mock_vmc_request_call_api):
    data = {
        "intent_path": "/infra/direct-connect/bgp",
        "consolidated_status": {"consolidated_status": "SUCCESS"},
    }
    mock_vmc_request_call_api.return_value = data
    yield data


@pytest.fixture
def direct_connect_advertised_routes_data(mock_vmc_request_call_api):
    data = {
        "advertised_routes": [
            {"ipv4_cidr": "10.82.45.0/26", "advertisement_state": "SUCCESS"},
            {"ipv4_cidr": "10.82.45.128/25", "advertisement_state": "SUCCESS"},
        ],
        "failed_advertised_routes": 0,
    }
    mock_vmc_request_call_api.return_value = data
    yield data


@pytest.fixture
def direct_connect_learned_routes_data(mock_vmc_request_call_api):
    data = {"ipv4_cidr": ["0.0.0.0/0"]}
    mock_vmc_request_call_api.return_value = data
    yield data


@pytest.fixture
def direct_connect_vifs_data(mock_vmc_request_call_api):
    data = {
        "results": [
            {
                "id": "dxvif-fgni7mol",
                "name": "SEA03-DX-N9K01-CORP-026",
                "state": "ATTACHED",
                "direct_connect_id": "dxcon-fh5fv2rw",
                "bgp_status": "UP",
                "local_ip": "10.75.12.134",
                "remote_ip": "10.75.12.133",
                "mtu": 1500,
                "remote_asn": "65280",
            }
        ],
        "result_count": 1,
    }
    mock_vmc_request_call_api.return_value = data
    yield data


def test_get_accounts_should_return_api_response(direct_connect_account_data):
    assert (
        vmc_direct_connect.get_accounts(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
        == direct_connect_account_data
    )


def test_get_accounts_called_with_url():
    expected_url = "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/cloud-service/api/v1/infra/accounts"
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_direct_connect.get_accounts(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url


def test_get_associated_groups_should_return_api_response(direct_connect_associated_groups_data):
    assert (
        vmc_direct_connect.get_associated_groups(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
        == direct_connect_associated_groups_data
    )


def test_get_associated_groups_called_with_url():
    expected_url = "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/cloud-service/api/v1/infra/associated-groups/"
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_direct_connect.get_associated_groups(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url


def test_get_bgp_info_should_return_api_response(direct_connect_bgp_info):
    assert (
        vmc_direct_connect.get_bgp_info(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
        == direct_connect_bgp_info
    )


def test_get_bgp_info_called_with_url():
    expected_url = "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/cloud-service/api/v1/infra/direct-connect/bgp"
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_direct_connect.get_bgp_info(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url


def test_get_bgp_status_should_return_api_response(direct_connect_bgp_status):
    assert (
        vmc_direct_connect.get_bgp_status(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
        == direct_connect_bgp_status
    )


def test_get_bgp_status_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/cloud-service/api/"
        "v1/infra/realized-state/status?intent_path=/infra/direct-connect/bgp"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_direct_connect.get_bgp_status(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url


def test_get_advertised_routes_should_return_api_response(direct_connect_advertised_routes_data):
    assert (
        vmc_direct_connect.get_advertised_routes(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
        == direct_connect_advertised_routes_data
    )


def test_get_advertised_routes_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/cloud-service/api/v1/"
        "infra/direct-connect/routes/advertised"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_direct_connect.get_advertised_routes(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url


def test_get_learned_routes_should_return_api_response(direct_connect_learned_routes_data):
    assert (
        vmc_direct_connect.get_learned_routes(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
        == direct_connect_learned_routes_data
    )


def test_get_learned_routes_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/cloud-service/api/v1/"
        "infra/direct-connect/routes/learned"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_direct_connect.get_learned_routes(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url


def test_get_vifs_should_return_api_response(direct_connect_vifs_data):
    assert (
        vmc_direct_connect.get_vifs(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
        == direct_connect_vifs_data
    )


def test_get_vifs_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/cloud-service/api/v1/"
        "infra/direct-connect/vifs"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_direct_connect.get_vifs(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
