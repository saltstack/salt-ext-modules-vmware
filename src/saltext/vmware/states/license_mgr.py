# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging


log = logging.getLogger(__name__)

try:
    import pyVmomi

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_license_mgr"
__proxyenabled__ = ["vmware_license_mgr"]


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


## DGM Don't believe you can create a License Manager - Check TBD


def present(name):
    """
    Create a license manager

    .. code-block:: yaml

    Create license manager:
      vmware_license_mgr.present:
        - name: licmgr1

    """
    ret = {"name": name, "result": None, "comment": "", "changes": {}}
    licmgrs = __salt__["vmware_license_mgr.list"]()
    if name in licmgrs:
        ret["comment"] = "license manager {} is already present. No changes made.".format(name)
        ret["result"] = True
    else:
        ret["comment"] = "license manager {} not found.".format(name)
        ret["result"] = False
    return ret


## def present(name):
##     """
##     Create a license manager
##
##     .. code-block:: yaml
##
##     Create license manager:
##       vmware_license_mgr.present:
##         - name: dc1
##
##     """
##     ret = {"name": name, "result": None, "comment": "", "changes": {}}
##     dcs = __salt__["vmware_license_mgr.list"]()
##     if name in dcs:
##         ret["comment"] = "license manager {} is already present. No changes made.".format(name)
##         ret["result"] = True
##     elif __opts__["test"]:
##         ret["comment"] = "license manager {} will be created.".format(name)
##         ret["result"] = None
##     else:
##         dc = __salt__["vmware_license_mgr.create"](name)
##         if isinstance(dc, dict) and dc.get(name) is not False:
##             ret["comment"] = "license manager - {} created.".format(name)
##             ret["changes"] = dc
##             ret["result"] = True
##
##         else:
##             ret["comment"] = dc["reason"]
##             ret["result"] = False
##     return ret


## DGM don't believe you can delete a License Manager - Check TBD
## def absent(name):
##     """
##     Delete a license manager.
##
##     .. code-block:: yaml
##
##     Delete license manager:
##       vmware_license_mgr.absent:
##         - name: dc1
##     """
##     ret = {"name": name, "result": None, "comment": "", "changes": {}}
##     dcs = __salt__["vmware_license_mgr.list"]()
##     if name not in dcs:
##         ret["comment"] = "license manager {} does not exist. No changes made.".format(name)
##         ret["result"] = True
##     elif __opts__["test"]:
##         ret["comment"] = "license manager {} will be deleted.".format(name)
##         ret["result"] = None
##     else:
##         dc = __salt__["vmware_license_mgr.delete"](name)
##         if isinstance(dc, dict) and dc.get(name) is not False:
##             ret["comment"] = "license manager - {} deleted.".format(name)
##             ret["changes"] = dc
##             ret["result"] = True
##
##         else:
##             ret["comment"] = dc["reason"]
##             ret["result"] = False
##     return ret
