"""
    :codeauthor: VMware
"""
import logging
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_sddc as vmc_sddc
from saltext.vmware.utils import vmc_constants

log = logging.getLogger(__name__)


@pytest.fixture
def sddc_data_by_id(mock_vmc_request_call_api):
    data = {
        "user_id": "f0880137-ae17-3a09-a8e1-2bd1da0d4b5d",
        "user_name": "test@mvmware.com",
        "created": "2021-04-05T18:29:35.000705Z",
        "version": 54,
        "id": "f46eda60-c67c-4613-a7fe-526b87948cb7",
        "resource_config": {
            "vc_url": "https://vcenter.hostname.com/",
            "cloud_username": "cloudadmin@vmc.local",
            "cloud_password": "Z8OYrQhD-T3v-cw",
        },
        "updated_by_user_id": "e05378ed-7c3d-3bfb-8129-9b5a554b8e50",
        "updated_by_user_name": "Internal-Operator",
        "updated": "2021-04-08T02:17:04.000000Z",
        "name": "CMBU-STG-NSXT-M12v6-04-05-21",
        "provider": "AWS",
        "sddc_state": "READY",
        "sddc_access_state": "ENABLED",
        "account_link_state": None,
        "sddc_type": None,
        "expiration_date": None,
        "sddc_template_id": None,
        "nsxt_csp_mode": True,
        "org_id": "a0c6eb59-66c8-4b70-93df-f578f3b7ea3e",
    }
    mock_vmc_request_call_api.return_value = data
    yield data


@pytest.fixture
def sddc_data(mock_vmc_request_call_api, sddc_data_by_id):
    data = [sddc_data_by_id, sddc_data_by_id]
    mock_vmc_request_call_api.return_value = data
    yield data


@pytest.fixture()
def vcenter_data():
    vcenter_data = {
        "description": "vmc_sddc.get_vcenter_detail",
        "vcenter_detail": {
            "vcenter_url": "https://vcenter.hostname.com/",
            "username": "cloudadmin@vmc.local",
            "password": "Z8OYrQhD-T3v-cw",
        },
    }
    yield vcenter_data


@pytest.fixture()
def vm_data(mock_vmc_vcenter_request_call_api):
    vms_data = [
        {
            "memory_size_MiB": 24576,
            "vm": "vm-36",
            "name": "NSX-Manager-0",
            "power_state": "POWERED_ON",
            "cpu_count": 4,
        },
        {
            "memory_size_MiB": 8192,
            "vm": "vm-37",
            "name": "NSX-Edge-0",
            "power_state": "POWERED_ON",
            "cpu_count": 4,
        },
    ]
    mock_vmc_vcenter_request_call_api.return_value = vms_data
    yield vms_data


def test_get_sddc_should_return_api_response(sddc_data):
    result = vmc_sddc.get(
        hostname="hostname",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        org_id="org_id",
        include_deleted=False,
        verify_ssl=False,
    )
    assert result == sddc_data


def test_get_sddc_called_with_url():
    expected_url = "https://hostname/vmc/api/orgs/org_id/sddcs"
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_sddc.get(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            include_deleted=False,
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.GET_REQUEST_METHOD


def test_get_sddc_by_id_should_return_single_sddc(sddc_data_by_id):
    result = vmc_sddc.get_by_id(
        hostname="hostname",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        org_id="org_id",
        sddc_id="sddc_id",
        verify_ssl=False,
    )
    assert result == sddc_data_by_id


def test_get_sddc_by_id_called_with_url():
    expected_url = "https://hostname/vmc/api/orgs/org_id/sddcs/sddc_id"
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_sddc.get_by_id(
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


def test_create_sddc_when_api_should_return_api_response(
    mock_vmc_request_call_api,
):
    expected_response = {"message": "SDDC created successfully"}
    mock_vmc_request_call_api.return_value = expected_response

    assert (
        vmc_sddc.create(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_name="test-sddc",
            num_hosts=1,
            provider="provider",
            region="region",
            verify_ssl=False,
        )
        == expected_response
    )


def test_create_sddc_called_with_url():
    expected_url = "https://hostname/vmc/api/orgs/org_id/sddcs"
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_sddc.create(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_name="test-sddc",
            num_hosts=1,
            provider="provider",
            region="region",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.POST_REQUEST_METHOD


def test_delete_sddc_when_api_should_return_api_response(
    mock_vmc_request_call_api,
):
    expected_response = {"message": "SDDC deleted successfully"}
    mock_vmc_request_call_api.return_value = expected_response
    assert (
        vmc_sddc.delete(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
        == expected_response
    )


def test_delete_sddc_called_with_url():
    expected_url = "https://hostname/vmc/api/orgs/org_id/sddcs/sddc_id"
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_sddc.delete(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.DELETE_REQUEST_METHOD


def test_update_sddc_when_api_should_return_api_response(
    mock_vmc_request_call_api,
):
    expected_response = {"message": "SDDC updated successfully"}
    mock_vmc_request_call_api.return_value = expected_response
    assert (
        vmc_sddc.update_name(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            sddc_new_name="sddc_new_name",
            verify_ssl=False,
        )
        == expected_response
    )


def test_update_sddc_called_with_expected_kwargs():
    expected_url = "https://hostname/vmc/api/orgs/org_id/sddcs/sddc_id"
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_sddc.update_name(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            sddc_new_name="sddc_new_name",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.PATCH_REQUEST_METHOD


@pytest.mark.parametrize(
    "actual_args, expected_payload",
    [
        # allow args have None - NA
        (
            {
                "sddc_new_name": None,
            },
            {
                "name": None,
            },
        ),
        # all args have values
        (
            {
                "sddc_new_name": "sddc_new",
            },
            {
                "name": "sddc_new",
            },
        ),
    ],
)
def test_assert_sddc_update_should_correctly_filter_args(actual_args, expected_payload):
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
        vmc_sddc.update_name(**actual_args)

    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["data"] == expected_payload


def test_get_vcenter_detail_should_return_api_response(sddc_data_by_id, vcenter_data):
    result = vmc_sddc.get_vcenter_detail(
        hostname="hostname",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        org_id="org_id",
        sddc_id="sddc_id",
        verify_ssl=False,
    )

    assert result == vcenter_data


def test_get_vcenter_detail_called_with_url():
    expected_url = "https://hostname/vmc/api/orgs/org_id/sddcs/sddc_id"
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_sddc.get_vcenter_detail(
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


def test_get_vcenter_detail_fail_with_error(mock_vmc_request_call_api):
    expected_response = {"error": "Given SDDC does not exist"}
    mock_vmc_request_call_api.return_value = expected_response
    result = vmc_sddc.get_vcenter_detail(
        hostname="hostname",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        org_id="org_id",
        sddc_id="sddc_d",
        verify_ssl=False,
    )
    assert "error" in result


def test_get_vms_by_sddc_id_should_return_api_response(
    mock_vcenter_headers, sddc_data_by_id, vm_data
):
    result = vmc_sddc.get_vms_by_sddc_id(
        hostname="hostname",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        org_id="org_id",
        sddc_id="sddc_id",
        verify_ssl=False,
    )
    assert result == vm_data


def test_get_vms_by_sddc_id_called_with_url(mock_vcenter_headers, sddc_data_by_id, vcenter_data):
    expected_url = "https://vcenter.hostname.com/api/vcenter/vm"
    with patch(
        "saltext.vmware.utils.vmc_vcenter_request.call_api", autospec=True
    ) as vmc_vcenter_request_call_api:
        vmc_sddc.get_vms_by_sddc_id(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_vcenter_request_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.GET_REQUEST_METHOD


def test_get_vms_by_sddc_id_fail_with_error(mock_vmc_request_call_api):
    expected_response = {"error": "Given SDDC does not exist"}
    mock_vmc_request_call_api.return_value = expected_response
    result = vmc_sddc.get_vms_by_sddc_id(
        hostname="hostname",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        org_id="org_id",
        sddc_id="sddc_d",
        verify_ssl=False,
    )
    assert "error" in result


def test_get_vms_should_return_api_response(mock_vcenter_headers, vm_data):
    result = vmc_sddc.get_vms(
        hostname="hostname",
        username="username",
        password="password",
        verify_ssl=False,
    )
    assert result == vm_data


def test_get_vms_called_with_url(mock_vcenter_headers):
    expected_url = "https://hostname/api/vcenter/vm"
    with patch(
        "saltext.vmware.utils.vmc_vcenter_request.call_api", autospec=True
    ) as vmc_vcenter_request_call_api:
        vmc_sddc.get_vms(
            hostname="hostname",
            username="username",
            password="password",
            verify_ssl=False,
        )
    call_kwargs = vmc_vcenter_request_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.GET_REQUEST_METHOD
