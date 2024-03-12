# Copyright 2021 VMware, Inc.
# SPDX-License: Apache-2.0
import logging

import salt.exceptions
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.connect as connect
import saltext.vmware.utils.datacenter as utils_datacenter
import saltext.vmware.utils.vsphere as utils_vmware

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_folder"
__func_alias__ = {"list_": "list"}


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def create(folder_name, dc_name, type, service_instance=None, profile=None):
    """
    Creates a folder on a given datacenter.

    folder_name
        Name of folder.

    dc_name
        Name of datacenter where folder will be created.

    type
        (vm, host, datastore, network) Type of folder to be created.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    dc_ref = utils_datacenter.get_datacenter(service_instance, dc_name)
    folder = utils_common.get_mor_by_property(
        service_instance, vim.Folder, folder_name, "name", dc_ref
    )
    if type == "vm":
        dc_ref.vmFolder.CreateFolder(folder_name)
    elif type == "host":
        dc_ref.hostFolder.CreateFolder(folder_name)
    elif type == "datastore":
        dc_ref.datastoreFolder.CreateFolder(folder_name)
    elif type == "network":
        dc_ref.networkFolder.CreateFolder(folder_name)
    else:
        raise salt.exceptions.CommandExecutionError("invalid type")
    return {"status": "created"}


def destroy(folder_name, dc_name, type, service_instance=None, profile=None):
    """
    Destroy a folder on a given datacenter.

    folder_name
        Name of folder.

    dc_name
        Name of datacenter where folder will be Destroyed.

    type
        (vm, host, datastore, network) Type of folder to be destroyed.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    dc_ref = utils_datacenter.get_datacenter(service_instance, dc_name)
    if type == "vm":
        folder = utils_common.get_mor_by_property(
            service_instance, vim.Folder, folder_name, "name", dc_ref.vmFolder
        )
    elif type == "host":
        folder = utils_common.get_mor_by_property(
            service_instance, vim.Folder, folder_name, "name", dc_ref.hostFolder
        )
    elif type == "datastore":
        folder = utils_common.get_mor_by_property(
            service_instance, vim.Folder, folder_name, "name", dc_ref.datastoreFolder
        )
    elif type == "network":
        folder = utils_common.get_mor_by_property(
            service_instance, vim.Folder, folder_name, "name", dc_ref.networkFolder
        )
    else:
        raise salt.exceptions.CommandExecutionError("invalid type")
    folder.Destroy_Task()
    return {"status": "destroyed"}


def rename(folder_name, new_folder_name, dc_name, type, service_instance=None, profile=None):
    """
    Rename a folder on a given datacenter.

    folder_name
        Name of folder.

    new_folder_name
        Name to rename folder.

    dc_name
        Name of datacenter where folder will be renamed.

    type
        (vm, host, datastore, network) Type of folder to be renamed.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    dc_ref = utils_datacenter.get_datacenter(service_instance, dc_name)
    if type == "vm":
        folder = utils_common.get_mor_by_property(
            service_instance, vim.Folder, folder_name, "name", dc_ref.vmFolder
        )
    elif type == "host":
        folder = utils_common.get_mor_by_property(
            service_instance, vim.Folder, folder_name, "name", dc_ref.hostFolder
        )
    elif type == "datastore":
        folder = utils_common.get_mor_by_property(
            service_instance, vim.Folder, folder_name, "name", dc_ref.datastoreFolder
        )
    elif type == "network":
        folder = utils_common.get_mor_by_property(
            service_instance, vim.Folder, folder_name, "name", dc_ref.networkFolder
        )
    else:
        raise salt.exceptions.CommandExecutionError("invalid type")
    folder.Rename_Task(new_folder_name)
    return {"status": "renamed"}


def move(folder_name, destination_folder_name, dc_name, type, service_instance=None, profile=None):
    """
    Move a folder on a given datacenter.

    folder_name
        Name of folder.

    destination_folder_name
        Destination folder for named folder.

    dc_name
        Name of datacenter where folder will be moved.

    type
        (vm, host, datastore, network) Type of folder to be moved.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    dc_ref = utils_datacenter.get_datacenter(service_instance, dc_name)
    if type == "vm":
        folder = utils_common.get_mor_by_property(
            service_instance, vim.Folder, folder_name, "name", dc_ref.vmFolder
        )
        destination = utils_common.get_mor_by_property(
            service_instance, vim.Folder, destination_folder_name, "name", dc_ref.vmFolder
        )
    elif type == "host":
        folder = utils_common.get_mor_by_property(
            service_instance, vim.Folder, folder_name, "name", dc_ref.hostFolder
        )
        destination = utils_common.get_mor_by_property(
            service_instance, vim.Folder, destination_folder_name, "name", dc_ref.hostFolder
        )
    elif type == "datastore":
        folder = utils_common.get_mor_by_property(
            service_instance, vim.Folder, folder_name, "name", dc_ref.datastoreFolder
        )
        destination = utils_common.get_mor_by_property(
            service_instance, vim.Folder, destination_folder_name, "name", dc_ref.datastoreFolder
        )
    elif type == "network":
        folder = utils_common.get_mor_by_property(
            service_instance, vim.Folder, folder_name, "name", dc_ref.networkFolder
        )
        destination = utils_common.get_mor_by_property(
            service_instance, vim.Folder, destination_folder_name, "name", dc_ref.networkFolder
        )
    else:
        raise salt.exceptions.CommandExecutionError("invalid type")
    task = destination.MoveIntoFolder_Task([folder])
    utils_common.wait_for_task(task, folder.name, "move folder")
    return {"status": "moved"}


def list_(service_instance=None, profile=None):
    """
    .. versionadded:: 23.6.29.0rc1

    Returns a list of folders.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    return utils_vmware.list_folders(service_instance)
