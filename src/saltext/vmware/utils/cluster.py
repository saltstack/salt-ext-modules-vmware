import logging

import salt.exceptions
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.datacenter as utils_datacenter

# pylint: disable=no-name-in-module
try:
    from pyVmomi import vim, vmodl

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False

log = logging.getLogger(__name__)


def get_cluster(dc_ref, cluster):
    """
    Returns a cluster in a datacenter.

    dc_ref
        The datacenter reference

    cluster
        The cluster to be retrieved
    """
    dc_name = utils_common.get_managed_object_name(dc_ref)
    log.trace("Retrieving cluster '%s' from datacenter '%s'", cluster, dc_name)
    si = utils_common.get_service_instance_from_managed_object(dc_ref, name=dc_name)
    traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(
        path="hostFolder",
        skip=True,
        type=vim.Datacenter,
        selectSet=[
            vmodl.query.PropertyCollector.TraversalSpec(
                path="childEntity", skip=False, type=vim.Folder
            )
        ],
    )
    items = [
        i["object"]
        for i in utils_common.get_mors_with_properties(
            si,
            vim.ClusterComputeResource,
            container_ref=dc_ref,
            property_list=["name"],
            traversal_spec=traversal_spec,
        )
        if i["name"] == cluster
    ]
    if not items:
        raise salt.exceptions.VMwareObjectRetrievalError(
            "Cluster '{}' was not found in datacenter " "'{}'".format(cluster, dc_name)
        )
    return items[0]


def create_cluster(dc_ref, cluster_name, cluster_spec):
    """
    Creates a cluster in a datacenter.

    dc_ref
        The parent datacenter reference.

    cluster_name
        The cluster name.

    cluster_spec
        The cluster spec (vim.ClusterConfigSpecEx).
        Defaults to None.
    """
    dc_name = utils_common.get_managed_object_name(dc_ref)
    log.trace("Creating cluster '%s' in datacenter '%s'", cluster_name, dc_name)
    try:
        dc_ref.hostFolder.CreateClusterEx(cluster_name, cluster_spec)
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)


def update_cluster(cluster_ref, cluster_spec):
    """
    Updates a cluster in a datacenter.

    cluster_ref
        The cluster reference.

    cluster_spec
        The cluster spec (vim.ClusterConfigSpecEx).
        Defaults to None.
    """
    cluster_name = utils_common.get_managed_object_name(cluster_ref)
    log.trace("Updating cluster '%s'", cluster_name)
    try:
        task = cluster_ref.ReconfigureComputeResource_Task(cluster_spec, modify=True)
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    utils_common.wait_for_task(task, cluster_name, "ClusterUpdateTask")


def delete_cluster(service_instance, cluster_name, datacenter_name):
    """
    Deletes a datacenter.

    service_instance
        The Service Instance Object

    cluster_name
        The name of the cluster to delete

    datacenter_name
        The datacenter name to which the cluster belongs
    """
    root_folder = utils_common.get_root_folder(service_instance)
    log.trace("Deleting cluster '%s' in '%s'", cluster_name, datacenter_name)
    try:
        dc_obj = utils_datacenter.get_datacenter(service_instance, datacenter_name)
        cluster_obj = get_cluster(dc_ref=dc_obj, cluster=cluster_name)
        task = cluster_obj.Destroy_Task()
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: {}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    utils_common.wait_for_task(task, cluster_name, "DeleteClusterTask")


def list_clusters(service_instance):
    """
    Returns a list of clusters associated with a given service instance.

    service_instance
        The Service Instance Object from which to obtain clusters.
    """
    return utils_common.list_objects(service_instance, vim.ClusterComputeResource)
