# SPDX-License-Identifier: Apache-2.0
# pylint: disable=no-name-in-module
import logging

import saltext.vmware.utils.common as utils_common

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

log = logging.getLogger(__name__)


def list_datacenters(service_instance):
    """
    Returns a list of datacenters associated with a given service instance.

    service_instance
        The Service Instance Object from which to obtain datacenters.
    """
    return utils_common.list_objects(service_instance, vim.Datacenter)


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
        for i in utils_common.get_mors_with_properties(service_instance, vim.Datacenter, property_list=["name"])
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


def create_datacenter(service_instance, datacenter_name):
    """
    Creates a datacenter.

    .. versionadded:: 2017.7.0

    service_instance
        The Service Instance Object

    datacenter_name
        The datacenter name
    """
    root_folder = utils_common.get_root_folder(service_instance)
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
    root_folder = utils_common.get_root_folder(service_instance)
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
    utils_common.wait_for_task(task, datacenter_name, "DeleteDatacenterTask")


def get_vm_datacenter(*, vm):
    """
    Return a datacenter from vm
    """
    datacenter = None
    while True:
        if isinstance(vm, vim.Datacenter):
            datacenter = vm
            break
        try:
            vm = vm.parent
        except AttributeError:
            break
    return datacenter
