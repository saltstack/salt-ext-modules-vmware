from unittest.mock import create_autospec
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_sddc as vmc_sddc_exec
import saltext.vmware.states.vmc_sddc as vmc_sddc

_sddc_data = [
    {
        "user_id": "f0880137-ae17-3a09-a8e1-2bd1da0d4b5d",
        "user_name": "test@mvmware.com",
        "created": "2021-04-05T18:29:35.000705Z",
        "version": 54,
        "id": "testSDDC1",
        "updated_by_user_id": "e05378ed-7c3d-3bfb-8129-9b5a554b8e50",
        "updated_by_user_name": "Internal-Operator",
        "updated": "2021-04-08T02:17:04.000000Z",
        "name": "sddc-123",
        "provider": "AWS",
        "resource_config": {},
        "sddc_state": "READY",
        "sddc_access_state": "ENABLED",
        "account_link_state": None,
        "sddc_type": None,
        "expiration_date": None,
        "sddc_template_id": None,
        "nsxt_csp_mode": True,
        "org_id": "a0c6eb59-66c8-4b70-93df-f578f3b7ea3e",
    }
]


_sddcs_data = [
    _sddc_data[0],
    {
        "user_id": "f0880137-ae17-3a09-a8e1-2bd1da0d4b5d",
        "user_name": "test@mvmware.com",
        "created": "2021-04-05T18:29:35.000705Z",
        "version": 54,
        "id": "testSDDC2",
        "updated_by_user_id": "e05378ed-7c3d-3bfb-8129-9b5a554b8e50",
        "updated_by_user_name": "Internal-Operator",
        "updated": "2021-04-08T02:17:04.000000Z",
        "name": "sddc-098",
        "provider": "AWS",
        "resource_config": {},
        "sddc_state": "READY",
        "sddc_access_state": "ENABLED",
        "account_link_state": None,
        "sddc_type": None,
        "expiration_date": None,
        "sddc_template_id": None,
        "nsxt_csp_mode": True,
        "org_id": "a0c6eb59-66c8-4b70-93df-f578f3b7ea3e",
    },
]


@pytest.fixture
def mocked_ok_response():
    response = {
        "user_id": "ff9379d5-c011-3719-95d2-5b92618de670",
        "user_name": "prjain@vmware.com",
        "created": "2022-04-28T10:41:58.000521Z",
        "version": 40,
        "id": "c2f3f894-a1f6-46de-a983-f5d3466f7346",
        "updated_by_user_id": "ff9379d5-c011-3719-95d2-5b92618de670",
        "updated_by_user_name": "prjain@vmware.com",
        "updated": "2022-04-28T10:43:25.000000Z",
        "name": "prerna-new-sddc-1",
        "provider": "ZEROCLOUD",
        "resource_config": {
            "sddc_id": "c2f3f894-a1f6-46de-a983-f5d3466f7346",
            "region": "US_WEST_2",
            "public_ip_pool": [],
            "agents": [
                {
                    "provider": "ZEROCLOUD",
                    "id": "0190fa0a-4b25-4b77-bca8-fd23f531f06f",
                    "agent_url": "https://zerocloud.agent.local/",
                    "reserved_ip": "127.0.0.1",
                    "internal_ip": "127.0.0.1",
                    "management_ip": None,
                    "network_gateway": "127.0.0.1",
                    "network_netmask": "255.255.255.0",
                    "network_cidr": "127.0.0.1/24",
                    "custom_properties": None,
                    "healthy": False,
                    "last_health_status_change": None,
                    "addresses": [],
                    "cert_enabled": False,
                    "hostname_verifier_enabled": True,
                    "agent_state": "DELETED",
                    "kms_key_id": None,
                    "tinyproxy_whitelist": None,
                    "tenant_service_info": {"s3_log_bucket_arn": ""},
                    "sddc_csp_oauth_client": None,
                    "master": True,
                }
            ],
            "sddc_manifest": {
                "esx_ami": {
                    "id": "ami-1a2b3c4d",
                    "region": "us-west-2",
                    "instance_type": "i3.metal",
                },
                "glcm_bundle": {"id": "1234", "s3_bucket": "s3-bucket"},
                "metadata": {"cycle_id": "Cycle-20", "timestamp": "1499881173421"},
                "vmc_version": "1.16",
                "vmc_internal_version": "1.16.0.1",
                "pop_info": {
                    "id": "be71c864-54e3-4093-b3c0-c1f987ccfb72",
                    "created_at": "2022-04-28T10:41:59.000066Z",
                    "ami_infos": {
                        "Dummy": {"id": "ZeroCloudAmiId", "name": "ZeroCloudAmi", "type": "POP"}
                    },
                },
                "ebs_backed_vsan_config": {"instance_type": "r5.metal"},
            },
            "pop_agent_xeni_connection": None,
            "esx_hosts": [
                {
                    "esx_id": "42b44ff9-cadb-4fa1-bff4-7b01a302400b",
                    "name": "Not Really ESX977321ac-ab39-445e-86d9-61072446e0a3",
                    "hostname": "zerocloud.esx.local92d57945-12c8-46e9-8277-d26290eec774",
                    "mac_address": "01-23-45-67-89-ab",
                    "provider": "ZEROCLOUD",
                    "esx_state": "READY",
                    "custom_properties": {},
                    "esx_credential": None,
                    "availability_zone": "us-west-2a",
                    "state_last_updated": "2022-04-28T10:42:03.135Z",
                    "ssh_check_failure_retry_time": 0,
                    "instance_type": "i3.metal",
                    "finger_print": None,
                    "instance_id": "fa4055b8-39fa-4dc0-a907-04261d5b609f",
                    "durable_host_name": None,
                }
            ],
            "custom_properties": {"DELETE": "0465642c-c236-4625-83df-5545a7cd9274"},
            "vpc_info": {
                "provider": "ZEROCLOUD",
                "network_type": "AWS_SIMPLE",
                "id": "vpc-zero-mocked-vpc-id",
                "vpc_cidr": "10.2.0.0/16",
                "ipv6_vpc_cidr": None,
                "route_table_id": "rtb-zero-mocked-route-table",
                "internet_gateway_id": "igw-zero-mocked-igw-id",
                "subnet_id": None,
                "association_id": None,
                "api_subnet_id": None,
                "api_association_id": None,
                "edge_subnet_id": None,
                "edge_association_id": None,
                "private_subnet_id": None,
                "private_association_id": None,
                "security_group_id": None,
                "esx_security_group_id": None,
                "esx_public_security_group_id": None,
                "vm_security_group_id": None,
                "peering_connection_id": None,
                "default_key_pair": None,
                "vgw_id": "vgw-id-zero-mocked",
                "vif_ids": [],
                "vgw_route_table_id": "rtb-vgw-zero-mocked",
                "tgw_ips": None,
                "traffic_group_edge_vm_ips": None,
                "available_zones": [],
                "routetables": {
                    "localTable": {"name": "localTable", "id": "rtb-zero-mocked-route-table"},
                    "vgwTable": {"name": "vgwTable", "id": "rtb-vgw-zero-mocked"},
                },
                "vcdr_enis": None,
                "prefix_lists": None,
                "created": False,
                "witness_az": {"id": None, "subnets": []},
            },
            "vc_ip": "https://skyscraper-97.skyscraper.dmz.onecloud/vsphere-s3Client",
            "vc_url": "https://skyscraper-97.skyscraper.dmz.onecloud/vsphere-s3Client",
            "vc_instance_id": None,
            "psc_ip": "https://skyscraper-190.skyscraper.dmz.onecloud/vsphere-s3Client",
            "psc_url": "https://skyscraper-190.skyscraper.dmz.onecloud/vsphere-s3Client",
            "nsx_mgr_ip": "https://nsxManager.None/",
            "nsx_mgr_url": "https://nsxManager.None/",
            "nsx_mgr_login_url": "https://nsxManager.None/login.jsp",
            "vc_management_ip": "127.0.0.5",
            "nfs_mode": False,
            "vc_public_ip": None,
            "vc_containerized_permissions_enabled": True,
            "vc_remote_plugin_support_enabled": True,
            "psc_management_ip": "127.0.0.5",
            "nsx_mgr_management_ip": "127.0.0.6",
            "nsx_controller_ips": None,
            "vxlan_subnet": "192.168.1.0/24",
            "skip_creating_vxlan": False,
            "cgws": [],
            "mgw_id": "",
            "sddc_networks": [],
            "provider": "ZEROCLOUD",
            "esx_cluster_id": None,
            "sso_domain": "vmc.local",
            "admin_username": "admin",
            "admin_password": "admin",
            "temp_vc_admin_password": None,
            "cloud_username": "clouduser@vmc.local",
            "cloud_password": "dummy_password",
            "cloud_user_group": None,
            "nsx_manager_username": None,
            "nsx_manager_password": None,
            "nsx_manager_audit_username": None,
            "nsx_manager_audit_password": None,
            "nsx_cloud_admin": "cloud_admin",
            "nsx_cloud_admin_password": "XOqU!At3!dHuD7e",
            "nsx_cloud_audit": "cloud_audit",
            "nsx_cloud_audit_password": "Iwn5F!HKqpA5!bV",
            "root_nsx_controller_password": None,
            "root_nsx_edge_password": None,
            "nsx_proxy_username": None,
            "nsx_proxy_password": None,
            "sddc_manager_credentials": None,
            "new_nsx_credentials": None,
            "management_rp": None,
            "management_ds": None,
            "vc_ssh_credential": None,
            "sub_domain": None,
            "nsx_reverse_proxy_url": None,
            "nsx_api_public_endpoint_url": None,
            "key_provider_data": None,
            "vc_csp_login_status": None,
            "vc_break_glass_url": None,
            "certificates": {},
            "management_vms": {},
            "dns_with_management_vm_private_ip": False,
            "fleet_management_queue_user": None,
            "fleet_management_queue_password": None,
            "fleet_management_username": None,
            "fleet_management_password": None,
            "perf_agent_svc_username": None,
            "perf_agent_svc_password": None,
            "backup_restore_vc_username": None,
            "backup_restore_vc_password": None,
            "clusters": [
                {
                    "cluster_id": "798e91a8-0361-4f28-8ecf-4e9ddeb06d9e",
                    "cluster_name": "Cluster-1",
                    "cluster_state": "READY",
                    "esx_host_list": [
                        {
                            "esx_id": "42b44ff9-cadb-4fa1-bff4-7b01a302400b",
                            "name": "Not Really ESX977321ac-ab39-445e-86d9-61072446e0a3",
                            "hostname": "zerocloud.esx.local92d57945-12c8-46e9-8277-d26290eec774",
                            "mac_address": "01-23-45-67-89-ab",
                            "provider": "ZEROCLOUD",
                            "esx_state": "READY",
                            "custom_properties": {},
                            "esx_credential": None,
                            "availability_zone": "us-west-2a",
                            "state_last_updated": "2022-04-28T10:42:03.135Z",
                            "ssh_check_failure_retry_time": 0,
                            "instance_type": "i3.metal",
                            "finger_print": None,
                            "instance_id": "fa4055b8-39fa-4dc0-a907-04261d5b609f",
                            "durable_host_name": None,
                        }
                    ],
                    "vsan_witness": None,
                    "volume_list": [],
                    "diskgroup_list": [],
                    "aws_kms_info": None,
                    "host_cpu_cores_count": 0,
                    "hyper_threading_enabled": False,
                    "esx_host_info": {"instance_type": "i3.metal"},
                    "cluster_capacity": {
                        "number_of_sockets": 2,
                        "total_number_of_cores": 36,
                        "cpu_capacity_ghz": 82.8,
                        "memory_capacity_gib": 512,
                        "number_of_ssds": 8,
                        "storage_capacity_gib": 10617,
                    },
                    "partition_placement_group_info": [
                        {
                            "availability_zone": "us-west-2",
                            "partition_group_names": [
                                "partition-pg-0-798e91a8-0361-4f28-8ecf-4e9ddeb06d9e"
                            ],
                        }
                    ],
                    "msft_license_config": {
                        "windows_licensing": None,
                        "mssql_licensing": None,
                        "academic_license": False,
                    },
                    "wcp_details": None,
                    "storage_capacity": 10617,
                }
            ],
            "deployment_type": "SINGLE_AZ",
            "availability_zones": ["us-west-2a"],
            "witness_availability_zone": "us-west-2a",
            "vlcm_enabled": False,
            "cvds_enabled": False,
            "edge_lcm_enabled": False,
            "esx_host_subnet": "127.0.0.1/28",
            "mgmt_appliance_network_name": None,
            "mgmt_appliance_connectivity_logical_switch_id": None,
            "nsxt_addons": None,
            "sddc_security": {"profile": "NONE", "hardened": False},
            "vc_oauth_client": None,
            "nsx_native_client": None,
            "vuln_scanner_admin_user": None,
            "vuln_scanner_password": None,
            "sddc_size": {"vc_size": "medium", "nsx_size": "small", "size": "NSX_SMALL"},
            "msft_license_config": None,
            "outpost_config": None,
            "ipv6_enabled": None,
            "max_num_public_ip": 30,
            "mgw_public_ip_pool": [],
            "intermediate_ip_pool": None,
            "zero_cloud_region": "US_WEST_2",
            "agent": {
                "provider": "ZEROCLOUD",
                "id": "0190fa0a-4b25-4b77-bca8-fd23f531f06f",
                "agent_url": "https://zerocloud.agent.local/",
                "reserved_ip": "127.0.0.1",
                "internal_ip": "127.0.0.1",
                "management_ip": None,
                "network_gateway": "127.0.0.1",
                "network_netmask": "255.255.255.0",
                "network_cidr": "127.0.0.1/24",
                "custom_properties": None,
                "healthy": False,
                "last_health_status_change": None,
                "addresses": [],
                "cert_enabled": False,
                "hostname_verifier_enabled": True,
                "agent_state": "DELETED",
                "kms_key_id": None,
                "tinyproxy_whitelist": None,
                "tenant_service_info": {"s3_log_bucket_arn": ""},
                "sddc_csp_oauth_client": None,
                "master": True,
            },
            "pop_xeni_connected": False,
            "non_master_agents": [],
            "mgmt_appliance_connectivity_enabled": False,
            "nsxt": False,
            "vswitch_name": "vSwitch0",
            "sddc_desired_state": True,
        },
        "sddc_state": "ACTIVE",
        "sddc_access_state": "ENABLED",
        "account_link_state": None,
        "sddc_type": "1NODE",
        "expiration_date": "2022-06-27T10:41:58.000521Z",
        "sddc_template_id": None,
        "nsxt_csp_mode": False,
        "org_id": "10e1092f-51d0-473a-80f8-137652fd0c39",
    }
    return response


@pytest.fixture
def mocked_error_response():
    error_response = {
        "error": "The credentials were incorrect or the account specified has been locked."
    }
    return error_response


@pytest.fixture
def configure_loader_modules():
    return {vmc_sddc: {}}


def test_absent_state_to_delete_when_module_returns_success_response(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_sddc_exec.get_by_id, return_value=mocked_ok_response
    )
    mock_delete_response = create_autospec(
        vmc_sddc_exec.delete,
        ok=True,
        return_value="SDDC Deleted Successfully",
    )
    sddc_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_sddc.__salt__,
        {
            "vmc_sddc.get_by_id": mock_get_by_id_response,
            "vmc_sddc.delete": mock_delete_response,
        },
    ):
        result = vmc_sddc.absent(
            name=sddc_id,
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            force_delete=False,
            retain_configuration=False,
            template_name=None,
        )

    assert result is not None
    assert result["changes"] == {"new": None, "old": mocked_ok_response}
    assert result["comment"] == "Deleted SDDC {}".format(sddc_id)
    assert result["result"]


def test_absent_state_when_object_to_delete_does_not_exists(mocked_ok_response):
    mock_get_by_id_response = create_autospec(vmc_sddc_exec.get_by_id, return_value={})
    sddc_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_sddc.__salt__,
        {"vmc_sddc.get_by_id": mock_get_by_id_response},
    ):
        result = vmc_sddc.absent(
            name=sddc_id,
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            force_delete=False,
            retain_configuration=False,
            template_name=None,
        )

    assert result is not None
    assert result["changes"] == {}
    assert result[
        "comment"
    ] == "No SDDC found with ID {} or deletion is already in progress or SDDC is still deploying".format(
        sddc_id
    )
    assert result["result"]


def test_absent_state_to_delete_when_opts_test_mode_is_true(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_sddc_exec.get_by_id,
        return_value={"results": [mocked_ok_response]},
    )
    sddc_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_sddc.__salt__,
        {"vmc_sddc.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_sddc.__opts__, {"test": True}):
            result = vmc_sddc.absent(
                name=sddc_id,
                hostname="hostname",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                force_delete=False,
                retain_configuration=False,
                template_name=None,
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "State absent will delete SDDC with ID {}".format(sddc_id)
    assert result["result"] is None


def test_absent_state_when_object_to_delete_does_not_exists_and_opts_test_mode_is_true(
    mocked_ok_response,
):
    mock_get_by_id_response = create_autospec(vmc_sddc_exec.get_by_id, return_value={})
    sddc_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_sddc.__salt__,
        {"vmc_sddc.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_sddc.__opts__, {"test": True}):
            result = vmc_sddc.absent(
                name=sddc_id,
                hostname="hostname",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                force_delete=False,
                retain_configuration=False,
                template_name=None,
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result[
        "comment"
    ] == "State absent will do nothing as no SDDC found with ID {} or deletion is already in progress or SDDC is still deploying".format(
        sddc_id
    )
    assert result["result"] is None


def test_absent_with_error_from_delete(mocked_ok_response, mocked_error_response):
    mock_get_by_id = create_autospec(
        vmc_sddc_exec.get_by_id,
        return_value={"results": [mocked_ok_response]},
    )
    mock_delete = create_autospec(vmc_sddc_exec.delete, return_value=mocked_error_response)

    with patch.dict(
        vmc_sddc.__salt__,
        {
            "vmc_sddc.get_by_id": mock_get_by_id,
            "vmc_sddc.delete": mock_delete,
        },
    ):
        result = vmc_sddc.absent(
            name="sddc_id",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            force_delete=False,
            retain_configuration=False,
            template_name=None,
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_absent_state_when_error_from_get_by_id(mocked_ok_response, mocked_error_response):
    mock_get_by_id = create_autospec(vmc_sddc_exec.get_by_id, return_value=mocked_error_response)

    with patch.dict(
        vmc_sddc.__salt__,
        {"vmc_sddc.get_by_id": mock_get_by_id},
    ):
        result = vmc_sddc.absent(
            name="sddc_id",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            force_delete=False,
            retain_configuration=False,
            template_name=None,
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_state_when_error_from_getting_sddc_list(mocked_ok_response, mocked_error_response):
    mock_sddc_list = create_autospec(vmc_sddc_exec.list_, return_value=mocked_error_response)

    with patch.dict(
        vmc_sddc.__salt__,
        {"vmc_sddc.list": mock_sddc_list},
    ):
        result = vmc_sddc.present(
            name="sddc_name",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            num_hosts=1,
            provider="ZEROCLOUD",
            region="us-west-1",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "Failed to get SDDCs for given org : The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_state_when_error_from_create(mocked_error_response):
    mock_sddc_list = create_autospec(vmc_sddc_exec.list_, return_value={})
    mock_create = create_autospec(vmc_sddc_exec.create, return_value=mocked_error_response)

    with patch.dict(
        vmc_sddc.__salt__,
        {
            "vmc_sddc.list": mock_sddc_list,
            "vmc_sddc.create": mock_create,
        },
    ):
        result = vmc_sddc.present(
            name="sddc_name",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            num_hosts=1,
            provider="ZEROCLOUD",
            region="us-west-1",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "Failed to add SDDC : The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_to_create_when_module_returns_success_response(mocked_ok_response):
    mock_sddc_list = create_autospec(vmc_sddc_exec.list_, return_value={})
    mock_create_response = create_autospec(vmc_sddc_exec.create, return_value=mocked_ok_response)
    sddc_name = mocked_ok_response["id"]

    with patch.dict(
        vmc_sddc.__salt__,
        {
            "vmc_sddc.list": mock_sddc_list,
            "vmc_sddc.create": mock_create_response,
        },
    ):
        result = vmc_sddc.present(
            name=sddc_name,
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            num_hosts=1,
            provider="ZEROCLOUD",
            region="us-west-1",
        )

    assert result is not None
    assert result["changes"]["new"] == mocked_ok_response
    assert result["changes"]["old"] is None
    assert result["comment"] == "Created SDDC {}".format(sddc_name)
    assert result["result"]


def test_present_state_for_create_when_opts_test_is_true(mocked_ok_response):
    mock_sddc_list = create_autospec(vmc_sddc_exec.list_, return_value={})
    sddc_name = mocked_ok_response["name"]

    with patch.dict(
        vmc_sddc.__salt__,
        {"vmc_sddc.list": mock_sddc_list},
    ):
        with patch.dict(vmc_sddc.__opts__, {"test": True}):
            result = vmc_sddc.present(
                name=sddc_name,
                hostname="hostname",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                num_hosts=1,
                provider="ZEROCLOUD",
                region="us-west-1",
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "SDDC {} would have been created".format(sddc_name)
    assert result["result"] is None


@pytest.mark.parametrize(
    "actual_args",
    [
        # all actual args are None
        ({}),
        # all args have values
        (
            {
                "account_link_config": {"delay_account_link": False},
                "account_link_sddc_config": [
                    {"connected_account_id": "123", "customer_subnet_ids": ["awx:qee:asd"]}
                ],
                "deployment_type": "SingleAZ",
                "host_instance_type": "i3.metal",
                "msft_license_config": {"mssql_licensing": "string", "windows_licensing": "string"},
                "sddc_id": "sddc_id",
                "sddc_template_id": "temp-123",
                "sddc_type": "OneNode",
                "size": "medium",
                "skip_creating_vxlan": False,
                "sso_domain": "domain",
                "storage_capacity": 1,
                "vpc_cidr": "vpc",
                "vxlan_subnet": "subnet",
                "validate_only": False,
            }
        ),
    ],
)
def test_present_state_during_create_should_correctly_pass_args(mocked_ok_response, actual_args):
    mock_sddc_list = create_autospec(vmc_sddc_exec.list_, return_value={})
    mock_create_response = mocked_ok_response.copy()

    common_actual_args = {
        "num_hosts": 4,
        "provider": "ZEROCLOUD",
        "region": "us-east-1",
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "verify_ssl": False,
    }

    mock_create_response.update(actual_args)
    actual_args.update(common_actual_args)
    mock_create = create_autospec(vmc_sddc_exec.create, return_value=mock_create_response)

    with patch.dict(
        vmc_sddc.__salt__,
        {
            "vmc_sddc.list": mock_sddc_list,
            "vmc_sddc.create": mock_create,
        },
    ):
        result = vmc_sddc.present(name=mocked_ok_response["name"], **actual_args)

    call_kwargs = mock_create.mock_calls[0][-1]

    subset = {k: v for k, v in call_kwargs.items() if k in actual_args}
    assert subset == actual_args

    assert result is not None
    assert result["changes"]["old"] is None
    assert result["changes"]["new"] == mock_create_response
    assert result["comment"] == "Created SDDC {}".format(mocked_ok_response["name"])
    assert result["result"]
