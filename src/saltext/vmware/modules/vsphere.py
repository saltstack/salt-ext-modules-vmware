# Copyright 2021 VMware, Inc.
# SPDX-License: Apache-2.0
import logging
import os

import salt.exceptions
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.connect as utils_connect
import saltext.vmware.utils.esxi as utils_esxi
import saltext.vmware.utils.vsphere as utils_vsphere


log = logging.getLogger(__name__)

try:
    from pyVmomi import vmodl, vim, VmomiSupport

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_vsphere"

DEFAULT_EXCEPTIONS = (
    vim.fault.InvalidState,
    vim.fault.NotFound,
    vim.fault.HostConfigFault,
    vmodl.fault.InvalidArgument,
    salt.exceptions.VMwareApiError,
    vim.fault.AlreadyExists,
    vim.fault.UserNotFound,
    salt.exceptions.CommandExecutionError,
    vmodl.fault.SystemError,
    TypeError,
)


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def system_info(
    service_instance=None,
    profile=None,
):
    """
    .. versionadded:: 23.4.4.0rc1

    Return system information about a VMware environment.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_vsphere.system_info
    """
    log.debug("Running vmware_vsphere.system_info")
    ret = None
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    ret = utils_common.get_inventory(service_instance).about.__dict__
    if "apiType" in ret:
        if ret["apiType"] == "HostAgent":
            ret = dictupdate.update(ret, utils_common.get_hardware_grains(service_instance))
    return ret


def list_resourcepools(
    service_instance=None,
    profile=None,
):
    """
    .. versionadded:: 23.4.4.0rc1

    Returns a list of resource pools for the specified host.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vsphere.list_resourcepools
    """
    log.debug("Running vmware_vsphere.list_resourcepools")
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    return utils_vsphere.list_resourcepools(service_instance)


def list_networks(
    service_instance=None,
    profile=None,
):
    """
    .. versionadded:: 23.4.4.0rc1

    Returns a list of networks for the specified host.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vsphere.list_networks
    """
    log.debug("Running vmware_vsphere.list_networks")
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    return utils_vsphere.list_networks(service_instance)


def list_vapps(
    service_instance=None,
    profile=None,
):
    """
    .. versionadded:: 23.6.29.0rc1

    Returns a list of vApps for the specified host.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    CLI Example:

    .. code-block:: bash

        # List vapps from all minions
        salt '*' vmware_vsphere.list_vapps
    """
    log.debug("Running vmware_vsphere.list_vapps")
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    return utils_vsphere.list_vapps(service_instance)


def _get_host_disks(host_reference):
    """
    Helper function that returns a dictionary containing a list of SSD and Non-SSD disks.
    """
    storage_system = host_reference.configManager.storageSystem
    disks = storage_system.storageDeviceInfo.scsiLun
    ssds = []
    non_ssds = []

    for disk in disks:
        try:
            has_ssd_attr = disk.ssd
        except AttributeError:
            has_ssd_attr = False
        if has_ssd_attr:
            ssds.append(disk)
        else:
            non_ssds.append(disk)

    return {"SSDs": ssds, "Non-SSDs": non_ssds}


def list_ssds(
    host_name=None,
    datacenter_name=None,
    cluster_name=None,
    service_instance=None,
    profile=None,
):
    """
    .. versionadded:: 23.6.29.0rc1

    Returns a list of SSDs for the given host or list of host_names.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vsphere.list_ssds
    """
    log.debug("Running vmware_vsphere.list_ssds")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )
    for host in hosts:
        disks = _get_host_disks(host).get("SSDs")
        names = []
        for disk in disks:
            names.append(disk.canonicalName)
        ret.update({host.name: names})

    return ret


def list_non_ssds(
    host_name=None,
    datacenter_name=None,
    cluster_name=None,
    service_instance=None,
    profile=None,
):
    """
    .. versionadded:: 23.6.29.0rc1

    Returns a list of Non-SSD disks for the given host or list of host_names.

    .. note::

        In the pyVmomi StorageSystem, ScsiDisks may, or may not have an ``ssd`` attribute.
        This attribute indicates if the ScsiDisk is SSD backed. As this option is optional,
        if a relevant disk in the StorageSystem does not have ``ssd = true``, it will end
        up in the ``non_ssds`` list here.

    host_name
        Filter by this ESXi hostname (optional)

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vsphere.list_non_ssds
    """
    log.debug("Running vmware_vsphere.list_non_ssds")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )
    for host in hosts:
        names = []
        disks = _get_host_disks(host).get("Non-SSDs")
        for disk in disks:
            names.append(disk.canonicalName)
        ret.update({host.name: names})

    return ret
