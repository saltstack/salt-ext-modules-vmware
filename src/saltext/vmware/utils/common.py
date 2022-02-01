# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Common functions used across modules
"""
import errno
import logging
import re
import time
from http.client import BadStatusLine

import salt.exceptions
import salt.modules.cmdmod
import salt.utils.path
import salt.utils.platform
import salt.utils.stringutils

try:
    from pyVmomi import vim, vmodl

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False

CAMELCASE_PATTERN = re.compile("((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))")

log = logging.getLogger(__name__)


def camel_to_snake_case(attrib):
    return CAMELCASE_PATTERN.sub(r"_\1", attrib).lower()


def get_root_folder(service_instance):
    """
    Returns the root folder of a vCenter.

    service_instance
        The Service Instance Object for which to obtain the root folder.

    """
    try:
        log.trace("Retrieving root folder")
        return service_instance.RetrieveContent().rootFolder
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


def get_service_content(service_instance):
    """
    Returns the service content for a Service Instance.

    service_instance
        The Service Instance from which to obtain service content.
    """
    try:
        return service_instance.RetrieveServiceContent()
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            f"Not enough permissions. Required privilege: '{exc.privilegeId}'"
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)


def get_content(
    service_instance,
    obj_type,
    property_list=None,
    container_ref=None,
    traversal_spec=None,
    local_properties=False,
):
    """
    Returns the content of the specified type of object for a Service Instance.

    For more information, please see:
    http://pubs.vmware.com/vsphere-50/index.jsp?topic=%2Fcom.vmware.wssdk.pg.doc_50%2FPG_Ch5_PropertyCollector.7.6.html

    service_instance
        The Service Instance from which to obtain content.

    obj_type
        The type of content to obtain.

    property_list
        An optional list of object properties to used to return even more filtered content results.

    container_ref
        An optional reference to the managed object to search under. Can either be an object of type Folder, Datacenter,
        ComputeResource, Resource Pool or HostSystem. If not specified, default behaviour is to search under the inventory
        rootFolder.

    traversal_spec
        An optional TraversalSpec to be used instead of the standard
        ``Traverse All`` spec.

    local_properties
        Flag specifying whether the properties to be retrieved are local to the
        container. If that is the case, the traversal spec needs to be None.
    """
    # Start at the rootFolder if container starting point not specified
    if not container_ref:
        container_ref = get_root_folder(service_instance)

    # By default, the object reference used as the starting poing for the filter
    # is the container_ref passed in the function
    obj_ref = container_ref
    local_traversal_spec = False
    if not traversal_spec and not local_properties:
        local_traversal_spec = True
        # We don't have a specific traversal spec override so we are going to
        # get everything using a container view
        try:
            obj_ref = service_instance.content.viewManager.CreateContainerView(
                container_ref, [obj_type], True
            )
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

        # Create 'Traverse All' traversal spec to determine the path for
        # collection
        traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(
            name="traverseEntities",
            path="view",
            skip=False,
            type=vim.view.ContainerView,
        )

    # Create property spec to determine properties to be retrieved
    property_spec = vmodl.query.PropertyCollector.PropertySpec(
        type=obj_type, all=True if not property_list else False, pathSet=property_list
    )

    # Create object spec to navigate content
    obj_spec = vmodl.query.PropertyCollector.ObjectSpec(
        obj=obj_ref,
        skip=True if not local_properties else False,
        selectSet=[traversal_spec] if not local_properties else None,
    )

    # Create a filter spec and specify object, property spec in it
    filter_spec = vmodl.query.PropertyCollector.FilterSpec(
        objectSet=[obj_spec],
        propSet=[property_spec],
        reportMissingObjectsInResults=False,
    )

    # Retrieve the contents
    try:
        content = service_instance.content.propertyCollector.RetrieveContents([filter_spec])
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

    # Destroy the object view
    if local_traversal_spec:
        try:
            obj_ref.Destroy()
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

    return content


def get_mors_with_properties(
    service_instance,
    object_type,
    property_list=None,
    container_ref=None,
    traversal_spec=None,
    local_properties=False,
):
    """
    Returns a list containing properties and managed object references for the managed object.

    service_instance
        The Service Instance from which to obtain managed object references.

    object_type
        The type of content for which to obtain managed object references.

    property_list
        An optional list of object properties used to return even more filtered managed object reference results.

    container_ref
        An optional reference to the managed object to search under. Can either be an object of type Folder, Datacenter,
        ComputeResource, Resource Pool or HostSystem. If not specified, default behaviour is to search under the inventory
        rootFolder.

    traversal_spec
        An optional TraversalSpec to be used instead of the standard
        ``Traverse All`` spec

    local_properties
        Flag specifying whether the properties to be retrieved are local to the
        container. If that is the case, the traversal spec needs to be None.
    """
    # Get all the content
    content_args = [service_instance, object_type]
    content_kwargs = {
        "property_list": property_list,
        "container_ref": container_ref,
        "traversal_spec": traversal_spec,
        "local_properties": local_properties,
    }
    try:
        content = get_content(*content_args, **content_kwargs)
    except BadStatusLine:
        content = get_content(*content_args, **content_kwargs)
    except OSError as exc:
        if exc.errno != errno.EPIPE:
            raise
        content = get_content(*content_args, **content_kwargs)

    object_list = []
    for obj in content:
        properties = {}
        for prop in obj.propSet:
            properties[prop.name] = prop.val
        properties["object"] = obj.obj
        object_list.append(properties)
    log.trace("Retrieved %s objects", len(object_list))
    return object_list


def get_mor_by_property(
    service_instance,
    object_type,
    property_value,
    property_name="name",
    container_ref=None,
):
    """
    Returns the first managed object reference having the specified property value.

    service_instance
        The Service Instance from which to obtain managed object references.

    object_type
        The type of content for which to obtain managed object references.

    property_value
        The name of the property for which to obtain the managed object reference.

    property_name
        An object property used to return the specified object reference results. Defaults to ``name``.

    container_ref
        An optional reference to the managed object to search under. Can either be an object of type Folder, Datacenter,
        ComputeResource, Resource Pool or HostSystem. If not specified, default behaviour is to search under the inventory
        rootFolder.
    """
    # Get list of all managed object references with specified property
    object_list = get_mors_with_properties(
        service_instance,
        object_type,
        property_list=[property_name],
        container_ref=container_ref,
    )

    for obj in object_list:
        obj_id = str(obj.get("object", "")).strip("'\"")
        if obj[property_name] == property_value or property_value == obj_id:
            return obj["object"]

    return None


def list_objects(service_instance, vim_object, properties=None):
    """
    Returns a simple list of objects from a given service instance.

    service_instance
        The Service Instance for which to obtain a list of objects.

    object_type
        The type of content for which to obtain information.

    properties
        An optional list of object properties used to return reference results.
        If not provided, defaults to ``name``.
    """
    if properties is None:
        properties = ["name"]

    items = []
    item_list = get_mors_with_properties(service_instance, vim_object, properties)
    for item in item_list:
        items.append(item["name"])
    return items


def get_service_instance_from_managed_object(mo_ref, name="<unnamed>"):
    """
    Retrieves the service instance from a managed object.

    me_ref
        Reference to a managed object (of type vim.ManagedEntity).

    name
        Name of managed object. This field is optional.
    """
    if not name:
        name = mo_ref.name
    log.trace("[%s] Retrieving service instance from managed object", name)
    si = vim.ServiceInstance("ServiceInstance")
    si._stub = mo_ref._stub
    return si


def get_properties_of_managed_object(mo_ref, properties):
    """
    Returns specific properties of a managed object, retrieved in an
    optimally.

    mo_ref
        The managed object reference.

    properties
        List of properties of the managed object to retrieve.
    """
    service_instance = get_service_instance_from_managed_object(mo_ref)
    log.trace("Retrieving name of %s", type(mo_ref).__name__)
    try:
        items = get_mors_with_properties(
            service_instance,
            type(mo_ref),
            container_ref=mo_ref,
            property_list=["name"],
            local_properties=True,
        )
        mo_name = items[0]["name"]
    except vmodl.query.InvalidProperty:
        mo_name = "<unnamed>"
    log.trace(
        "Retrieving properties '%s' of %s '%s'",
        properties,
        type(mo_ref).__name__,
        mo_name,
    )
    items = get_mors_with_properties(
        service_instance,
        type(mo_ref),
        container_ref=mo_ref,
        property_list=properties,
        local_properties=True,
    )
    if not items:
        raise salt.exceptions.VMwareApiError(
            "Properties of managed object '{}' weren't " "retrieved".format(mo_name)
        )
    return items[0]


def get_managed_object_name(mo_ref):
    """
    Returns the name of a managed object.
    If the name wasn't found, it returns None.

    mo_ref
        The managed object reference.
    """
    props = get_properties_of_managed_object(mo_ref, ["name"])
    return props.get("name")


def get_resource_pools(
    service_instance,
    resource_pool_names,
    datacenter_name=None,
    get_all_resource_pools=False,
):
    """
    Retrieves resource pool objects

    service_instance
        The service instance object to query the vCenter

    resource_pool_names
        Resource pool names

    datacenter_name
        Name of the datacenter where the resource pool is available

    get_all_resource_pools
        Boolean

    return
        Resourcepool managed object reference
    """

    properties = ["name"]
    if not resource_pool_names:
        resource_pool_names = []
    if datacenter_name:
        import saltext.vmware.utils.datacenter as utils_datacenter

        container_ref = utils_datacenter.get_datacenter(service_instance, datacenter_name)
    else:
        container_ref = get_root_folder(service_instance)

    resource_pools = get_mors_with_properties(
        service_instance,
        vim.ResourcePool,
        container_ref=container_ref,
        property_list=properties,
    )

    selected_pools = []
    for pool in resource_pools:
        if get_all_resource_pools or (pool["name"] in resource_pool_names):
            selected_pools.append(pool["object"])
    if not selected_pools:
        raise salt.exceptions.VMwareObjectRetrievalError(
            "The resource pools with properties "
            "names={} get_all={} could not be found".format(selected_pools, get_all_resource_pools)
        )

    return selected_pools


def _filter_kwargs(allowed_kwargs, default_dict=None, **kwargs):
    result = default_dict or {}
    for field in allowed_kwargs:
        val = kwargs.get(field)
        if val is not None:
            result[field] = val
    return result


def _read_paginated(func, display_name, **kwargs):
    results = []
    paginated = {"cursor": None}
    while "cursor" in paginated:
        paginated = func(**kwargs)
        if "error" in paginated:
            return paginated
        results.extend(
            result for result in paginated["results"] if result.get("display_name") == display_name
        )
        kwargs["cursor"] = paginated.get("cursor")
    return results


def wait_for_task(task, instance_name, task_type, sleep_seconds=1, log_level="debug"):
    """
    Waits for a task to be completed.

    task
        The task to wait for.

    instance_name
        The name of the ESXi host, vCenter Server, or Virtual Machine that
        the task is being run on.

    task_type
        The type of task being performed. Useful information for debugging purposes.

    sleep_seconds
        The number of seconds to wait before querying the task again.
        Defaults to ``1`` second.

    log_level
        The level at which to log task information. Default is ``debug``,
        but ``info`` is also supported.
    """
    time_counter = 0
    start_time = time.time()
    log.trace("task = %s, task_type = %s", task, task.__class__.__name__)
    try:
        task_info = task.info
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.FileNotFound as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareFileNotFoundError(exc.msg)
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    while task_info.state == "running" or task_info.state == "queued":
        if time_counter % sleep_seconds == 0:
            msg = "[ {} ] Waiting for {} task to finish [{} s]".format(
                instance_name, task_type, time_counter
            )
            if log_level == "info":
                log.info(msg)
            else:
                log.debug(msg)
        time.sleep(1.0 - ((time.time() - start_time) % 1.0))
        time_counter += 1
        try:
            task_info = task.info
        except vim.fault.NoPermission as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareApiError(
                "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
            )
        except vim.fault.FileNotFound as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareFileNotFoundError(exc.msg)
        except vim.fault.VimFault as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareApiError(exc.msg)
        except vmodl.RuntimeFault as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareRuntimeError(exc.msg)
    if task_info.state == "success":
        msg = "[ {} ] Successfully completed {} task in {} seconds".format(
            instance_name, task_type, time_counter
        )
        if log_level == "info":
            log.info(msg)
        else:
            log.debug(msg)
        # task is in a successful state
        return task_info.result
    else:
        # task is in an error state
        try:
            raise task_info.error
        except vim.fault.NoPermission as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareApiError(
                "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
            )
        except vim.fault.FileNotFound as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareFileNotFoundError(exc.msg)
        except vim.fault.VimFault as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareApiError(exc.msg)
        except vmodl.fault.SystemError as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareSystemError(exc.msg)
        except vmodl.fault.InvalidArgument as exc:
            log.exception(exc)
            exc_message = exc.msg
            if exc.faultMessage:
                exc_message = "{} ({})".format(exc_message, exc.faultMessage[0].message)
            raise salt.exceptions.VMwareApiError(exc_message)


def get_parent_type(node, parent_type):
    """
    Return a parent of specified type from a node.

    node
        Object reference to start at.

    parent_type
        The vim type of the parent you are searching for.
    """
    if isinstance(node, parent_type):
        return node
    try:
        node = node.parent
    except AttributeError:
        return None
    return get_parent_type(node, parent_type)


def get_path(node, service_instance, path=""):
    """
    Return a path to root from a node.

    node
        Object reference to start at.

    service_instance
        The Service Instance from which to obtain managed object references.

    path
        Path to node, recursively passed.
    """
    if node == service_instance.content.rootFolder:
        return path
    try:
        path = "/" + node.name + path
        node = node.parent
    except AttributeError:
        return path
    return get_path(node, service_instance, path)


def get_datacenters(service_instance, datacenter_names=None, get_all_datacenters=False):
    """
    Returns all datacenters in a vCenter.

    service_instance
        The Service Instance Object from which to obtain cluster.

    datacenter_names
        List of datacenter names to filter by. Default value is None.

    get_all_datacenters
        Flag specifying whether to retrieve all datacenters.
        Default value is None.
    """
    items = [
        i["object"]
        for i in get_mors_with_properties(service_instance, vim.Datacenter, property_list=["name"])
        if get_all_datacenters or (datacenter_names and i["name"] in datacenter_names)
    ]
    return items


def get_datacenter(service_instance, datacenter_name):
    """
    Returns a vim.Datacenter managed object.

    service_instance
        The Service Instance Object from which to obtain datacenter.

    datacenter_name
        The datacenter name
    """
    items = get_datacenters(service_instance, datacenter_names=[datacenter_name])
    if not items:
        raise salt.exceptions.VMwareObjectRetrievalError(
            "Datacenter '{}' was not found".format(datacenter_name)
        )
    return items[0]


def list_datacenters(service_instance):
    """
    Returns a list of datacenters associated with a given service instance.

    service_instance
        The Service Instance Object from which to obtain datacenters.
    """
    return list_objects(service_instance, vim.Datacenter)


def create_datacenter(service_instance, datacenter_name):
    """
    Creates a datacenter.

    .. versionadded:: 2017.7.0

    service_instance
        The Service Instance Object

    datacenter_name
        The datacenter name
    """
    root_folder = get_root_folder(service_instance)
    log.trace("Creating datacenter '%s'", datacenter_name)
    try:
        dc_obj = root_folder.CreateDatacenter(datacenter_name)
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
    return dc_obj


def delete_datacenter(service_instance, datacenter_name):
    """
    Deletes a datacenter.

    service_instance
        The Service Instance Object

    datacenter_name
        The datacenter name
    """
    root_folder = get_root_folder(service_instance)
    log.trace("Deleting datacenter '%s'", datacenter_name)
    try:
        dc_obj = get_datacenter(service_instance, datacenter_name)
        task = dc_obj.Destroy_Task()
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
    wait_for_task(task, datacenter_name, "DeleteDatacenterTask")


def get_parent_of_type(mors, type):
    """
    Finds the first parent of a managed object that matches the type specified.

    `None` is returned if no object is found.
    """
    while True:
        if isinstance(mors, type):
            return mors
        try:
            mors = mors.parent
        except AttributeError:
            return None


def find_filtered_object(service_instance, datacenter_name=None, cluster_name=None, host_name=None):
    """
    Finds zero or one matching objects: plug in almost any combination of datacenter, cluster, and/or host name.

    If cluster_name is passed, datacenter_name must also be passed.

    At least one of the optional parameters must be set.

    The most specific object will be returned (if you pass host_name and datacenter_name, the host will be returned).

    service_instance
        The Service Instance Object from which to obtain cluster.

    datacenter_name
        (Optional) Datacenter name to filter by.

    cluster_name
        (Optional) Exact cluster name to filter by. If used, datacenter_name is required.

    host_name
        (Optional) Exact host name name to filter by.
    """
    try:
        if host_name:
            import saltext.vmware.utils.esxi as utils_esxi

            hosts = utils_esxi.get_hosts(
                service_instance,
                datacenter_name=datacenter_name,
                cluster_name=cluster_name,
                host_names=[host_name],
            )
            return hosts[0] if hosts else None
        elif cluster_name and datacenter_name:
            import saltext.vmware.utils.cluster as utils_cluster

            datacenter = get_datacenter(service_instance, datacenter_name)
            return utils_cluster.get_cluster(datacenter, cluster_name)
        elif datacenter_name:
            return get_datacenter(service_instance, datacenter_name=datacenter_name)
        else:
            raise salt.exceptions.ArgumentValueError(
                "find_filtered_object requires at least one of datacenter_name, host_name, or cluster_name with datacenter_name"
            )
    except salt.exceptions.VMwareObjectRetrievalError:
        return None


def get_license_mgrs(service_instance, license_mgr_names=None, get_all_license_mgrs=False):
    """
    Returns all license managers in a vCenter.

    service_instance
        The Service Instance Object from which to obtain cluster.

    license_mgr_names
        List of license manager names to filter by. Default value is None.

    get_all_license_mgrs
        Flag specifying whether to retrieve all license managers.
        Default value is None.
    """
    log.debug("started get all License Managers")
    items = [
        i["object"]
        for i in get_mors_with_properties(
            service_instance, vim.LicenseAssignmentManager, property_list=["name"]
        )
        if get_all_license_mgrs or (license_mgr_names and i["name"] in license_mgr_names)
    ]
    log.debug("exited get all License Managers")
    return items


def get_license_mgr(service_instance, license_mgr_name):
    """
    Returns a vim.LicenseAssignmentManager managed object.

    service_instance
        The Service Instance Object from which to obtain license manager.

    license_mgr_name
        The license manager name
    """
    log.debug(f"started get License Manager '{license_mgr_name}'")
    items = get_license_mgrs(service_instance, license_mgr_names=[license_mgr_name])
    if not items:
        raise salt.exceptions.VMwareObjectRetrievalError(
            f"license manager '{license_mgr_name}' was not found"
        )
    log.debug(f"exit License Manager '{license_mgr_name}'")
    return items[0]


def list_license_mgrs(service_instance):
    """
    Returns a list of license managers associated with a given service instance.

    service_instance
        The Service Instance Object from which to obtain license managers.
    """
    log.debug("start list of License Managers")
    return list_objects(service_instance, vim.LicenseAssignmentManager)


def deployment_resources(host_name, service_instance):
    """
    Returns the dict representation of deployment resources from given host name.

    host_name
        The name of the esxi host to obtain esxi reference.

    """
    destination_host_ref = get_mor_by_property(
        service_instance,
        vim.HostSystem,
        host_name,
    )
    datacenter_ref = get_parent_type(destination_host_ref, vim.Datacenter)
    cluster_ref = get_parent_type(destination_host_ref, vim.ClusterComputeResource)
    resource_pool = cluster_ref.resourcePool

    return {
        "destination_host": destination_host_ref,
        "datacenter": datacenter_ref,
        "cluster": cluster_ref,
        "resource_pool": resource_pool,
    }
