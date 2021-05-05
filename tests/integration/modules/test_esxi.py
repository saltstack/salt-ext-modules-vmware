# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import saltext.vmware.modules.esxi as esxi
import pytest


def test_esxi_get_lun_ids_should_return_lun_NAA_ids(service_instance, integration_test_config):
    expected_lun_ids = integration_test_config["esxi_datastore_disk_names"]
    actual_ids = esxi.get_lun_ids(service_instance=service_instance)
    assert actual_ids == expected_lun_ids


@pytest.mark.parametrize(
    "arg_name", [
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
        "vsanSupported"
    ]
)
def test_esxi_host_capability_params(service_instance, integration_test_config, arg_name):
    """
    Test we are returning the same values from get_capabilities
    as our connected vcenter instance.
    """
    capabilities = esxi.get_capabilities(service_instance=service_instance)
    for host_id in capabilities:
        expected_value = integration_test_config['esxi_capabilities'][host_id][arg_name]
        assert capabilities[host_id][arg_name] == expected_value