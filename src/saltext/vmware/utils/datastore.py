# Copyright 2022 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import salt.exceptions
import salt.modules.cmdmod
import salt.utils.path
import salt.utils.platform
import salt.utils.stringutils
import saltext.vmware.utils.common as utils_common

try:
    from pyVmomi import vim, vmodl

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


log = logging.getLogger(__name__)


def __virtual__():
    """
    Only load if PyVmomi is installed.
    """
    if HAS_PYVMOMI:
        return True

    return False, "Missing dependency: The salt.utils.vmware module requires pyVmomi."


# 3 datastore functions are still in utils/vmware.py:
# def list_datastores(service_instance):
# def get_datastore_files(service_instance, directory, datastores, container_object, browser_spec):
# def rename_datastore(datastore_ref, new_datastore_name):


def list_datastore_clusters(service_instance):
    """
    Returns a list of datastore clusters associated with a given service instance.

    service_instance
        The Service Instance Object from which to obtain datastore clusters.
    """
    return utils_common.list_objects(service_instance, vim.StoragePod)


def get_datastores_from_ref(
    service_instance,
    reference,
    datastore_names=None,
    backing_disk_ids=None,
    get_all_datastores=False,
):
    """
    Returns a list of vim.Datastore objects representing the datastores visible
    from a VMware object, filtered by their names, or the backing disk
    cannonical name or scsi_addresses

    service_instance
        The Service Instance Object from which to obtain datastores.

    reference
        The VMware object from which the datastores are visible.

    datastore_names
        The list of datastore names to be retrieved. Default value is None.

    backing_disk_ids
        The list of canonical names of the disks backing the datastores
        to be retrieved. Only supported if reference is a vim.HostSystem.
        Default value is None

    get_all_datastores
        Specifies whether to retrieve all disks in the host.
        Default value is False.
    """
    obj_name = utils_common.get_managed_object_name(reference)
    if get_all_datastores:
        log.trace("Retrieving all datastores visible to '%s'", obj_name)
    else:
        log.trace(
            "Retrieving datastores visible to '%s': names = (%s); " "backing disk ids = (%s)",
            obj_name,
            datastore_names,
            backing_disk_ids,
        )
        if backing_disk_ids and not isinstance(reference, vim.HostSystem):

            raise salt.exceptions.ArgumentValueError(
                "Unsupported reference type '{}' when backing disk filter "
                "is set".format(reference.__class__.__name__)
            )
    if (not get_all_datastores) and backing_disk_ids:
        # At this point we know the reference is a vim.HostSystem
        log.trace("Filtering datastores with backing disk ids: %s", backing_disk_ids)
        storage_system = get_storage_system(service_instance, reference, obj_name)
        props = utils_common.get_properties_of_managed_object(
            storage_system, ["fileSystemVolumeInfo.mountInfo"]
        )
        mount_infos = props.get("fileSystemVolumeInfo.mountInfo", [])
        disk_datastores = []
        # Non vmfs volumes aren't backed by a disk
        for vol in [i.volume for i in mount_infos if isinstance(i.volume, vim.HostVmfsVolume)]:

            if not [e for e in vol.extent if e.diskName in backing_disk_ids]:
                # Skip volume if it doesn't contain an extent with a
                # canonical name of interest
                continue
            log.trace(
                "Found datastore '%s' for disk id(s) '%s'",
                vol.name,
                [e.diskName for e in vol.extent],
            )
            disk_datastores.append(vol.name)
        log.trace("Datastore found for disk filter: %s", disk_datastores)
        if datastore_names:
            datastore_names.extend(disk_datastores)
        else:
            datastore_names = disk_datastores

    if (not get_all_datastores) and (not datastore_names):
        log.trace(
            "No datastore to be filtered after retrieving the datastores "
            "backed by the disk id(s) '%s'",
            backing_disk_ids,
        )
        return []

    log.trace("datastore_names = %s", datastore_names)

    # Use the default traversal spec
    if isinstance(reference, vim.HostSystem):
        # Create a different traversal spec for hosts because it looks like the
        # default doesn't retrieve the datastores
        traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(
            name="host_datastore_traversal",
            path="datastore",
            skip=False,
            type=vim.HostSystem,
        )
    elif isinstance(reference, vim.ClusterComputeResource):
        # Traversal spec for clusters
        traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(
            name="cluster_datastore_traversal",
            path="datastore",
            skip=False,
            type=vim.ClusterComputeResource,
        )
    elif isinstance(reference, vim.Datacenter):
        # Traversal spec for datacenter
        traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(
            name="datacenter_datastore_traversal",
            path="datastore",
            skip=False,
            type=vim.Datacenter,
        )
    elif isinstance(reference, vim.StoragePod):
        # Traversal spec for datastore clusters
        traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(
            name="datastore_cluster_traversal",
            path="childEntity",
            skip=False,
            type=vim.StoragePod,
        )
    elif (
        isinstance(reference, vim.Folder)
        and utils_common.get_managed_object_name(reference) == "Datacenters"
    ):
        # Traversal of root folder (doesn't support multiple levels of Folders)
        traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(
            path="childEntity",
            selectSet=[
                vmodl.query.PropertyCollector.TraversalSpec(
                    path="datastore", skip=False, type=vim.Datacenter
                )
            ],
            skip=False,
            type=vim.Folder,
        )
    else:
        raise salt.exceptions.ArgumentValueError(
            "Unsupported reference type '{}'" "".format(reference.__class__.__name__)
        )

    items = utils_common.get_mors_with_properties(
        service_instance,
        object_type=vim.Datastore,
        property_list=["name"],
        container_ref=reference,
        traversal_spec=traversal_spec,
    )
    log.trace("Retrieved %s datastores", len(items))
    items = [i for i in items if get_all_datastores or i["name"] in datastore_names]
    log.trace("Filtered datastores: %s", [i["name"] for i in items])
    return [i["object"] for i in items]


def get_storage_system(service_instance, host_ref, hostname=None):
    """
    Returns a host's storage system
    """

    if not hostname:
        hostname = utils_common.get_managed_object_name(host_ref)

    traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(
        path="configManager.storageSystem", type=vim.HostSystem, skip=False
    )
    objs = utils_common.get_mors_with_properties(
        service_instance,
        vim.HostStorageSystem,
        property_list=["systemFile"],
        container_ref=host_ref,
        traversal_spec=traversal_spec,
    )
    if not objs:
        raise salt.exceptions.VMwareObjectRetrievalError(
            "Host's '{}' storage system was not retrieved" "".format(hostname)
        )
    log.trace("[%s] Retrieved storage system", hostname)
    return objs[0]["object"]


def get_datastores(
    service_instance, datastore_name=None, datacenter_name=None, cluster_name=None, host_name=None
):
    """
    Gets datastores on the most specific of host_name, cluster_name, datacenter_name, or everywhere.

    Then optionally filters them by datastore_name.
    """
    if datacenter_name or cluster_name or host_name:
        reference = utils_common.find_filtered_object(
            service_instance,
            datacenter_name=datacenter_name,
            cluster_name=cluster_name,
            host_name=host_name,
        )
        return get_datastores_from_ref(
            service_instance,
            reference=reference,
            datastore_names=[datastore_name],
            get_all_datastores=not datastore_name,
        )
    else:
        # TODO: update get_datastores_from_ref to work recursively
        # get_datastores_from_ref doesn't actually find all datastores when
        #  searching everything, this should work
        datastores = utils_common.get_mors_with_properties(
            service_instance, vim.Datastore, property_list=["name"]
        )
        if not datastore_name:
            return [datastore["object"] for datastore in datastores]
        else:
            return [
                datastore["object"]
                for datastore in datastores
                if datastore["name"] == datastore_name
            ]


def enter_maintenance_mode(datastore_ref):
    """
    Put datastore in maintenance mode.

    datastore_ref
        Reference to datastore.
    """
    ret = datastore_ref.DatastoreEnterMaintenanceMode()
    utils_common.wait_for_task(ret.task, datastore_ref.name, "Put datastore in maintenance mode")
    if datastore_ref.summary.maintenanceMode == "inMaintenance":
        return True
    return False


def exit_maintenance_mode(datastore_ref):
    """
    Take datastore out of maintenance mode.

    datastore_ref
        Reference to datastore.
    """
    task = datastore_ref.DatastoreExitMaintenanceMode_Task()
    utils_common.wait_for_task(task, datastore_ref.name, "Take datastore out of maintenance mode")
    if datastore_ref.summary.maintenanceMode == "normal":
        return True
    return False
