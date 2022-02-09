# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import uuid
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import salt.exceptions
import saltext.vmware.modules.esxi as esxi
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.esxi


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


@pytest.fixture
def esxi_manage_test_instance(integration_test_config):
    instance = integration_test_config.get("esxi_manage_test_instance")
    if instance is None:
        pytest.skip("test requires esxi manage test instance credentials")
    else:
        return instance


def test_esxi_get_lun_ids_should_return_lun_NAA_ids(service_instance, integration_test_config):
    expected_lun_ids = integration_test_config["esxi_datastore_disk_names"]
    actual_ids = esxi.get_lun_ids(service_instance=service_instance)
    assert actual_ids == expected_lun_ids


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

    # TODO: This should be a unit test, not an integration test -W. Werner, 2022-02-09
    host = MagicMock()
    host.configManager.imageConfigManager.FetchSoftwarePackages.side_effect = (
        salt.exceptions.VMwareApiError
    )
    with patch("saltext.vmware.utils.esxi.get_hosts", autospec=True, return_value=[host]):
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


def test_get_firewall_config(service_instance):
    """
    Test get firewall configuration on ESXi host
    """
    ret = esxi.get_firewall_config(
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

    ret = esxi.get_dns_config(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
        host_name="no_host",
    )
    assert not ret


def test_add(esxi_manage_test_instance, service_instance):
    """
    Test esxi add
    """
    ret = esxi.add(
        esxi_manage_test_instance["name"],
        esxi_manage_test_instance["user"],
        esxi_manage_test_instance["password"],
        esxi_manage_test_instance["cluster"],
        esxi_manage_test_instance["datacenter"],
        verify_host_cert=False,
        service_instance=service_instance,
    )
    assert ret["state"] == "connected"


def test_manage_disconnect(esxi_manage_test_instance, service_instance):
    """
    Test esxi manage disconnect task
    """
    ret = esxi.disconnect(
        esxi_manage_test_instance["name"],
        service_instance=service_instance,
    )
    assert ret["state"] == "disconnected"


def test_move(esxi_manage_test_instance, service_instance):
    """
    Test esxi move
    """
    ret = esxi.move(
        esxi_manage_test_instance["name"],
        esxi_manage_test_instance["move"],
        service_instance=service_instance,
    )
    assert (
        ret["state"]
        == f"moved {esxi_manage_test_instance['name']} from {esxi_manage_test_instance['cluster']} to {esxi_manage_test_instance['move']}"
    )


def test_manage_connect(esxi_manage_test_instance, service_instance):
    """
    Test esxi manage connect task
    """
    ret = esxi.connect(
        esxi_manage_test_instance["name"],
        service_instance=service_instance,
    )
    assert ret["state"] == "connected"


def test_manage_remove(esxi_manage_test_instance, service_instance):
    """
    Test esxi manage remove task
    """
    esxi.disconnect(
        esxi_manage_test_instance["name"],
        service_instance=service_instance,
    )
    ret = esxi.remove(
        esxi_manage_test_instance["name"],
        service_instance=service_instance,
    )
    assert ret["state"] == f"removed host {esxi_manage_test_instance['name']}"


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


def test_get_ntp_config(service_instance):
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

    ret = esxi.get_ntp_config(
        service_instance=service_instance,
        datacenter_name="Datacenter",
        cluster_name="Cluster",
        host_name="no_host",
    )
    assert not ret


def test_add_update_remove_user(service_instance):
    """
    Test add/update/remove a local ESXi user
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
