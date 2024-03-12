# SPDX-License-Identifier: Apache-2.0
import logging

import saltext.vmware.utils.connect as connect
import saltext.vmware.utils.datastore as utils_datastore

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_datastore"
__proxyenabled__ = ["vmware_datastore"]


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def maintenance_mode(
    name, enter_maintenance_mode, datacenter_name=None, service_instance=None, profile=None
):
    """
    Manage boot option for a virtual machine

    name
        The name of the datastore.

    enter_maintenance_mode
        (Bool) True to put datastore in maintenance mode, False to exit maintenance mode.

    datacenter_name
        The name of the datacenter containing the datastore.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}
    assert isinstance(name, str)
    datastores = utils_datastore.get_datastores(
        service_instance, datastore_name=name, datacenter_name=datacenter_name
    )
    ds = datastores[0] if datastores else None
    status = ds.summary.maintenanceMode
    if enter_maintenance_mode:
        if status == "inMaintenance":
            ret["comment"] = "Already in maintenance mode."
            return ret

        if __opts__["test"]:
            ret["result"] = None
            ret["changes"] = {"new": f"datastore {name} will enter maintenance mode."}
            ret["comment"] = "These options are set to change."
            return ret

        mode = utils_datastore.enter_maintenance_mode(ds)
        if mode:
            ret["changes"] = {"new": f"datastore {name} is in maintenance mode."}
            ret["comment"] = "These options changed."
            return ret
        ret["comment"] = f"Failed to put datastore {name} in maintenance mode."
        ret["result"] = False
        return ret
    else:
        if status == "normal":
            ret["comment"] = "Already exited maintenance mode."
            return ret

        if __opts__["test"]:
            ret["result"] = None
            ret["changes"] = {"new": f"datastore {name} will exit maintenance mode."}
            ret["comment"] = "These options are set to change."
            return ret

        mode = utils_datastore.exit_maintenance_mode(ds)
        if mode:
            ret["changes"] = {"new": f"datastore {name} exited maintenance mode."}
            ret["comment"] = "These options changed."
            return ret
        ret["comment"] = f"datastore {name} failed to exit maintenance mode."
        ret["result"] = False
        return ret
