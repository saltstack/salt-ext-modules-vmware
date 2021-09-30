# Copyright 2021 VMware, Inc.
# SPDX-License: Apache-2.0
import logging

import salt.exceptions
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.esxi as utils_esxi
from saltext.vmware.utils.connect import get_service_instance

log = logging.getLogger(__name__)

try:
    from pyVmomi import vmodl, vim, VmomiSupport

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_esxi"


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def get_lun_ids(service_instance=None):
    """
    Return a list of LUN (Logical Unit Number) NAA (Network Addressing Authority) IDs.
    """

    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)

    hosts = utils_esxi.get_hosts(service_instance=service_instance, get_all_hosts=True)
    ids = []
    for host in hosts:
        for datastore in host.datastore:
            for extent in datastore.info.vmfs.extent:
                ids.append(extent.diskName)
    return ids


def get_capabilities(service_instance=None):
    """
    Return ESXi host's capability information.
    """
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    hosts = utils_esxi.get_hosts(service_instance=service_instance, get_all_hosts=True)
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
    Manage the power state of the ESXi host.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname whose power state needs to be managed (optional).

    state
        Sets the ESXi host to this power state. Valid values: "reboot", "standby", "poweron", "shutdown".

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
    except (vmodl.fault.NotSupported, salt.exceptions.VMwareApiError) as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def manage_service(
    service_name,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    state=None,
    startup_policy=None,
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
        Filter by this ESXi hostname whose power state needs to be managed (optional)

    state
        Sets the service running on the ESXi host to this state. Valid values: "start", "stop", "restart".

    startup_policy
        Sets the service startup policy. If unspecified, no changes are made. Valid values "on", "off", "automatic".
        - on: Start and stop with host
        - off: Start and stop manually
        - automatic: Start automatically if any ports are open, and stop when all ports are closed

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.manage_service sshd datacenter_name=dc1 cluster_name=cl1 host_name=host1 state=restart startup_policy=on
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
                    raise salt.exceptions.SaltException("Unknown state - {}".format(state))
            if startup_policy is not None:
                if startup_policy is True:
                    startup_policy = "on"
                elif startup_policy is False:
                    startup_policy = "off"
                host_service.UpdateServicePolicy(id=service_name, policy=startup_policy)
        ret = True
    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vmodl.fault.InvalidArgument,
        salt.exceptions.VMwareApiError,
    ) as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def list_services(
    service_name=None,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    state=None,
    startup_policy=None,
    service_instance=None,
):
    """
    List the state of services running on matching EXSI hosts.

    service_name
        Filter by this service name. (optional)

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    state
        Filter by this service state. Valid values: "running", "stopped"

    startup_policy
        Filter by this service startup policy. Valid values "on", "off", "automatic".

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

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
            if startup_policy is not None:
                # salt converts command line input "on" and "off" to True and False. Handle explicitly.
                if startup_policy is True:
                    startup_policy = "on"
                elif startup_policy is False:
                    startup_policy = "off"
            services = host_service.serviceInfo.service
            for service in services or []:
                if service_name and service.key != service_name:
                    continue
                if startup_policy and service.policy != startup_policy:
                    continue
                if state and state == "running" and not service.running:
                    continue
                if state and state == "stopped" and service.running:
                    continue
                ret[h.name][service.key] = {
                    "state": "running" if service.running else "stopped",
                    "startup_policy": service.policy,
                }
    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vmodl.fault.InvalidArgument,
        salt.exceptions.VMwareApiError,
    ) as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def get_acceptance_level(
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    acceptance_level=None,
    service_instance=None,
):
    """
    Get acceptance level on matching EXSI hosts.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    acceptance_level
        Filter by this acceptance level. Valid values: "community", "partner", "vmware_accepted", "vmware_certified". (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.get_acceptance_level

    Returns:

    .. code-block:: json

        {
            "host1": "partner",
            "host2": "partner"
        }

    """

    log.debug("Running vmware_esxi.get_acceptance_level")
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
            host_config_manager = h.configManager.imageConfigManager
            if not host_config_manager:
                continue
            host_acceptance_level = host_config_manager.HostImageConfigGetAcceptance()
            if acceptance_level and host_acceptance_level != acceptance_level:
                continue
            ret[h.name] = host_acceptance_level
    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vmodl.fault.InvalidArgument,
        salt.exceptions.VMwareApiError,
    ) as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def set_acceptance_level(
    acceptance_level,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
):
    """
    Set acceptance level on matching EXSI hosts.

    acceptance_level
        Set to this acceptance level. Valid values: "community", "partner", "vmware_accepted", "vmware_certified".

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.set_acceptance_level

    Returns:

    .. code-block:: json

        {
            "host1": "partner",
            "host2": "partner"
        }

    """

    log.debug("Running vmware_esxi.set_acceptance_level")
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
            host_config_manager = h.configManager.imageConfigManager
            if not host_config_manager:
                continue
            host_config_manager.UpdateHostImageAcceptanceLevel(newAcceptanceLevel=acceptance_level)
            ret[h.name] = acceptance_level
    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vmodl.fault.InvalidArgument,
        salt.exceptions.VMwareApiError,
    ) as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def get_advanced_config(
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    config_name=None,
    service_instance=None,
):
    """
    Get advanced config on matching EXSI hosts.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    config_name
        Filter by this config_name. (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.get_advanced_config
    """
    log.debug("Running vmware_esxi.get_advanced_config")
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
            config_manager = h.configManager.advancedOption
            ret[h.name] = {}
            if not config_manager:
                continue
            for opt in config_manager.QueryOptions(config_name):
                ret[h.name][opt.key] = opt.value

    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vmodl.fault.InvalidArgument,
        salt.exceptions.VMwareApiError,
    ) as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def set_advanced_configs(
    config_dict,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
):
    """
    Set multiple advanced configurations on matching EXSI hosts.

    config_dict
        Set the configuration key to the configuration value. Eg: {"Annotations.WelcomeMessage": "Hello"}

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.set_advanced_config config_name=Annotations.WelcomeMessage config_value=Hello

    Returns:

    .. code-block:: json

        {
            "host1": {
                "Annotations.WelcomeMessage": "HelloDemo"
            },
        }

    """
    log.debug("Running vmware_esxi.set_advanced_configs")
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
            config_manager = h.configManager.advancedOption
            ret[h.name] = {}
            if not config_manager:
                continue

            supported_configs = {}
            for opt in config_manager.supportedOption:
                if opt.key not in config_dict:
                    continue
                supported_configs[opt.key] = opt.optionType

            advanced_configs = []
            for opt in config_dict:
                opt_type = supported_configs[opt]
                val = config_dict[opt]
                if isinstance(opt_type, vim.option.BoolOption) and not isinstance(val, bool):
                    val = val.lower() == "true"
                elif isinstance(opt_type, vim.option.LongOption):
                    val = VmomiSupport.vmodlTypes["long"](val)
                elif isinstance(opt_type, vim.option.IntOption):
                    val = VmomiSupport.vmodlTypes["int"](val)
                advanced_configs.append(vim.option.OptionValue(key=opt, value=val))
                ret[h.name][opt] = config_dict[opt]
            config_manager.UpdateOptions(changedValue=advanced_configs)
    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vmodl.fault.InvalidArgument,
        salt.exceptions.VMwareApiError,
    ) as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def set_advanced_config(
    config_name,
    config_value,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
):
    """
    Set a single advanced configuration on matching EXSI hosts.

    config_name
        Name of the advanced configuration to be set.

    config_value
        Set the advanced configuration to this value.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.set_advanced_config config_name=Annotations.WelcomeMessage config_value=Hello

    Returns:

    .. code-block:: json

        {
            "host1": {
                "Annotations.WelcomeMessage": "HelloDemo"
            },
        }

    """
    log.debug("Running vmware_esxi.set_advanced_config")
    return set_advanced_configs(
        config_dict={config_name: config_value},
        datacenter_name=datacenter_name,
        cluster_name=cluster_name,
        host_name=host_name,
        service_instance=service_instance,
    )
