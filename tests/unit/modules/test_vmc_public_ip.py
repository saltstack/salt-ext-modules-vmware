"""
    Unit tests for vmc_public_ip execution module
    :codeauthor: VMware
"""
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_public_ip as vmc_public_ip
from saltext.vmware.utils import vmc_constants


@pytest.fixture
def public_ip_data_by_id(mock_vmc_request_call_api):
    data = {
        "id": "4ee86a7c-48af-48c8-a72e-2c6e8dbf3c9f",
        "display_name": "TEST_IP",
        "ip": "10.206.208.153",
        "marked_for_delete": False,
        "_create_time": 1618464918318,
        "_create_user": "pnaval@vmware.com",
        "_last_modified_time": 1618464919446,
        "_last_modified_user": "pnaval@vmware.com",
        "_protection": "UNKNOWN",
        "_revision": 1,
    }
    mock_vmc_request_call_api.return_value = data
    yield data


@pytest.fixture
def public_ip_data(mock_vmc_request_call_api, public_ip_data_by_id):
    data = {"result_count": 1, "results": [public_ip_data_by_id]}
    mock_vmc_request_call_api.return_value = data
    yield data


def test_get_public_ip_should_return_api_response(public_ip_data):
    assert (
        vmc_public_ip.get(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
        == public_ip_data
    )


def test_get_public_ips_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/"
        "cloud-service/api/v1/infra/public-ips"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        result = vmc_public_ip.get(
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


@pytest.mark.parametrize(
    "actual_args, expected_params",
    [
        # all actual args are None
        (
            {},
            {},
        ),
        # all actual args have few param values
        (
            {"page_size": 2},
            {"page_size": 2},
        ),
        # all actual args have all possible params
        (
            {"cursor": "00012", "page_size": 2, "sort_by": ["action"], "sort_ascending": True},
            {"cursor": "00012", "page_size": 2, "sort_by": ["action"], "sort_ascending": True},
        ),
    ],
)
def test_assert_get_public_ip_should_correctly_filter_args(actual_args, expected_params):
    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "verify_ssl": False,
    }
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        actual_args.update(common_actual_args)
        vmc_public_ip.get(**actual_args)

    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["params"] == expected_params


def test_get_public_ip_by_id_should_return_api_response(public_ip_data_by_id):
    assert (
        vmc_public_ip.get_by_id(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            public_ip_id="TEST_IP",
            verify_ssl=False,
        )
        == public_ip_data_by_id
    )


def test_get_public_ip_by_id_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/"
        "cloud-service/api/v1/infra/public-ips/TEST_IP"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        result = vmc_public_ip.get_by_id(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            public_ip_id="TEST_IP",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.GET_REQUEST_METHOD


def test_delete_public_ip_should_return_api_response(mock_vmc_request_call_api):
    data = {"message": "Public IP deleted successfully"}
    mock_vmc_request_call_api.return_value = data
    assert (
        vmc_public_ip.delete(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            public_ip_id="TEST_IP",
            verify_ssl=False,
        )
        == data
    )


def test_delete_public_ip_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/"
        "cloud-service/api/v1/infra/public-ips/TEST_IP"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        result = vmc_public_ip.delete(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            public_ip_id="TEST_IP",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.DELETE_REQUEST_METHOD
