# SPDX-License-Identifier: Apache-2.0
import logging

import saltext.vmware.modules.folder as m_folder
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.connect as connect

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_folder"
__proxyenabled__ = ["vmware_folder"]


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def manage(name, task, dc_name, type, service_instance=None, profile=None):
    """
    Creates or destroy a folder on a given datacenter.

    name
        Name of folder.

    task
        create or destroy

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
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}
    task_string = "created" if (task == "create") else "destroyed"

    if __opts__["test"]:
        ret["changes"] = {"new": f"folder {name} will be {task_string}"}
        ret["comment"] = "These options are set to change."
        return ret

    if task == "create":
        result = m_folder.create(name, dc_name, type, service_instance)
        ret["changes"] = {"new": f"folder {name} {task_string}"}
    elif task == "destroy":
        result = m_folder.destroy(name, dc_name, type, service_instance)
        ret["changes"] = {"new": f"folder {name} {task_string}"}
    else:
        ret["comment"] = "invalid task"
        ret["result"] = False
        return ret

    ret["comment"] = result["status"]
    return ret


def rename(name, new_folder_name, dc_name, type, service_instance=None, profile=None):
    """
    Rename a folder on a given datacenter.

    name
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
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}

    if __opts__["test"]:
        ret["changes"] = {"new": f"folder {name} will be renamed {new_folder_name}"}
        ret["comment"] = "These options are set to change."
        return ret

    result = m_folder.rename(name, new_folder_name, dc_name, type, service_instance)
    ret["changes"] = {"new": f"folder {name} renamed {new_folder_name}"}
    ret["comment"] = result["status"]
    return ret


def move(name, destination_folder_name, dc_name, type, service_instance=None, profile=None):
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
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}

    if __opts__["test"]:
        ret["changes"] = {"new": f"folder {name} will be moved to {destination_folder_name}"}
        ret["comment"] = "These options are set to change."
        return ret

    result = m_folder.move(name, destination_folder_name, dc_name, type, service_instance)
    ret["changes"] = {"new": f"folder {name} moved to {destination_folder_name}"}
    ret["comment"] = result["status"]
    return ret
