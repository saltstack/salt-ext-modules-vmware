# Copyright 2021 VMware, Inc.
# SPDX-License: Apache-2.0
import saltext.vmware.utils.connect as connect


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


# # TODO: remove/rehash code below here -W. Werner, 2021-04-28


"""
Glues the VMware vSphere Execution Module to the VMware ESXi Proxy Minions to the
:mod:`esxi proxymodule <salt.proxy.esxi>`.

.. versionadded:: 2015.8.4

Depends: :mod:`vSphere Remote Execution Module (salt.modules.vsphere)
<salt.modules.vsphere>`

For documentation on commands that you can direct to an ESXi host via proxy,
look in the documentation for :mod:`salt.modules.vsphere <salt.modules.vsphere>`.

This execution module calls through to a function in the ESXi proxy module
called ``ch_config``, which looks up the function passed in the ``command``
parameter in :mod:`salt.modules.vsphere <salt.modules.vsphere>` and calls it.

To execute commands with an ESXi Proxy Minion using the vSphere Execution Module,
use the ``esxi.cmd <vsphere-function-name>`` syntax. Both args and kwargs needed
for various vsphere execution module functions must be passed through in a kwarg-
type manor.

.. code-block:: bash

    salt 'esxi-proxy' esxi.cmd system_info
    salt 'exsi-proxy' esxi.cmd get_service_policy service_name='ssh'

"""

import logging
import sys

import salt.utils.platform

log = logging.getLogger(__name__)

__proxyenabled__ = ["esxi"]
__virtualname__ = "esxi"


def __virtual__():
    return __virtualname__


def cmd(command, *args, **kwargs):
    proxy_prefix = __opts__["proxy"]["proxytype"]
    proxy_cmd = proxy_prefix + ".ch_config"

    return __proxy__[proxy_cmd](command, *args, **kwargs)


def get_details():
    return __proxy__["esxi.get_details"]()


def upload_ssh_key(
    host,
    username,
    password,
    ssh_key=None,
    ssh_key_file=None,
    protocol=None,
    port=None,
    certificate_verify=None,
):
    """
    Upload an ssh key for root to an ESXi host via http PUT.
    This function only works for ESXi, not vCenter.
    Only one ssh key can be uploaded for root.  Uploading a second key will
    replace any existing key.

    :param host: The location of the ESXi Host
    :param username: Username to connect as
    :param password: Password for the ESXi web endpoint
    :param ssh_key: Public SSH key, will be added to authorized_keys on ESXi
    :param ssh_key_file: File containing the SSH key.  Use 'ssh_key' or
                         ssh_key_file, but not both.
    :param protocol: defaults to https, can be http if ssl is disabled on ESXi
    :param port: defaults to 443 for https
    :param certificate_verify: If true require that the SSL connection present
                               a valid certificate. Default: True
    :return: Dictionary with a 'status' key, True if upload is successful.
             If upload is unsuccessful, 'status' key will be False and
             an 'Error' key will have an informative message.

    CLI Example:

    .. code-block:: bash

        salt '*' vsphere.upload_ssh_key my.esxi.host root bad-password ssh_key_file='/etc/salt/my_keys/my_key.pub'

    """
    if protocol is None:
        protocol = "https"
    if port is None:
        port = 443
    if certificate_verify is None:
        certificate_verify = True

    url = "{}://{}:{}/host/ssh_root_authorized_keys".format(protocol, host, port)
    ret = {}
    result = None
    try:
        if ssh_key:
            result = salt.utils.http.query(
                url,
                status=True,
                text=True,
                method="PUT",
                username=username,
                password=password,
                data=ssh_key,
                verify_ssl=certificate_verify,
            )
        elif ssh_key_file:
            result = salt.utils.http.query(
                url,
                status=True,
                text=True,
                method="PUT",
                username=username,
                password=password,
                data_file=ssh_key_file,
                data_render=False,
                verify_ssl=certificate_verify,
            )
        if result.get("status") == 200:
            ret["status"] = True
        else:
            ret["status"] = False
            ret["Error"] = result["error"]
    except Exception as msg:  # pylint: disable=broad-except
        ret["status"] = False
        ret["Error"] = msg

    return ret


def get_ssh_key(host, username, password, protocol=None, port=None, certificate_verify=None):
    """
    Retrieve the authorized_keys entry for root.
    This function only works for ESXi, not vCenter.

    :param host: The location of the ESXi Host
    :param username: Username to connect as
    :param password: Password for the ESXi web endpoint
    :param protocol: defaults to https, can be http if ssl is disabled on ESXi
    :param port: defaults to 443 for https
    :param certificate_verify: If true require that the SSL connection present
                               a valid certificate. Default: True
    :return: True if upload is successful

    CLI Example:

    .. code-block:: bash

        salt '*' vsphere.get_ssh_key my.esxi.host root bad-password certificate_verify=True

    """
    if protocol is None:
        protocol = "https"
    if port is None:
        port = 443
    if certificate_verify is None:
        certificate_verify = True

    url = "{}://{}:{}/host/ssh_root_authorized_keys".format(protocol, host, port)
    ret = {}
    try:
        result = salt.utils.http.query(
            url,
            status=True,
            text=True,
            method="GET",
            username=username,
            password=password,
            verify_ssl=certificate_verify,
        )
        if result.get("status") == 200:
            ret["status"] = True
            ret["key"] = result["text"]
        else:
            ret["status"] = False
            ret["Error"] = result["error"]
    except Exception as msg:  # pylint: disable=broad-except
        ret["status"] = False
        ret["Error"] = msg

    return ret


def update_host_password(
    host, username, password, new_password, protocol=None, port=None, verify_ssl=True
):
    """
    Update the password for a given host.

    .. note:: Currently only works with connections to ESXi hosts. Does not work with vCenter servers.

    host
        The location of the ESXi host.

    username
        The username used to login to the ESXi host, such as ``root``.

    password
        The password used to login to the ESXi host.

    new_password
        The new password that will be updated for the provided username on the ESXi host.

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        salt '*' vsphere.update_host_password my.esxi.host root original-bad-password new-bad-password

    """
    service_instance = salt.utils.vmware.get_service_instance(
        host=host,
        username=username,
        password=password,
        protocol=protocol,
        port=port,
        verify_ssl=verify_ssl,
    )
    # Get LocalAccountManager object
    account_manager = salt.utils.vmware.get_inventory(service_instance).accountManager

    # Create user account specification object and assign id and password attributes
    user_account = vim.host.LocalAccountManager.AccountSpecification()
    user_account.id = username
    user_account.password = new_password

    # Update the password
    try:
        account_manager.UpdateUser(user_account)
    except vmodl.fault.SystemError as err:
        raise CommandExecutionError(err.msg)
    except vim.fault.UserNotFound:
        raise CommandExecutionError(
            "'vsphere.update_host_password' failed for host {}: " "User was not found.".format(host)
        )
    # If the username and password already exist, we don't need to do anything.
    except vim.fault.AlreadyExists:
        pass

    return True


def configure_host_cache(enabled, datastore=None, swap_size_MiB=None, service_instance=None):
    """
    Configures the host cache on the selected host.

    enabled
        Boolean flag specifying whether the host cache is enabled.

    datastore
        Name of the datastore that contains the host cache. Must be set if
        enabled is ``true``.

    swap_size_MiB
        Swap size in Mibibytes. Needs to be set if enabled is ``true``. Must be
        smaller than the datastore size.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.configure_host_cache enabled=False

        salt '*' vsphere.configure_host_cache enabled=True datastore=ds1
            swap_size_MiB=1024
    """
    log.debug("Validating host cache input")
    schema = SimpleHostCacheSchema.serialize()
    try:
        jsonschema.validate(
            {
                "enabled": enabled,
                "datastore_name": datastore,
                "swap_size_MiB": swap_size_MiB,
            },
            schema,
        )
    except jsonschema.exceptions.ValidationError as exc:
        raise ArgumentValueError(exc)
    if not enabled:
        raise ArgumentValueError("Disabling the host cache is not supported")
    ret_dict = {"enabled": False}

    host_ref = _get_proxy_target(service_instance)
    hostname = __proxy__["esxi.get_details"]()["esxi_host"]
    if datastore:
        ds_refs = salt.utils.vmware.get_datastores(
            service_instance, host_ref, datastore_names=[datastore]
        )
        if not ds_refs:
            raise VMwareObjectRetrievalError(
                "Datastore '{}' was not found on host " "'{}'".format(datastore, hostname)
            )
        ds_ref = ds_refs[0]
    salt.utils.vmware.configure_host_cache(host_ref, ds_ref, swap_size_MiB)
    return True


def get_host_cache(service_instance=None):
    """
    Returns the host cache configuration on the proxy host.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.get_host_cache
    """
    # Default to getting all disks if no filtering is done
    ret_dict = {}
    host_ref = _get_proxy_target(service_instance)
    hostname = __proxy__["esxi.get_details"]()["esxi_host"]
    hci = saltext.vmware.utils.vmware.get_host_cache(host_ref)
    if not hci:
        log.debug("Host cache not configured on host '{}'".format(hostname))
        ret_dict["enabled"] = False
        return ret_dict

    # TODO Support multiple host cache info objects (on multiple datastores)
    return {
        "enabled": True,
        "datastore": {"name": hci.key.name},
        "swap_size": "{}MiB".format(hci.swapSize),
    }
