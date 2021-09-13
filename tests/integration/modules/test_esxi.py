# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pytest
import saltext.vmware.modules.esxi as esxi


def test_esxi_get_lun_ids_should_return_lun_NAA_ids(service_instance, integration_test_config):
    expected_lun_ids = integration_test_config["esxi_datastore_disk_names"]
    actual_ids = esxi.get_lun_ids(service_instance=service_instance)
    assert actual_ids == expected_lun_ids


@pytest.mark.parametrize(
    "arg_name",
    [
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
    ],
)
def test_esxi_host_capability_params(service_instance, integration_test_config, arg_name):
    """
    Test we are returning the same values from get_capabilities
    as our connected vcenter instance.
    """
    capabilities = esxi.get_capabilities(service_instance=service_instance)
    for host_id in capabilities:
        expected_value = integration_test_config["esxi_capabilities"][host_id][arg_name]
        assert capabilities[host_id][arg_name] == expected_value


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
