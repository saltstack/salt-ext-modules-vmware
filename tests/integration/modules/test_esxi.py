# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from unittest.mock import MagicMock

import pytest
import salt.exceptions
import saltext.vmware.modules.esxi as esxi
import saltext.vmware.utils.esxi


def test_esxi_get_lun_ids_should_return_lun_NAA_ids(service_instance, integration_test_config):
    expected_lun_ids = integration_test_config["esxi_datastore_disk_names"]
    actual_ids = esxi.get_lun_ids(service_instance=service_instance)
    assert actual_ids == expected_lun_ids


HOST_CAPABILITIES = [
        "accel3d_supported",
        "background_snapshots_supported",
        "checkpoint_ft_compatibility_issues",
        "checkpoint_ft_supported",
        "clone_from_snapshot_supported",
        "cpu_hw_mmu_supported",
        "cpu_memory_resource_configuration_supported",
        "crypto_supported",
        "datastore_principal_supported",
        "delta_disk_backings_supported",
        "eight_plus_host_vmfs_sharedAccess_supported",
        "encrypted_vmotion_supported",
        "encryption_cbrc_supported",
        "encryption_fault_tolerance_supported",
        "encryption_hbr_supported",
        "encryption_hot_operation_supported",
        "encryption_memory_save_supported",
        "encryption_rdm_supported",
        "encryption_vflash_supported",
        "encryption_with_snapshots_supported",
        "feature_capabilities_supported",
        "firewall_ip_rules_supported",
        "ft_compatibility_issues",
        "ft_supported",
        "gateway_on_nic_supported",
        "hbr_nic_selection_supported",
        "high_guest_mem_supported",
        "host_access_manager_supported",
        "inter_vm_communication_through_vmci_supported",
        "ipmi_supported",
        "iscsi_supported",
        "latency_sensitivity_supported",
        "local_swap_datastore_supported",
        "login_by_ssl_thumbprint_supported",
        "maintenance_mode_supported",
        "mark_as_local_supported",
        "mark_as_ssd_supported",
        "max_host_running_vms",
        "max_host_supported_vcpus",
        "max_num_disks_sv_motion",
        "max_registered_vms",
        "max_running_vms",
        "max_supported_vms",
        "max_supported_vcpus",
        "max_vcpus_per_ft_vm",
        "message_bus_proxy_supported",
        "multiple_network_stack_instance_supported",
        "nested_hv_supported",
        "nfs_41_krb5i_supported",
        "nfs_41_supported",
        "nfs_supported",
        "nic_teaming_supported",
        "one_k_volume_apis_supported",
        "per_vm_network_traffic_shaping_supported",
        "per_vm_swap_files",
        "pre_assigned_pci_unit_numbers_supported",
        "provisioning_nic_selection_supported",
        "reboot_supported",
        "record_replay_supported",
        "recursive_resource_pools_supported",
        "reliable_memory_aware",
        "replay_compatibility_issues",
        "replay_unsupported_reason",
        "restricted_snapshot_relocate_supported",
        "san_supported",
        "scaled_screenshot_supported",
        "scheduled_hardware_upgrade_supported",
        "screenshot_supported",
        "service_package_info_supported",
        "shutdown_supported",
        "smart_card_authentication_supported",
        "smp_ft_compatibility_issues",
        "smp_ft_supported",
        "snapshot_relayout_supported",
        "standby_supported",
        "storage_iorm_supported",
        "storage_policy_supported",
        "storage_vmotion_supported",
        "supported_vmfs_major_version",
        "suspended_relocate_supported",
        "tpm_supported",
        "turn_disk_locator_led_supported",
        "unshared_swap_vmotion_supported",
        "upit_supported",
        "vflash_supported",
        "vpmc_supported",
        "vstorage_capable",
        "virtual_exec_usage_supported",
        "virtual_volume_datastore_supported",
        "vlan_tagging_supported",
        "vm_direct_path_gen_2_supported",
        "vm_direct_path_gen_2_unsupported_reason",
        "vm_direct_path_gen_2_unsupported_reason_extended",
        "vmfs_datastore_mount_capable",
        "vmotion_across_network_supported",
        "vmotion_supported",
        "vmotion_with_storage_vmotion_supported",
        "vr_nfc_nic_selection_supported",
        "vsan_supported",
    ]


def test_esxi_host_capability_params(service_instance, integration_test_config):
    """
    Test we are returning the same values from get_capabilities
    as our connected vcenter instance.
    """
    capabilities = esxi.get_capabilities(service_instance=service_instance)
    for host_id in capabilities:
        for arg_name in HOST_CAPABILITIES:
            assert capabilities[host_id][arg_name] == integration_test_config["esxi_capabilities"][host_id][arg_name]


def test_list_pkgs(service_instance):
    """
    Test list packages on ESXi host
    """
    ret = esxi.list_pkgs(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    assert ret
    for host in ret:
        assert ret[host]
        for pkg in ret[host]:
            assert sorted(list(ret[host][pkg])) == sorted(
                [
                    "version",
                    "vendor",
                    "summary",
                    "description",
                    "acceptance_level",
                    "maintenance_mode_required",
                    "creation_date",
                ]
            )

    host = MagicMock()
    host.configManager.imageConfigManager.FetchSoftwarePackages.side_effect = (
        salt.exceptions.VMwareApiError
    )
    setattr(saltext.vmware.utils.esxi, "get_hosts", MagicMock(return_value=[host]))
    with pytest.raises(salt.exceptions.SaltException) as exc:
        ret = esxi.list_pkgs(
            service_instance=service_instance,
            datacenter_name="Datacenter",
            cluster_name="Cluster",
        )


def test_manage_service(service_instance):
    """
    Test manage services on esxi host
    """
    SSH_SERVICE = "TSM-SSH"
    ret = esxi.manage_service(
        service_name=SSH_SERVICE,
        service_instance=service_instance,
        state="start",
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    assert ret

    ret = esxi.list_services(
        service_name=SSH_SERVICE,
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    for host in ret:
        assert ret[host][SSH_SERVICE]["state"] == "running"

    ret = esxi.manage_service(
        service_name=SSH_SERVICE,
        service_instance=service_instance,
        state="stop",
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    assert ret

    ret = esxi.list_services(
        service_name=SSH_SERVICE,
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    for host in ret:
        assert ret[host][SSH_SERVICE]["state"] == "stopped"

    ret = esxi.manage_service(
        service_name=SSH_SERVICE,
        service_instance=service_instance,
        state="restart",
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    assert ret
    ret = esxi.list_services(
        service_name=SSH_SERVICE,
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    for host in ret:
        assert ret[host][SSH_SERVICE]["state"] == "running"

    for policy in ["on", "off", "automatic"]:
        ret = esxi.manage_service(
            service_name=SSH_SERVICE,
            service_instance=service_instance,
            startup_policy=policy,
            datacenter_name="Datacenter",
            cluster_name="Cluster",
        )
        assert ret
        ret = esxi.list_services(
            service_name=SSH_SERVICE,
            service_instance=service_instance,
            datacenter_name="Datacenter",
            cluster_name="Cluster",
        )
        for host in ret:
            assert ret[host][SSH_SERVICE]["startup_policy"] == policy


def test_acceptance_level(service_instance):
    """
    Test acceptance level on esxi host
    """
    ret = esxi.set_acceptance_level(
        acceptance_level="community",
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    for h in ret:
        assert ret[h] == "community"

    ret = esxi.get_acceptance_level(
        acceptance_level="community",
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    assert set(ret.values()) == {"community"}


def test_advanced_config(service_instance):
    """
    Test advanced config on esxi host
    """
    ret = esxi.set_advanced_config(
        config_name="Annotations.WelcomeMessage",
        config_value="testing",
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    for h in ret:
        assert ret[h]["Annotations.WelcomeMessage"] == "testing"

    ret = esxi.get_advanced_config(
        config_name="Annotations.WelcomeMessage",
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    for h in ret:
        assert ret[h]["Annotations.WelcomeMessage"] == "testing"

    ret = esxi.set_advanced_configs(
        config_dict={"Annotations.WelcomeMessage": "test1", "BufferCache.FlushInterval": 3000},
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    for h in ret:
        assert ret[h]["Annotations.WelcomeMessage"] == "test1"
        assert ret[h]["BufferCache.FlushInterval"] == 3000

    ret = esxi.get_advanced_config(
        config_name="BufferCache.FlushInterval",
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    for h in ret:
        assert ret[h]["BufferCache.FlushInterval"] == 3000


def test_get_dns_config(service_instance):
    """
    Test get dns configuration on ESXi host
    """
    ret = esxi.get_dns_config(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    assert ret
    for host in ret:
        assert ret[host]["ip"]
        assert ret[host]["host_name"]
        assert ret[host]["domain_name"]

    ret = esxi.get_dns_config(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
        host_name="no_host",
    )
    assert not ret


def test_add(integration_test_config, service_instance):
    """
    Test esxi add
    """
    if integration_test_config["esxi_manage_test_instance"]:
        ret = esxi.add(
            integration_test_config["esxi_manage_test_instance"]["name"],
            integration_test_config["esxi_manage_test_instance"]["user"],
            integration_test_config["esxi_manage_test_instance"]["password"],
            integration_test_config["esxi_manage_test_instance"]["cluster"],
            integration_test_config["esxi_manage_test_instance"]["datacenter"],
            verify_host_cert=False,
            service_instance=service_instance,
        )
        assert ret["state"] == "connected"
    else:
        pytest.skip("test requires esxi manage test instance credentials")


def test_manage_disconnect(integration_test_config, service_instance):
    """
    Test esxi manage disconnect task
    """
    if integration_test_config["esxi_manage_test_instance"]:
        ret = esxi.disconnect(
            integration_test_config["esxi_manage_test_instance"]["name"],
            service_instance=service_instance,
        )
        assert ret["state"] == "disconnected"
    else:
        pytest.skip("test requires esxi manage test instance credentials")


def test_move(integration_test_config, service_instance):
    """
    Test esxi move
    """
    if integration_test_config["esxi_manage_test_instance"]:
        ret = esxi.move(
            integration_test_config["esxi_manage_test_instance"]["name"],
            integration_test_config["esxi_manage_test_instance"]["move"],
            service_instance=service_instance,
        )
        assert (
            ret["state"]
            == f"moved {integration_test_config['esxi_manage_test_instance']['name']} from {integration_test_config['esxi_manage_test_instance']['cluster']} to {integration_test_config['esxi_manage_test_instance']['move']}"
        )
    else:
        pytest.skip("test requires esxi manage test instance credentials")


def test_manage_connect(integration_test_config, service_instance):
    """
    Test esxi manage connect task
    """
    if integration_test_config["esxi_manage_test_instance"]:
        ret = esxi.connect(
            integration_test_config["esxi_manage_test_instance"]["name"],
            service_instance=service_instance,
        )
        assert ret["state"] == "connected"
    else:
        pytest.skip("test requires esxi manage test instance credentials")


def test_manage_remove(integration_test_config, service_instance):
    """
    Test esxi manage remove task
    """
    if integration_test_config["esxi_manage_test_instance"]:
        esxi.disconnect(
            integration_test_config["esxi_manage_test_instance"]["name"],
            service_instance=service_instance,
        )
        ret = esxi.remove(
            integration_test_config["esxi_manage_test_instance"]["name"],
            service_instance=service_instance,
        )
        assert (
            ret["state"]
            == f"removed host {integration_test_config['esxi_manage_test_instance']['name']}"
        )
    else:
        pytest.skip("test requires esxi manage test instance credentials")


def test_esxi_get(service_instance):
    """
    Test get configuration on ESXi host
    """
    ret = esxi.get(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    assert ret
    for host in ret:
        assert ret[host]["cpu_model"]
        assert ret[host]["capabilities"]
        assert ret[host]["nics"]
        assert ret[host]["num_cpu_cores"]

    ret = esxi.get(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
        include_host_capabilities=False,
    )
    assert ret
    for host in ret:
        assert ret[host]["cpu_model"]
        assert "capabilities" not in ret[host]
        assert ret[host]["nics"]
        assert ret[host]["num_cpu_cores"]

    ret = esxi.get(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
        host_name="no_host",
    )
    assert not ret
