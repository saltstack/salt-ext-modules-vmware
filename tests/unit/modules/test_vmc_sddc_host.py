"""
    Unit tests for vmc_sddc_host execution module
"""

import logging
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_sddc_host as vmc_sddc_host
from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request

log = logging.getLogger(__name__)


@pytest.fixture
def host_data():
    data = [
        {
            "esx_id": "f5437b89-3360-444c-ab14-3332e32e03cd",
            "name": "Not Really ESX3ddaf75e-a570-40d3-a470-52b17eff8eb7",
            "hostname": "zerocloud.esx.localff020345-3ce0-4fe6-b15a-c54d33df5ad3",
            "mac_address": "01-23-45-67-89-ab",
            "provider": "ZEROCLOUD",
            "esx_state": "READY",
            "custom_properties": None,
            "esx_credential": None,
            "availability_zone": "us-west-2a",
            "state_last_updated": "2021-04-19T16:34:55.157Z",
            "ssh_check_failure_retry_time": 0,
            "instance_type": "i3.metal",
            "finger_print": None,
            "instance_id": "ddae0fbb-257f-4fea-b9d5-a02b609db708",
            "durable_host_name": None,
        },
        {
            "esx_id": "8bba6fee-0db7-441e-a7fd-86cc4ecce480",
            "name": "Not Really ESX1d2259b4-0758-4dbc-8bf5-bd96e398e77a",
            "hostname": "zerocloud.esx.localb1d2325b-8dad-4e41-a7b1-c735d7d62c51",
            "mac_address": "01-23-45-67-89-ab",
            "provider": "ZEROCLOUD",
            "esx_state": "READY",
            "custom_properties": None,
            "esx_credential": None,
            "availability_zone": None,
            "state_last_updated": "2021-04-19T16:38:27.686Z",
            "ssh_check_failure_retry_time": 0,
            "instance_type": "i3.metal",
            "finger_print": None,
            "instance_id": "25817091-8325-4948-8b5d-a373bbf1e67f",
            "durable_host_name": None,
        },
    ]
    yield data


@pytest.fixture
def hosts_data(host_data):
    data = {"description": "vmc_sddc_host.list_", "esx_hosts": host_data}
    yield data


@pytest.fixture
def sddc_data_by_id(mock_vmc_request_call_api, host_data):
    data = {
        "user_id": "f0880137-ae17-3a09-a8e1-2bd1da0d4b5d",
        "user_name": "test@mvmware.com",
        "created": "2021-04-05T18:29:35.000705Z",
        "id": "f46eda60-c67c-4613-a7fe-526b87948cb7",
        "resource_config": {
            "vc_url": "https://vcenter.sddc-10-182-155-238.vmwarevmc.com/",
            "cloud_username": "cloudadmin@vmc.local",
            "cloud_password": "Z8OYrQhD-T3v-cw",
            "clusters": [
                {
                    "cluster_id": "e97920ae-1410-4269-9caa-29584eb8cf6d",
                    "cluster_name": "Cluster-757-1",
                    "cluster_state": "READY",
                    "esx_host_list": host_data,
                    "vsan_witness": None,
                    "volume_list": None,
                    "diskgroup_list": None,
                    "aws_kms_info": None,
                    "host_cpu_cores_count": 0,
                    "hyper_threading_enabled": False,
                    "esx_host_info": {"instance_type": "i3.metal"},
                    "cluster_capacity": {
                        "number_of_sockets": 8,
                        "total_number_of_cores": 144,
                        "cpu_capacity_ghz": 331.2,
                        "memory_capacity_gib": 2048,
                        "number_of_ssds": 32,
                        "storage_capacity_gib": 42468,
                    },
                    "partition_placement_group_info": [
                        {
                            "availability_zone": "us-west-2",
                            "partition_group_names": [
                                "partition-pg-0-e97920ae-1410-4269-9caa-29584eb8cf6d"
                            ],
                        }
                    ],
                    "msft_license_config": None,
                    "wcp_details": None,
                    "storage_capacity": 42468,
                }
            ],
            "esx_hosts": host_data[0],
        },
        "updated_by_user_id": "e05378ed-7c3d-3bfb-8129-9b5a554b8e50",
        "updated_by_user_name": "Internal-Operator",
        "updated": "2021-04-08T02:17:04.000000Z",
        "name": "CMBU-STG-NSXT-M12v6-04-05-21",
    }
    mock_vmc_request_call_api.return_value = data
    yield data


def test_get_sddc_hosts_should_return_api_response(sddc_data_by_id, hosts_data):
    result = vmc_sddc_host.list_(
        hostname="hostname",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        org_id="org_id",
        sddc_id="sddc_id",
        verify_ssl=False,
    )
    assert result == hosts_data


def test_get_sddc_hosts_fail_with_error(mock_vmc_request_call_api):
    expected_response = {"error": "Given SDDC does not exist"}
    mock_vmc_request_call_api.return_value = expected_response
    result = vmc_sddc_host.list_(
        hostname="hostname",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        org_id="org_id",
        sddc_id="sddc_d",
        verify_ssl=False,
    )
    assert "error" in result


def test_get_sddc_called_with_url():
    expected_url = "https://hostname/vmc/api/orgs/org_id/sddcs/sddc_id"
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_sddc_host.list_(
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


def test_manage_esx_host_when_api_should_return_api_response(
    mock_vmc_request_call_api,
):
    expected_response = {"message": "Esx Host Added successfully"}
    mock_vmc_request_call_api.return_value = expected_response
    assert (
        vmc_sddc_host.manage(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            num_hosts=1,
            verify_ssl=False,
        )
        == expected_response
    )


def test_manage_esx_host_called_with_url():
    expected_url = "https://hostname/vmc/api/orgs/org_id/sddcs/sddc_id/esxs"
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_sddc_host.manage(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            num_hosts=1,
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.POST_REQUEST_METHOD


@pytest.mark.parametrize(
    "actual_args, expected_params",
    [
        # all actual args are None
        (
            {},
            {},
        ),
        # all actual args have param values
        (
            {"action": "add"},
            {"action": "add"},
        ),
    ],
)
def test_assert_manage_esx_host_should_correctly_filter_args(actual_args, expected_params):
    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "num_hosts": 1,
        "verify_ssl": False,
    }
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        actual_args.update(common_actual_args)
        vmc_sddc_host.manage(**actual_args)

    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["params"] == expected_params
