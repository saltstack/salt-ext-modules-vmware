# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging


log = logging.getLogger(__name__)

try:
    import pyVmomi

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_datacenter"
__proxyenabled__ = ["vmware_datacenter"]


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def present(name):
    """
    Create a datacenter

    .. code-block:: yaml

        Create Datacenter:
          vmware_datacenter.present:
            - name: dc1
    """
    ret = {"name": name, "result": None, "comment": "", "changes": {}}
    dcs = __salt__["vmware_datacenter.list"]()
    if name in dcs:
        ret["comment"] = "Datacenter {} is already present. No changes made.".format(name)
        ret["result"] = True
    elif __opts__["test"]:
        ret["comment"] = "Datacenter {} will be created.".format(name)
        ret["result"] = None
    else:
        dc = __salt__["vmware_datacenter.create"](name)
        if isinstance(dc, dict) and dc.get(name) is not False:
            ret["comment"] = "Datacenter - {} created.".format(name)
            ret["changes"] = dc
            ret["result"] = True

        else:
            ret["comment"] = dc["reason"]
            ret["result"] = False
    return ret


def absent(name):
    """
    Delete a datacenter.

    .. code-block:: yaml

        Delete Datacenter:
          vmware_datacenter.absent:
            - name: dc1
    """
    ret = {"name": name, "result": None, "comment": "", "changes": {}}
    dcs = __salt__["vmware_datacenter.list"]()
    if name not in dcs:
        ret["comment"] = "Datacenter {} does not exist. No changes made.".format(name)
        ret["result"] = True
    elif __opts__["test"]:
        ret["comment"] = "Datacenter {} will be deleted.".format(name)
        ret["result"] = None
    else:
        dc = __salt__["vmware_datacenter.delete"](name)
        if isinstance(dc, dict) and dc.get(name) is not False:
            ret["comment"] = "Datacenter - {} deleted.".format(name)
            ret["changes"] = dc
            ret["result"] = True

        else:
            ret["comment"] = dc["reason"]
            ret["result"] = False
    return ret
