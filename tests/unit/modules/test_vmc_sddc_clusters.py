"""
    Unit tests for vmc_sddc_clusters execution module
"""

import logging
from unittest.mock import patch

import pytest
from saltext.vmware.modules import vmc_sddc_clusters
from saltext.vmware.utils import vmc_constants

log = logging.getLogger(__name__)


@pytest.fixture
def cluster_data_by_id():
    data = {
        "clusters": [
            {
                "cluster_id": "e97920ae-1410-4269-9caa-29584eb8cf6d",
                "cluster_name": "Cluster-757-1",
                "cluster_state": "READY",
                "esx_host_list": [
                    {
                        "esx_id": "3ec306b9-c332-4af7-99d1-57b879791c13",
                        "name": "Not Really ESX9774568e-bf30-4ee8-96df-aaa4e7a77c94",
                        "hostname": "zerocloud.esx.local234f86df-4e1f-4153-b1aa-8b80a223219b",
                        "mac_address": "01-23-45-67-89-ab",
                        "provider": "ZEROCLOUD",
                        "esx_state": "READY",
                        "custom_properties": None,
                        "esx_credential": None,
                        "availability_zone": "us-west-2a",
                        "state_last_updated": "2021-06-04T13:15:11.050Z",
                        "ssh_check_failure_retry_time": 0,
                        "instance_type": "i3.metal",
                        "finger_print": None,
                        "instance_id": "31a8de4c-a344-419c-8c90-e1ef80ec38b6",
                        "durable_host_name": None,
                    },
                    {
                        "esx_id": "8e2c1d84-b555-483d-bbe0-425a27daf4a0",
                        "name": "Not Really ESX2653e249-e4f2-4db6-b33a-5c3064ff57e1",
                        "hostname": "zerocloud.esx.localac6a41e0-c2ce-4354-8c0f-8009411c4e77",
                        "mac_address": "01-23-45-67-89-ab",
                        "provider": "ZEROCLOUD",
                        "esx_state": "READY",
                        "custom_properties": None,
                        "esx_credential": None,
                        "availability_zone": "us-west-2a",
                        "state_last_updated": "2021-06-04T13:15:11.050Z",
                        "ssh_check_failure_retry_time": 0,
                        "instance_type": "i3.metal",
                        "finger_print": None,
                        "instance_id": "7c4cb1e8-dde0-4c86-a926-ff6a7c3a6d0a",
                        "durable_host_name": None,
                    },
                    {
                        "esx_id": "bd606586-0cff-4b15-8019-9b18bb8053e8",
                        "name": "Not Really ESX248b3033-a031-457a-9670-a28653cc9ee5",
                        "hostname": "zerocloud.esx.locala56d505c-bf77-4fe3-bc2f-f6f533e33a32",
                        "mac_address": "01-23-45-67-89-ab",
                        "provider": "ZEROCLOUD",
                        "esx_state": "READY",
                        "custom_properties": None,
                        "esx_credential": None,
                        "availability_zone": None,
                        "state_last_updated": "2021-06-28T12:15:54.587Z",
                        "ssh_check_failure_retry_time": 0,
                        "instance_type": "i3.metal",
                        "finger_print": None,
                        "instance_id": "b02e3a1f-dc42-4302-9da7-4e40e8f21392",
                        "durable_host_name": None,
                    },
                    {
                        "esx_id": "f8297b8c-7cdb-40ec-a156-1d63b1e66f2e",
                        "name": "Not Really ESX50148250-a597-4df0-b127-77038527c104",
                        "hostname": "zerocloud.esx.local71f8565a-7eba-4de8-835d-397fdb3f61b1",
                        "mac_address": "01-23-45-67-89-ab",
                        "provider": "ZEROCLOUD",
                        "esx_state": "READY",
                        "custom_properties": None,
                        "esx_credential": None,
                        "availability_zone": None,
                        "state_last_updated": "2021-06-29T12:42:12.332Z",
                        "ssh_check_failure_retry_time": 0,
                        "instance_type": "i3.metal",
                        "finger_print": None,
                        "instance_id": "f35ebb36-bb7e-49ab-bc56-154d742abfef",
                        "durable_host_name": None,
                    },
                ],
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
        ]
    }
    yield data


@pytest.fixture
def sddc_data_by_id(mock_vmc_request_call_api, cluster_data_by_id):
    data = {
        "user_id": "f0880137-ae17-3a09-a8e1-2bd1da0d4b5d",
        "user_name": "test@mvmware.com",
        "created": "2021-04-05T18:29:35.000705Z",
        "id": "f46eda60-c67c-4613-a7fe-526b87948cb7",
        "resource_config": {
            "vc_url": "https://vcenter.sddc-10-182-155-238.vmwarevmc.com/",
            "cloud_username": "cloudadmin@vmc.local",
            "cloud_password": "Z8OYrQhD-T3v-cw",
            "clusters": cluster_data_by_id,
        },
        "updated_by_user_id": "e05378ed-7c3d-3bfb-8129-9b5a554b8e50",
        "updated_by_user_name": "Internal-Operator",
        "updated": "2021-04-08T02:17:04.000000Z",
        "name": "CMBU-STG-NSXT-M12v6-04-05-21",
    }
    mock_vmc_request_call_api.return_value = data
    yield data


@pytest.fixture
def clusters_data(cluster_data_by_id):
    data = {"description": "vmc_sddc_clusters.list_", "clusters": cluster_data_by_id}
    yield data


@pytest.fixture
def primary_cluster_data(mock_vmc_request_call_api, cluster_data_by_id):
    data = cluster_data_by_id.get(0)
    mock_vmc_request_call_api.return_value = data
    yield data


def test_list_clusters_should_return_api_response(sddc_data_by_id, clusters_data):
    result = vmc_sddc_clusters.list_(
        hostname="hostname",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        org_id="org_id",
        sddc_id="sddc_id",
        verify_ssl=False,
    )
    assert result == clusters_data


def test_list_sddc_clusters_called_with_url():
    expected_url = "https://hostname/vmc/api/orgs/org_id/sddcs/sddc_id"
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_sddc_clusters.list_(
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


def test_list_sddc_clusters_fail_with_error(mock_vmc_request_call_api):
    expected_response = {"error": "Given SDDC does not exist"}
    mock_vmc_request_call_api.return_value = expected_response
    result = vmc_sddc_clusters.list_(
        hostname="hostname",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        org_id="org_id",
        sddc_id="wrong_sddc_id",
        verify_ssl=False,
    )
    assert "error" in result


def test_create_cluster_when_api_should_return_api_response(
    mock_vmc_request_call_api,
):
    expected_response = {"message": "Cluster created successfully"}
    mock_vmc_request_call_api.return_value = expected_response
    assert (
        vmc_sddc_clusters.create(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            num_hosts=1,
            host_cpu_cores_count=1,
            host_instance_type=" i3.metal",
            storage_capacity=1,
            verify_ssl=False,
        )
        == expected_response
    )


def test_create_cluster_called_with_url():
    expected_url = "https://hostname/vmc/api/orgs/org_id/sddcs/sddc_id/clusters"
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_sddc_clusters.create(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            num_hosts=1,
            host_cpu_cores_count=1,
            host_instance_type=" i3.metal",
            storage_capacity=1,
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.POST_REQUEST_METHOD


def test_get_primary_cluster_should_return_single_cluster(primary_cluster_data):
    result = vmc_sddc_clusters.get_primary(
        hostname="hostname",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        org_id="org_id",
        sddc_id="sddc_id",
        verify_ssl=False,
    )
    assert result == primary_cluster_data


def test_get_primary_cluster_called_with_url():
    expected_url = "https://hostname/vmc/api/orgs/org_id/sddcs/sddc_id/primarycluster"
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_sddc_clusters.get_primary(
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


def test_delete_cluster_when_api_should_return_api_response(
    mock_vmc_request_call_api,
):
    expected_response = {"message": "Cluster deleted successfully"}
    mock_vmc_request_call_api.return_value = expected_response
    assert (
        vmc_sddc_clusters.delete(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            cluster_id="cluster_id",
            verify_ssl=False,
        )
        == expected_response
    )


def test_delete_cluster_when_api_should_return_error_when_cluster_is_in_maintenance(
    mock_vmc_request_call_api,
):
    expected_response = {
        "message": "Cluster is currently not in a state where it can be deleted. Please try once the status is READY or FAILED."
    }
    mock_vmc_request_call_api.return_value = expected_response
    assert (
        vmc_sddc_clusters.delete(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            cluster_id="cluster_id",
            verify_ssl=False,
        )
        == expected_response
    )


def test_delete_cluster_called_with_url():
    expected_url = "https://hostname/vmc/api/orgs/org_id/sddcs/sddc_id/clusters/cluster_id"
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_sddc_clusters.delete(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            cluster_id="cluster_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.DELETE_REQUEST_METHOD
