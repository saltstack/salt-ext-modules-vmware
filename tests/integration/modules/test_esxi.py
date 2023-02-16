# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import uuid
from unittest.mock import MagicMock

import pytest
import salt.exceptions
import saltext.vmware.modules.esxi as esxi
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.esxi


def test_esxi_get_lun_ids_should_return_lun_NAA_ids(service_instance, integration_test_config):
    expected_lun_ids = integration_test_config["esxi_datastore_disk_names"]
    actual_ids = esxi.get_lun_ids(service_instance=service_instance)
    assert actual_ids == expected_lun_ids


HOST_CAPABILITIES = [
    "accel3dSupported",
    "backgroundSnapshotsSupported",
    "cloneFromSnapshotSupported",
    "cpuHwMmuSupported",
    "cpuMemoryResourceConfigurationSupported",
    "cryptoSupported",
    "datastorePrincipalSupported",
    "deltaDiskBackingsSupported",
    "eightPlusHostVmfsSharedAccessSupported",
    "encryptedVMotionSupported",
    "encryptionCBRCSupported",
    "encryptionChangeOnAddRemoveSupported",
    "encryptionFaultToleranceSupported",
    "encryptionHBRSupported",
    "encryptionHotOperationSupported",
    "encryptionMemorySaveSupported",
    "encryptionRDMSupported",
    "encryptionVFlashSupported",
    "encryptionWithSnapshotsSupported",
    "featureCapabilitiesSupported",
    "firewallIpRulesSupported",
    "ftCompatibilityIssues",
    "ftSupported",
    "gatewayOnNicSupported",
    "hbrNicSelectionSupported",
    "highGuestMemSupported",
    "hostAccessManagerSupported",
    "interVMCommunicationThroughVMCISupported",
    "ipmiSupported",
    "iscsiSupported",
    "latencySensitivitySupported",
    "localSwapDatastoreSupported",
    "loginBySSLThumbprintSupported",
    "maintenanceModeSupported",
    "markAsLocalSupported",
    "markAsSsdSupported",
    "maxHostRunningVms",
    "maxHostSupportedVcpus",
    "maxNumDisksSVMotion",
    "maxRegisteredVMs",
    "maxRunningVMs",
    "maxSupportedVMs",
    "maxSupportedVcpus",
    "maxVcpusPerFtVm",
    "messageBusProxySupported",
    "multipleNetworkStackInstanceSupported",
    "nestedHVSupported",
    "nfs41Krb5iSupported",
    "nfs41Supported",
    "nfsSupported",
    "nicTeamingSupported",
    "oneKVolumeAPIsSupported",
    "perVMNetworkTrafficShapingSupported",
    "perVmSwapFiles",
    "preAssignedPCIUnitNumbersSupported",
    "provisioningNicSelectionSupported",
    "rebootSupported",
    "recordReplaySupported",
    "recursiveResourcePoolsSupported",
    "reliableMemoryAware",
    "replayCompatibilityIssues",
    "replayUnsupportedReason",
    "restrictedSnapshotRelocateSupported",
    "sanSupported",
    "scaledScreenshotSupported",
    "scheduledHardwareUpgradeSupported",
    "screenshotSupported",
    "servicePackageInfoSupported",
    "shutdownSupported",
    "smartCardAuthenticationSupported",
    "smpFtCompatibilityIssues",
    "smpFtSupported",
    "snapshotRelayoutSupported",
    "standbySupported",
    "storageIORMSupported",
    "storagePolicySupported",
    "storageVMotionSupported",
    "supportedVmfsMajorVersion",
    "suspendedRelocateSupported",
    "tpmSupported",
    "turnDiskLocatorLedSupported",
    "unsharedSwapVMotionSupported",
    "upitSupported",
    "vFlashSupported",
    "vPMCSupported",
    "vStorageCapable",
    "virtualExecUsageSupported",
    "virtualVolumeDatastoreSupported",
    "vlanTaggingSupported",
    "vmDirectPathGen2Supported",
    "vmDirectPathGen2UnsupportedReason",
    "vmDirectPathGen2UnsupportedReasonExtended",
    "vmfsDatastoreMountCapable",
    "vmotionAcrossNetworkSupported",
    "vmotionSupported",
    "vmotionWithStorageVMotionSupported",
    "vrNfcNicSelectionSupported",
    "vsanSupported",
]


def test_esxi_host_capability_params(service_instance, integration_test_config):
    """
    Test we are returning the same values from get_capabilities
    as our connected vcenter instance.
    """
    capabilities = esxi.get_capabilities(service_instance=service_instance)
    for host_id in capabilities:
        for arg_name in HOST_CAPABILITIES:
            assert (
                capabilities[host_id][utils_common.camel_to_snake_case(arg_name)]
                == integration_test_config["esxi_capabilities"][host_id][arg_name]
            )


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


def test_manage_service(service_instance):
    """
    Test manage services on esxi host
    """
    SSH_SERVICE = "TSM-SSH"
    ret = esxi.service_start(
        service_name=SSH_SERVICE,
        service_instance=service_instance,
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

    ret = esxi.service_stop(
        service_name=SSH_SERVICE,
        service_instance=service_instance,
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

    ret = esxi.service_restart(
        service_name=SSH_SERVICE,
        service_instance=service_instance,
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
        ret = esxi.service_policy(
            service_name=SSH_SERVICE,
            startup_policy=policy,
            service_instance=service_instance,
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


def test_firewall_config(service_instance):
    """
    Test firewall configuration on ESXi host
    """
    ret = esxi.get_all_firewall_configs(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    assert ret
    for host in ret:
        assert ret[host][0]["allowed_hosts"]
        assert ret[host][0]["key"]
        assert ret[host][0]["service"]
        assert ret[host][0]["service"]
        assert ret[host][0]["rule"]

    ret = esxi.get_all_firewall_configs(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
        host_name="no_host",
    )
    assert not ret

    ret = esxi.set_firewall_config(
        firewall_config={
            "name": "esxupdate",
            "enabled": True,
            "allowed_hosts": {
                "all_ip": True,
                "ip_address": ["169.199.100.11"],
                "ip_network": ["169.199.200.0/24"],
            },
        },
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    assert ret
    for host in ret:
        for rule in host:
            assert host[rule][0]["enabled"] is True
            assert host[rule][0]["allowed_hosts"]["all_ip"] is True
            assert host[rule][0]["allowed_hosts"]["ip_address"][0] == "169.199.100.11"
            assert host[rule][0]["allowed_hosts"]["ip_network"][0] == "169.199.200.0/24"

    ret = esxi.set_all_firewall_configs(
        firewall_configs=[
            {
                "name": "esxupdate",
                "enabled": False,
                "allowed_hosts": {"all_ip": False, "ip_address": [], "ip_network": []},
            }
        ],
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    assert ret
    for host in ret[0]:
        for rule in host:
            assert host[rule][0]["allowed_hosts"]["all_ip"] is False
            assert host[rule][0]["enabled"] is False
            assert host[rule][0]["allowed_hosts"]["ip_address"] == []
            assert host[rule][0]["allowed_hosts"]["ip_network"] == []


def test_add(integration_test_config, service_instance):
    """
    Test esxi add
    """
    if "esxi_manage_test_instance" in integration_test_config:
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
    if "esxi_manage_test_instance" in integration_test_config:
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
    if "esxi_manage_test_instance" in integration_test_config:
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
    if "esxi_manage_test_instance" in integration_test_config:
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
    if "esxi_manage_test_instance" in integration_test_config:
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
        assert ret[host]["vsan"]
        assert ret[host]["datastores"]
        assert ret[host]["num_cpu_cores"]

    ret = esxi.get(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
        key="vsan:health",
    )
    assert ret
    for host in ret:
        assert ret[host] == "unknown"

    ret = esxi.get(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
        host_name="no_host",
    )
    assert not ret


def test_ntp_config(service_instance):
    """
    Test get ntp configuration on ESXi host
    """
    ret = esxi.get_ntp_config(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    assert ret
    expected = {
        "ntp_config_file",
        "time_zone",
        "time_zone_description",
        "time_zone_name",
        "ntp_servers",
        "time_zone_gmt_offset",
    }
    for host in ret:
        assert not expected - set(ret[host])

        assert ret[host]["ntp_servers"] == []

    ret = esxi.set_ntp_config(
        ntp_servers=["192.174.1.100", "192.174.1.200"],
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    for host in ret:
        assert host

    ret = esxi.get_ntp_config(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )

    for host in ret:
        assert ret[host]["ntp_servers"] == ["192.174.1.100", "192.174.1.200"]

    ret = esxi.set_ntp_config(
        ntp_servers=[],
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )
    for host in ret:
        assert host

    ret = esxi.get_ntp_config(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
    )

    for host in ret:
        assert ret[host]["ntp_servers"] == []

    ret = esxi.get_ntp_config(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
        host_name="no_host",
    )
    assert not ret


def test_add_update_remove_user(service_instance):
    """
    Test add/get/update/remove a local ESXi user
    """
    user_name = "A{}".format(uuid.uuid4())
    ret = esxi.add_user(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
        user_name=user_name,
        password="Secret@123",
    )
    assert ret
    for host in ret:
        assert ret[host]

    ret = esxi.get_user(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
        user_name=user_name,
    )
    assert ret
    for host in ret:
        assert ret[host]

    ret = esxi.update_user(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
        user_name=user_name,
        password="Secret@123",
        description="admin",
    )
    assert ret
    for host in ret:
        assert ret[host]

    with pytest.raises(salt.exceptions.SaltException) as exc:
        ret = esxi.update_user(
            service_instance=service_instance,
            datacenter_name="Datacenter",
            cluster_name="Cluster",
            user_name="nobody",
            password="Secret@123",
            description="admin",
        )

    ret = esxi.remove_user(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
        user_name=user_name,
    )
    assert ret
    for host in ret:
        assert ret[host]

    ret = esxi.add_user(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
        host_name="no_host",
        user_name=user_name,
        password="",
    )
    assert not ret


def test_add_update_remove_role(service_instance):
    """
    Test add/update/remove a local ESXi role
    """
    role_name = "A{}".format(uuid.uuid4())
    ret = esxi.add_role(
        service_instance=service_instance,
        role_name=role_name,
        privilege_ids=["Folder.Create"],
    )
    assert ret["role_id"]

    ret = esxi.update_role(
        service_instance=service_instance,
        role_name=role_name,
        privilege_ids=["Folder.Create", "Folder.Delete"],
    )
    assert ret

    with pytest.raises(salt.exceptions.SaltException) as exc:
        ret = esxi.update_role(
            service_instance=service_instance, role_name="nobody", privilege_ids=["Folder.Create"]
        )

    ret = esxi.remove_role(
        service_instance=service_instance,
        role_name=role_name,
    )
    assert ret


def test_add_update_remove_vmkernel_adapter(service_instance):
    """
    Test add/update/remove a vmkernel adapter
    """
    adapters = esxi.create_vmkernel_adapter(
        service_instance=service_instance,
        port_group_name="VMNetwork-PortGroup",
        dvswitch_name="dvSwitch",
        mtu=2000,
        enable_fault_tolerance=True,
        network_type="dhcp",
    )
    assert adapters
    for host in adapters:
        assert adapters[host]

    for host in adapters:
        ret = esxi.update_vmkernel_adapter(
            adapter_name=adapters[host],
            datacenter_name="Datacenter",
            service_instance=service_instance,
            port_group_name="VMNetwork-PortGroup",
            dvswitch_name="dvSwitch",
            mtu=2000,
            enable_fault_tolerance=True,
            network_type="dhcp",
            host_name=host,
        )
        assert ret
        for host in ret:
            assert ret[host]

        ret = esxi.delete_vmkernel_adapter(
            service_instance=service_instance, adapter_name=adapters[host], host_name=host
        )
        assert ret
        for host in ret:
            assert ret[host]

    with pytest.raises(salt.exceptions.SaltException) as exc:
        ret = esxi.update_vmkernel_adapter(
            service_instance=service_instance,
            adapter_name="nonexistent",
            port_group_name="VMNetwork-PortGroup",
        )

    ret = esxi.delete_vmkernel_adapter(
        service_instance=service_instance, adapter_name="nonexistent"
    )
    assert ret
    for host in ret:
        assert not ret[host]


def test_maintenance_mode(service_instance):
    hosts = list(esxi.get(service_instance=service_instance))
    assert hosts
    host = hosts[0]
    ret = esxi.in_maintenance_mode(host, service_instance)
    assert ret == dict(maintenanceMode="normal")

    try:
        for i in range(3):
            ret = esxi.maintenance_mode(host, 120, service_instance=service_instance)
            assert ret == dict(maintenanceMode="inMaintenance", changes=not i)
    except Exception as e:
        esxi.exit_maintenance_mode(host, 120, service_instance=service_instance)
        raise e

    ret = esxi.in_maintenance_mode(host, service_instance)
    assert ret == dict(maintenanceMode="inMaintenance")

    for i in range(3):
        ret = esxi.exit_maintenance_mode(host, 120, service_instance=service_instance)
        assert ret == dict(maintenanceMode="normal", changes=not i)

    ret = esxi.in_maintenance_mode(host, service_instance)
    assert ret == dict(maintenanceMode="normal")


def test_lockdown_mode(service_instance):
    hosts = list(esxi.get(service_instance=service_instance))
    assert hosts
    host = hosts[0]
    ret = esxi.in_lockdown_mode(host, service_instance)
    assert ret == dict(lockdownMode="normal")

    try:
        for i in range(3):
            ret = esxi.lockdown_mode(host, service_instance=service_instance)
            assert ret == dict(lockdownMode="inLockdown", changes=not i)
    except Exception as e:
        esxi.exit_lockdown_mode(host, service_instance=service_instance)
        raise e

    ret = esxi.in_lockdown_mode(host, service_instance)
    assert ret == dict(lockdownMode="inLockdown")

    for i in range(3):
        ret = esxi.exit_lockdown_mode(host, service_instance=service_instance)
        assert ret == dict(lockdownMode="normal", changes=not i)

    ret = esxi.in_lockdown_mode(host, service_instance)
    assert ret == dict(lockdownMode="normal")


def test_get_vsan_enabled(service_instance):
    ret = esxi.get_vsan_enabled(
        service_instance=service_instance,
    )
    assert ret
    for key in ret:
        assert isinstance(ret[key], bool)


def test_vsan_enabled(service_instance):
    ret = esxi.vsan_enable(
        service_instance=service_instance,
    )
    assert ret
    for key in ret:
        assert isinstance(ret[key], bool)
    ret = esxi.vsan_enable(
        enable=False,
        service_instance=service_instance,
    )
    assert ret
    for key in ret:
        assert isinstance(ret[key], bool)


def test_get_vsan_eligible_disks(service_instance):
    ret = esxi.get_vsan_eligible_disks(
        service_instance=service_instance,
    )
    assert ret
    for key in ret:
        assert ret[key].get("Eligible")


def test_vsan_add_disks(service_instance):
    ret = esxi.vsan_add_disks(
        service_instance=service_instance,
    )
    assert ret
    for key in ret:
        assert ret[key].get("Disks Added")


def test_list_disks(service_instance):
    ret = esxi.list_disks(
        service_instance=service_instance,
    )
    assert ret
    for host_name in ret:
        for disk in ret[host_name]:
            assert disk.get("id")
            assert disk.get("scsi_address")