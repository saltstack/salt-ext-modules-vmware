# Copyright 2021 VMware, Inc.
# SPDX-License: Apache-2.0
import logging

import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.connect as connect
import saltext.vmware.utils.datastore as utils_datastore
import saltext.vmware.utils.esxi as utils_esxi

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_datastore"


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def maintenance_mode(datastore_name, datacenter_name=None, service_instance=None, profile=None):
    """
    Put datastore in maintenance mode.

    datastore_name
        Name of datastore.

    datacenter_name
        (optional) Name of datacenter where datastore exists.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    assert isinstance(datastore_name, str)
    datastores = utils_datastore.get_datastores(
        service_instance, datastore_name=datastore_name, datacenter_name=datacenter_name
    )
    ds = datastores[0] if datastores else None
    ret = utils_datastore.enter_maintenance_mode(ds)
    if ret:
        return {"maintenanceMode": "inMaintenance"}
    return {"maintenanceMode": "failed to enter maintenance mode"}


def exit_maintenance_mode(
    datastore_name, datacenter_name=None, service_instance=None, profile=None
):
    """
    Take datastore out of maintenance mode.

    datastore_name
        Name of datastore.

    datacenter_name
        (optional) Name of datacenter where datastore exists.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    assert isinstance(datastore_name, str)
    datastores = utils_datastore.get_datastores(
        service_instance, datastore_name=datastore_name, datacenter_name=datacenter_name
    )
    ds = datastores[0] if datastores else None
    ret = utils_datastore.exit_maintenance_mode(ds)
    if ret:
        return {"maintenanceMode": "normal"}
    return {"maintenanceMode": "failed to exit maintenance mode"}


def get(
    datastore_name=None,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Return info about datastores.

    datastore_name
        Filter by this datastore name (required when cluster is not specified)

    datacenter_name
        Filter by this datacenter name (required when cluster is not specified)

    cluster_name
        Filter by this cluster name (required when datacenter is not specified)

    host_name
        Filter by this ESXi hostname (optional).

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)
    """
    log.debug(f"Running {__virtualname__}.get")
    ret = []
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    datastores = utils_datastore.get_datastores(
        service_instance,
        datastore_name=datastore_name,
        datacenter_name=datacenter_name,
        cluster_name=cluster_name,
        host_name=host_name,
    )

    for datastore in datastores:
        summary = datastore.summary
        info = {
            "accessible": summary.accessible,
            "capacity": summary.capacity,
            "freeSpace": summary.freeSpace,
            "maintenanceMode": summary.maintenanceMode,
            "multipleHostAccess": summary.multipleHostAccess,
            "name": summary.name,
            "type": summary.type,
            "url": summary.url,
            "uncommitted": summary.uncommitted if summary.uncommitted else 0,
        }
        ret.append(info)

    return ret


def list_datastores(
    datastore_names=None,
    backing_disk_ids=None,
    backing_disk_scsi_addresses=None,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Returns a list of dict representations of the datastores visible to the
    proxy object. The list of datastores can be filtered by datastore names,
    backing disk ids (canonical names) or backing disk scsi addresses.
    Supported proxy types: esxi, esxcluster, esxdatacenter

    datastore_names
        List of the names of datastores to filter on

    backing_disk_ids
        List of canonical names of the backing disks of the datastores to filer.
        Default is None.

    backing_disk_scsi_addresses
        List of scsi addresses of the backing disks of the datastores to filter.
        Default is None.

    datacenter_name
        Filter by this datacenter name (required when cluster is not specified)

    cluster_name
        Filter by this cluster name (required when datacenter is not specified)

    host_name
        Filter by this ESXi hostname (optional).

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_datastore.list_datastores
        salt '*' vmware_datastore.list_datastores datastore_names=[ds1, ds2]
    """
    log.debug("Running vmware_datastore.list_datastores")
    ret = {}
    service_instance = service_instance or connect.get_service_instance(
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
        # Default to getting all disks if no filtering is done
        get_all_datastores = (
            True
            if not (datastore_names or backing_disk_ids or backing_disk_scsi_addresses)
            else False
        )
        # Get the ids of the disks with the scsi addresses
        if backing_disk_scsi_addresses:
            log.debug("Retrieving disk ids for scsi addresses '%s'", backing_disk_scsi_addresses)
            disk_ids = [
                d.canonicalName
                for d in utils_common.get_disks(host, scsi_addresses=backing_disk_scsi_addresses)
            ]
            log.debug("Found disk ids '%s'", disk_ids)
            backing_disk_ids = backing_disk_ids.extend(disk_ids) if backing_disk_ids else disk_ids
        datastores = utils_datastore.get_datastores_from_ref(
            service_instance, host, datastore_names, backing_disk_ids, get_all_datastores
        )

        # Search for disk backed datastores if target is host
        # to be able to add the backing_disk_ids
        mount_infos = []
        if isinstance(host, vim.HostSystem):
            storage_system = utils_common.get_storage_system(service_instance, host, host.name)
            props = utils_common.get_properties_of_managed_object(
                storage_system, ["fileSystemVolumeInfo.mountInfo"]
            )
            mount_infos = props.get("fileSystemVolumeInfo.mountInfo", [])
        ret[host.name] = []
        for datastore in datastores:
            datastore_dict = {
                "name": datastore.name,
                "type": datastore.summary.type,
                "free_space": datastore.summary.freeSpace,
                "capacity": datastore.summary.capacity,
            }
            backing_disk_ids = []
            for vol in [
                i.volume
                for i in mount_infos
                if i.volume.name == datastore.name and isinstance(i.volume, vim.HostVmfsVolume)
            ]:

                backing_disk_ids.extend([e.diskName for e in vol.extent])
            if backing_disk_ids:
                datastore_dict["backing_disk_ids"] = backing_disk_ids
            ret[host.name].append(datastore_dict)
    return ret
