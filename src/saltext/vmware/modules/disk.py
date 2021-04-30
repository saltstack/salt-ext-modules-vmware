# SPDX-License-Identifier: Apache-2.0
import logging
import sys

import saltext.vmware.utils.vmware
from salt.utils.decorators import depends
from salt.utils.decorators import ignores_kwargs

log = logging.getLogger(__name__)

try:
    # pylint: disable=no-name-in-module
    from pyVmomi import (
        vim,
        vmodl,
        pbm,
        VmomiSupport,
    )

    # pylint: enable=no-name-in-module

    # We check the supported vim versions to infer the pyVmomi version
    if (
        "vim25/6.0" in VmomiSupport.versionMap
        and sys.version_info > (2, 7)
        and sys.version_info < (2, 7, 9)
    ):

        log.debug("pyVmomi not loaded: Incompatible versions " "of Python. See Issue #29537.")
        raise ImportError()
    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_disk"


def __virtual__():
    return __virtualname__


def list_disks(disk_ids=None, scsi_addresses=None, service_instance=None):
    """
    Returns a list of dict representations of the disks in an ESXi host.
    The list of disks can be filtered by disk canonical names or
    scsi addresses.

    disk_ids:
        List of disk canonical names to be retrieved. Default is None.

    scsi_addresses
        List of scsi addresses of disks to be retrieved. Default is None


    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.list_disks

        salt '*' vsphere.list_disks disk_ids='[naa.00, naa.001]'

        salt '*' vsphere.list_disks
            scsi_addresses='[vmhba0:C0:T0:L0, vmhba1:C0:T0:L0]'
    """
    host_ref = _get_proxy_target(service_instance)
    hostname = __proxy__["esxi.get_details"]()["esxi_host"]
    log.trace("Retrieving disks if host '{}'".format(hostname))
    log.trace("disk ids = {}".format(disk_ids))
    log.trace("scsi_addresses = {}".format(scsi_addresses))
    # Default to getting all disks if no filtering is done
    get_all_disks = True if not (disk_ids or scsi_addresses) else False
    ret_list = []
    scsi_address_to_lun = saltext.vmware.utils.vmware.get_scsi_address_to_lun_map(
        host_ref, hostname=hostname
    )
    canonical_name_to_scsi_address = {
        lun.canonicalName: scsi_addr for scsi_addr, lun in scsi_address_to_lun.items()
    }
    for d in saltext.vmware.utils.vmware.get_disks(
        host_ref, disk_ids, scsi_addresses, get_all_disks
    ):
        ret_list.append(
            {
                "id": d.canonicalName,
                "scsi_address": canonical_name_to_scsi_address[d.canonicalName],
            }
        )
    return ret_list


def erase_disk_partitions(disk_id=None, scsi_address=None, service_instance=None):
    """
    Erases the partitions on a disk.
    The disk can be specified either by the canonical name, or by the
    scsi_address.

    disk_id
        Canonical name of the disk.
        Either ``disk_id`` or ``scsi_address`` needs to be specified
        (``disk_id`` supersedes ``scsi_address``.

    scsi_address
        Scsi address of the disk.
        ``disk_id`` or ``scsi_address`` needs to be specified
        (``disk_id`` supersedes ``scsi_address``.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.erase_disk_partitions scsi_address='vmhaba0:C0:T0:L0'

        salt '*' vsphere.erase_disk_partitions disk_id='naa.000000000000001'
    """
    if not disk_id and not scsi_address:
        raise ArgumentValueError("Either 'disk_id' or 'scsi_address' " "needs to be specified")
    host_ref = _get_proxy_target(service_instance)
    hostname = __proxy__["esxi.get_details"]()["esxi_host"]
    if not disk_id:
        scsi_address_to_lun = saltext.vmware.utils.vmware.get_scsi_address_to_lun_map(host_ref)
        if scsi_address not in scsi_address_to_lun:
            raise VMwareObjectRetrievalError(
                "Scsi lun with address '{}' was not found on host '{}'"
                "".format(scsi_address, hostname)
            )
        disk_id = scsi_address_to_lun[scsi_address].canonicalName
        log.trace(
            "[{}] Got disk id '{}' for scsi address '{}'" "".format(hostname, disk_id, scsi_address)
        )
    log.trace("Erasing disk partitions on disk '{}' in host '{}'" "".format(disk_id, hostname))
    saltext.vmware.utils.vmware.erase_disk_partitions(
        service_instance, host_ref, disk_id, hostname=hostname
    )
    log.info("Erased disk partitions on disk '{}' on host '{}'" "".format(disk_id, hostname))
    return True


def list_disk_partitions(disk_id=None, scsi_address=None, service_instance=None):
    """
    Lists the partitions on a disk.
    The disk can be specified either by the canonical name, or by the
    scsi_address.

    disk_id
        Canonical name of the disk.
        Either ``disk_id`` or ``scsi_address`` needs to be specified
        (``disk_id`` supersedes ``scsi_address``.

    scsi_address`
        Scsi address of the disk.
        ``disk_id`` or ``scsi_address`` needs to be specified
        (``disk_id`` supersedes ``scsi_address``.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.list_disk_partitions scsi_address='vmhaba0:C0:T0:L0'

        salt '*' vsphere.list_disk_partitions disk_id='naa.000000000000001'
    """
    if not disk_id and not scsi_address:
        raise ArgumentValueError("Either 'disk_id' or 'scsi_address' " "needs to be specified")
    host_ref = _get_proxy_target(service_instance)
    hostname = __proxy__["esxi.get_details"]()["esxi_host"]
    if not disk_id:
        scsi_address_to_lun = saltext.vmware.utils.vmware.get_scsi_address_to_lun_map(host_ref)
        if scsi_address not in scsi_address_to_lun:
            raise VMwareObjectRetrievalError(
                "Scsi lun with address '{}' was not found on host '{}'"
                "".format(scsi_address, hostname)
            )
        disk_id = scsi_address_to_lun[scsi_address].canonicalName
        log.trace(
            "[{}] Got disk id '{}' for scsi address '{}'" "".format(hostname, disk_id, scsi_address)
        )
    log.trace("Listing disk partitions on disk '{}' in host '{}'" "".format(disk_id, hostname))
    partition_info = saltext.vmware.utils.vmware.get_disk_partition_info(host_ref, disk_id)
    ret_list = []
    # NOTE: 1. The layout view has an extra 'None' partition for free space
    #       2. The orders in the layout/partition views are not the same
    for part_spec in partition_info.spec.partition:
        part_layout = [
            p for p in partition_info.layout.partition if p.partition == part_spec.partition
        ][0]
        part_dict = {
            "hostname": hostname,
            "device": disk_id,
            "format": partition_info.spec.partitionFormat,
            "partition": part_spec.partition,
            "type": part_spec.type,
            "sectors": part_spec.endSector - part_spec.startSector + 1,
            "size_KB": (part_layout.end.block - part_layout.start.block + 1)
            * part_layout.start.blockSize
            / 1024,
        }
        ret_list.append(part_dict)
    return ret_list


def list_diskgroups(cache_disk_ids=None, service_instance=None):
    """
    Returns a list of disk group dict representation on an ESXi host.
    The list of disk groups can be filtered by the cache disks
    canonical names. If no filtering is applied, all disk groups are returned.

    cache_disk_ids:
        List of cache disk canonical names of the disk groups to be retrieved.
        Default is None.

    use_proxy_details
        Specify whether to use the proxy minion's details instead of the
        arguments

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.list_diskgroups

        salt '*' vsphere.list_diskgroups cache_disk_ids='[naa.000000000000001]'
    """
    host_ref = _get_proxy_target(service_instance)
    hostname = __proxy__["esxi.get_details"]()["esxi_host"]
    log.trace("Listing diskgroups in '{}'".format(hostname))
    get_all_diskgroups = True if not cache_disk_ids else False
    ret_list = []
    for dg in saltext.vmware.utils.vmware.get_diskgroups(
        host_ref, cache_disk_ids, get_all_diskgroups
    ):
        ret_list.append(
            {
                "cache_disk": dg.ssd.canonicalName,
                "capacity_disks": [d.canonicalName for d in dg.nonSsd],
            }
        )
    return ret_list


def create_diskgroup(cache_disk_id, capacity_disk_ids, safety_checks=True, service_instance=None):
    """
    Creates disk group on an ESXi host with the specified cache and
    capacity disks.

    cache_disk_id
        The canonical name of the disk to be used as a cache. The disk must be
        ssd.

    capacity_disk_ids
        A list containing canonical names of the capacity disks. Must contain at
        least one id. Default is True.

    safety_checks
        Specify whether to perform safety check or to skip the checks and try
        performing the required task. Default value is True.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.create_diskgroup cache_disk_id='naa.000000000000001'
            capacity_disk_ids='[naa.000000000000002, naa.000000000000003]'
    """
    log.trace("Validating diskgroup input")
    schema = DiskGroupsDiskIdSchema.serialize()
    try:
        jsonschema.validate(
            {"diskgroups": [{"cache_id": cache_disk_id, "capacity_ids": capacity_disk_ids}]},
            schema,
        )
    except jsonschema.exceptions.ValidationError as exc:
        raise ArgumentValueError(exc)
    host_ref = _get_proxy_target(service_instance)
    hostname = __proxy__["esxi.get_details"]()["esxi_host"]
    if safety_checks:
        diskgroups = saltext.vmware.utils.vmware.get_diskgroups(host_ref, [cache_disk_id])
        if diskgroups:
            raise VMwareObjectExistsError(
                "Diskgroup with cache disk id '{}' already exists ESXi "
                "host '{}'".format(cache_disk_id, hostname)
            )
    disk_ids = capacity_disk_ids[:]
    disk_ids.insert(0, cache_disk_id)
    disks = saltext.vmware.utils.vmware.get_disks(host_ref, disk_ids=disk_ids)
    for id in disk_ids:
        if not [d for d in disks if d.canonicalName == id]:
            raise VMwareObjectRetrievalError(
                "No disk with id '{}' was found in ESXi host '{}'" "".format(id, hostname)
            )
    cache_disk = [d for d in disks if d.canonicalName == cache_disk_id][0]
    capacity_disks = [d for d in disks if d.canonicalName in capacity_disk_ids]
    vsan_disk_mgmt_system = salt.utils.vsan.get_vsan_disk_management_system(service_instance)
    dg = salt.utils.vsan.create_diskgroup(
        service_instance, vsan_disk_mgmt_system, host_ref, cache_disk, capacity_disks
    )
    return True


def add_capacity_to_diskgroup(
    cache_disk_id, capacity_disk_ids, safety_checks=True, service_instance=None
):
    """
    Adds capacity disks to the disk group with the specified cache disk.

    cache_disk_id
        The canonical name of the cache disk.

    capacity_disk_ids
        A list containing canonical names of the capacity disks to add.

    safety_checks
        Specify whether to perform safety check or to skip the checks and try
        performing the required task. Default value is True.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.add_capacity_to_diskgroup
            cache_disk_id='naa.000000000000001'
            capacity_disk_ids='[naa.000000000000002, naa.000000000000003]'
    """
    log.trace("Validating diskgroup input")
    schema = DiskGroupsDiskIdSchema.serialize()
    try:
        jsonschema.validate(
            {"diskgroups": [{"cache_id": cache_disk_id, "capacity_ids": capacity_disk_ids}]},
            schema,
        )
    except jsonschema.exceptions.ValidationError as exc:
        raise ArgumentValueError(exc)
    host_ref = _get_proxy_target(service_instance)
    hostname = __proxy__["esxi.get_details"]()["esxi_host"]
    disks = saltext.vmware.utils.vmware.get_disks(host_ref, disk_ids=capacity_disk_ids)
    if safety_checks:
        for id in capacity_disk_ids:
            if not [d for d in disks if d.canonicalName == id]:
                raise VMwareObjectRetrievalError(
                    "No disk with id '{}' was found in ESXi host '{}'" "".format(id, hostname)
                )
    diskgroups = saltext.vmware.utils.vmware.get_diskgroups(
        host_ref, cache_disk_ids=[cache_disk_id]
    )
    if not diskgroups:
        raise VMwareObjectRetrievalError(
            "No diskgroup with cache disk id '{}' was found in ESXi "
            "host '{}'".format(cache_disk_id, hostname)
        )
    vsan_disk_mgmt_system = salt.utils.vsan.get_vsan_disk_management_system(service_instance)
    salt.utils.vsan.add_capacity_to_diskgroup(
        service_instance, vsan_disk_mgmt_system, host_ref, diskgroups[0], disks
    )
    return True


def remove_capacity_from_diskgroup(
    cache_disk_id,
    capacity_disk_ids,
    data_evacuation=True,
    safety_checks=True,
    service_instance=None,
):
    """
    Remove capacity disks from the disk group with the specified cache disk.

    cache_disk_id
        The canonical name of the cache disk.

    capacity_disk_ids
        A list containing canonical names of the capacity disks to add.

    data_evacuation
        Specifies whether to gracefully evacuate the data on the capacity disks
        before removing them from the disk group. Default value is True.

    safety_checks
        Specify whether to perform safety check or to skip the checks and try
        performing the required task. Default value is True.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.remove_capacity_from_diskgroup
            cache_disk_id='naa.000000000000001'
            capacity_disk_ids='[naa.000000000000002, naa.000000000000003]'
    """
    log.trace("Validating diskgroup input")
    schema = DiskGroupsDiskIdSchema.serialize()
    try:
        jsonschema.validate(
            {"diskgroups": [{"cache_id": cache_disk_id, "capacity_ids": capacity_disk_ids}]},
            schema,
        )
    except jsonschema.exceptions.ValidationError as exc:
        raise ArgumentValueError(str(exc))
    host_ref = _get_proxy_target(service_instance)
    hostname = __proxy__["esxi.get_details"]()["esxi_host"]
    disks = saltext.vmware.utils.vmware.get_disks(host_ref, disk_ids=capacity_disk_ids)
    if safety_checks:
        for id in capacity_disk_ids:
            if not [d for d in disks if d.canonicalName == id]:
                raise VMwareObjectRetrievalError(
                    "No disk with id '{}' was found in ESXi host '{}'" "".format(id, hostname)
                )
    diskgroups = saltext.vmware.utils.vmware.get_diskgroups(
        host_ref, cache_disk_ids=[cache_disk_id]
    )
    if not diskgroups:
        raise VMwareObjectRetrievalError(
            "No diskgroup with cache disk id '{}' was found in ESXi "
            "host '{}'".format(cache_disk_id, hostname)
        )
    log.trace("data_evacuation = {}".format(data_evacuation))
    salt.utils.vsan.remove_capacity_from_diskgroup(
        service_instance,
        host_ref,
        diskgroups[0],
        capacity_disks=[d for d in disks if d.canonicalName in capacity_disk_ids],
        data_evacuation=data_evacuation,
    )
    return True


def remove_diskgroup(cache_disk_id, data_accessibility=True, service_instance=None):
    """
    Remove the diskgroup with the specified cache disk.

    cache_disk_id
        The canonical name of the cache disk.

    data_accessibility
        Specifies whether to ensure data accessibility. Default value is True.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.remove_diskgroup cache_disk_id='naa.000000000000001'
    """
    log.trace("Validating diskgroup input")
    host_ref = _get_proxy_target(service_instance)
    hostname = __proxy__["esxi.get_details"]()["esxi_host"]
    diskgroups = saltext.vmware.utils.vmware.get_diskgroups(
        host_ref, cache_disk_ids=[cache_disk_id]
    )
    if not diskgroups:
        raise VMwareObjectRetrievalError(
            "No diskgroup with cache disk id '{}' was found in ESXi "
            "host '{}'".format(cache_disk_id, hostname)
        )
    log.trace("data accessibility = {}".format(data_accessibility))
    salt.utils.vsan.remove_diskgroup(
        service_instance, host_ref, diskgroups[0], data_accessibility=data_accessibility
    )
    return True
