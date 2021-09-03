# Copyright 2021 VMware, Inc.
# SPDX-License: Apache-2.0
import logging

import salt.exceptions
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.esxi as utils_esxi
from saltext.vmware.utils.connect import get_service_instance

log = logging.getLogger(__name__)

try:
    from pyVmomi import vmodl, vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_esxi"


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


# @connect.get_si
def get_lun_ids(*, service_instance):
    """
    Return a list of LUN (Logical Unit Number) NAA (Network Addressing Authority) IDs.
    """

    # TODO: Might be better to use that other recursive view thing? Not sure
    hosts = service_instance.content.rootFolder.childEntity[0].hostFolder.childEntity[0].host
    ids = []
    for host in hosts:
        for datastore in host.datastore:
            for extent in datastore.info.vmfs.extent:
                ids.append(extent.diskName)
    return ids


# @connect.get_si
def get_capabilities(*, service_instance=None):
    """
    Return ESXi host's capability information.
    """
    if service_instance is None:
        ...
    hosts = service_instance.content.rootFolder.childEntity[0].hostFolder.childEntity[0].host
    capabilities = {}
    for host in hosts:
        capability = host.capability
        capabilities[host.name] = {
            "accel3dSupported": capability.accel3dSupported,
            "backgroundSnapshotsSupported": capability.backgroundSnapshotsSupported,
            "checkpointFtCompatibilityIssues": list(capability.smpFtCompatibilityIssues),
            "checkpointFtSupported": capability.smpFtSupported,
            "cloneFromSnapshotSupported": capability.cloneFromSnapshotSupported,
            "cpuHwMmuSupported": capability.cpuHwMmuSupported,
            "cpuMemoryResourceConfigurationSupported": capability.cpuMemoryResourceConfigurationSupported,
            "cryptoSupported": capability.cryptoSupported,
            "datastorePrincipalSupported": capability.datastorePrincipalSupported,
            "deltaDiskBackingsSupported": capability.deltaDiskBackingsSupported,
            "eightPlusHostVmfsSharedAccessSupported": capability.eightPlusHostVmfsSharedAccessSupported,
            "encryptedVMotionSupported": capability.encryptedVMotionSupported,
            "encryptionCBRCSupported": capability.encryptionCBRCSupported,
            "encryptionChangeOnAddRemoveSupported": capability.encryptionChangeOnAddRemoveSupported,
            "encryptionFaultToleranceSupported": capability.encryptionFaultToleranceSupported,
            "encryptionHBRSupported": capability.encryptionHBRSupported,
            "encryptionHotOperationSupported": capability.encryptionHotOperationSupported,
            "encryptionMemorySaveSupported": capability.encryptionMemorySaveSupported,
            "encryptionRDMSupported": capability.encryptionRDMSupported,
            "encryptionVFlashSupported": capability.encryptionVFlashSupported,
            "encryptionWithSnapshotsSupported": capability.encryptionWithSnapshotsSupported,
            "featureCapabilitiesSupported": capability.featureCapabilitiesSupported,
            "firewallIpRulesSupported": capability.firewallIpRulesSupported,
            "ftCompatibilityIssues": list(capability.ftCompatibilityIssues),
            "ftSupported": capability.ftSupported,
            "gatewayOnNicSupported": capability.gatewayOnNicSupported,
            "hbrNicSelectionSupported": capability.hbrNicSelectionSupported,
            "highGuestMemSupported": capability.highGuestMemSupported,
            "hostAccessManagerSupported": capability.hostAccessManagerSupported,
            "interVMCommunicationThroughVMCISupported": capability.interVMCommunicationThroughVMCISupported,
            "ipmiSupported": capability.ipmiSupported,
            "iscsiSupported": capability.iscsiSupported,
            "latencySensitivitySupported": capability.latencySensitivitySupported,
            "localSwapDatastoreSupported": capability.localSwapDatastoreSupported,
            "loginBySSLThumbprintSupported": capability.loginBySSLThumbprintSupported,
            "maintenanceModeSupported": capability.maintenanceModeSupported,
            "markAsLocalSupported": capability.markAsLocalSupported,
            "markAsSsdSupported": capability.markAsSsdSupported,
            "maxHostRunningVms": capability.maxHostRunningVms,
            "maxHostSupportedVcpus": capability.maxHostSupportedVcpus,
            "maxNumDisksSVMotion": capability.maxNumDisksSVMotion,
            "maxRegisteredVMs": capability.maxRegisteredVMs,
            "maxRunningVMs": capability.maxRunningVMs,
            "maxSupportedVMs": capability.maxSupportedVMs,
            "maxSupportedVcpus": capability.maxSupportedVcpus,
            "maxVcpusPerFtVm": capability.maxVcpusPerFtVm,
            "messageBusProxySupported": capability.messageBusProxySupported,
            "multipleNetworkStackInstanceSupported": capability.multipleNetworkStackInstanceSupported,
            "nestedHVSupported": capability.nestedHVSupported,
            "nfs41Krb5iSupported": capability.nfs41Krb5iSupported,
            "nfs41Supported": capability.nfs41Supported,
            "nfsSupported": capability.nfsSupported,
            "nicTeamingSupported": capability.nicTeamingSupported,
            "oneKVolumeAPIsSupported": capability.oneKVolumeAPIsSupported,
            "perVMNetworkTrafficShapingSupported": capability.perVMNetworkTrafficShapingSupported,
            "perVmSwapFiles": capability.perVmSwapFiles,
            "preAssignedPCIUnitNumbersSupported": capability.preAssignedPCIUnitNumbersSupported,
            "provisioningNicSelectionSupported": capability.provisioningNicSelectionSupported,
            "rebootSupported": capability.rebootSupported,
            "recordReplaySupported": capability.recordReplaySupported,
            "recursiveResourcePoolsSupported": capability.recursiveResourcePoolsSupported,
            "reliableMemoryAware": capability.reliableMemoryAware,
            "replayCompatibilityIssues": list(capability.replayCompatibilityIssues),
            "replayUnsupportedReason": capability.replayUnsupportedReason,
            "restrictedSnapshotRelocateSupported": capability.restrictedSnapshotRelocateSupported,
            "sanSupported": capability.sanSupported,
            "scaledScreenshotSupported": capability.scaledScreenshotSupported,
            "scheduledHardwareUpgradeSupported": capability.scheduledHardwareUpgradeSupported,
            "screenshotSupported": capability.screenshotSupported,
            "servicePackageInfoSupported": capability.servicePackageInfoSupported,
            "shutdownSupported": capability.shutdownSupported,
            "smartCardAuthenticationSupported": capability.smartCardAuthenticationSupported,
            "smpFtCompatibilityIssues": list(capability.smpFtCompatibilityIssues),
            "smpFtSupported": capability.smpFtSupported,
            "snapshotRelayoutSupported": capability.snapshotRelayoutSupported,
            "standbySupported": capability.standbySupported,
            "storageIORMSupported": capability.storageIORMSupported,
            "storagePolicySupported": capability.storagePolicySupported,
            "storageVMotionSupported": capability.storageVMotionSupported,
            "supportedVmfsMajorVersion": list(capability.supportedVmfsMajorVersion),
            "suspendedRelocateSupported": capability.suspendedRelocateSupported,
            "tpmSupported": capability.tpmSupported,
            "turnDiskLocatorLedSupported": capability.turnDiskLocatorLedSupported,
            "unsharedSwapVMotionSupported": capability.unsharedSwapVMotionSupported,
            "upitSupported": capability.upitSupported,
            "vFlashSupported": capability.vFlashSupported,
            "vPMCSupported": capability.vPMCSupported,
            "vStorageCapable": capability.vStorageCapable,
            "virtualExecUsageSupported": capability.virtualExecUsageSupported,
            "virtualVolumeDatastoreSupported": capability.virtualVolumeDatastoreSupported,
            "vlanTaggingSupported": capability.vlanTaggingSupported,
            "vmDirectPathGen2Supported": capability.vmDirectPathGen2Supported,
            "vmDirectPathGen2UnsupportedReason": list(capability.vmDirectPathGen2UnsupportedReason),
            "vmDirectPathGen2UnsupportedReasonExtended": capability.vmDirectPathGen2UnsupportedReasonExtended,
            "vmfsDatastoreMountCapable": capability.vmfsDatastoreMountCapable,
            "vmotionAcrossNetworkSupported": capability.vmotionAcrossNetworkSupported,
            "vmotionSupported": capability.vmotionSupported,
            "vmotionWithStorageVMotionSupported": capability.vmotionWithStorageVMotionSupported,
            "vrNfcNicSelectionSupported": capability.vrNfcNicSelectionSupported,
            "vsanSupported": capability.vsanSupported,
        }

    return capabilities


def power_state(
    datacenter_name=None, cluster_name=None, host_name=None, state=None, timeout=600, force=True
):
    """
    Manage the power state of the ESXI host.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXI hostname whose power state needs to be managed (Optional)

    state
        Sets the ESXI host to this power state. Valid values: "reboot", "standby", "poweron", "shutdown".

    timeout
        Timeout when transitioning power state to standby / poweron. Default: 600 seconds

    force
        Force power state transition. Default: True


    .. code-block:: bash

        salt '*' vmware_esxi.power_state datacenter_name=dc1 cluster_name=cl1 host_name=host1 state=shutdown
    """
    ret = None
    task = None
    service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=True if not host_name else False,
    )

    try:
        for h in hosts:
            if state == "reboot":
                task = h.RebootHost_Task(force)
            elif state == "standby":
                task = h.PowerDownHostToStandBy_Task(timeout, force)
            elif state == "poweron":
                task = h.PowerUpHostFromStandBy_Task(timeout)
            elif state == "shutdown":
                task = h.ShutdownHost_Task(force)
            if task:
                utils_common.wait_for_task(task, h.name, "PowerStateTask")
            ret = True
    except vmodl.fault.NotSupported as exc:
        ret = exc.msg
    except salt.exceptions.VMwareApiError as api_err:
        ret = str(api_err)
    return ret


def manage_service(
    service_name,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    state=None,
    service_policy=None,
    service_instance=None,
):
    """
    Manage the state of the service running on the EXSI host.

    service_name
        Service that needs to be managed.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXI hostname whose power state needs to be managed (optional)

    state
        Sets the service running on the ESXI host to this state. Valid values: "start", "stop", "restart".

    service_policy
        Sets the service startup policy. If unspecified, no changes are made. Valid values "on", "off", "automatic".
        - on: Start and stop with host
        - off: Start and stop manually
        - automatic: Start automatically if any ports are open, and stop when all ports are closed

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (Optional)

    .. code-block:: bash

        salt '*' vmware_esxi.manage_service sshd datacenter_name=dc1 cluster_name=cl1 host_name=host1 state=restart service_policy=on
    """
    log.debug("Running vmware_esxi.manage_service")
    ret = None
    task = None
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=True if not host_name else False,
    )

    try:
        for h in hosts:
            host_service = h.configManager.serviceSystem
            if not host_service:
                continue
            if state:
                if state == "start":
                    host_service.StartService(id=service_name)
                elif state == "stop":
                    host_service.StopService(id=service_name)
                elif state == "restart":
                    host_service.RestartService(id=service_name)
                else:
                    return "Error: Unknown state - {}".format(state)
            if service_policy is not None:
                if service_policy is True:
                    service_policy = "on"
                elif service_policy is False:
                    service_policy = "off"
                host_service.UpdateServicePolicy(id=service_name, policy=service_policy)
        ret = True
    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vmodl.fault.InvalidArgument,
    ) as exc:
        ret = exc.msg
    except salt.exceptions.VMwareApiError as api_err:
        ret = str(api_err)
    return ret


def list_services(
    service_name=None,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    state=None,
    service_policy=None,
    service_instance=None,
):
    """
    Manage the state of the service running on the EXSI host.

    service_name
        Filter by this service name. (optional)

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXI hostname (optional)

    state
        Filter by this service state. Valid values: "running", "stopped"

    service_policy
        Filter by this service startup policy. Valid values "on", "off", "automatic".

    service_instance
        Use this vCenter service connection instance instead of creating a new one. Optional.

    .. code-block:: bash

        salt '*' vmware_esxi.list_services
    """
    log.debug("Running vmware_esxi.list_services")
    ret = {}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=True if not host_name else False,
    )

    try:
        for h in hosts:
            host_service = h.configManager.serviceSystem
            ret[h.name] = {}
            if not host_service:
                continue
            if service_policy is not None:
                # salt converts command line input "on" and "off" to True and False. Handle explicitly.
                if service_policy is True:
                    service_policy = "on"
                elif service_policy is False:
                    service_policy = "off"
            services = host_service.serviceInfo.service
            for service in services or []:
                if service_name and service.key != service_name:
                    continue
                if service_policy and service.policy != service_policy:
                    continue
                if state and state == "running" and not service.running:
                    continue
                if state and state == "stopped" and service.running:
                    continue
                ret[h.name][service.key] = {
                    "state": "running" if service.running else "stopped",
                    "service_policy": service.policy,
                }
    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vmodl.fault.InvalidArgument,
    ) as exc:
        ret = exc.msg
    except salt.exceptions.VMwareApiError as api_err:
        ret = str(api_err)
    return ret
