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


def absent(license_key):
    """
    Remove a license

    license
        License Key to remove form license manager

    .. code-block:: yaml

    Remove license from License Manager:
      vmware_license_mgr.absent:
        - license: license_key

    """
    ret = __salt__["vmware_license_mgr.remove"](license_key)
    return ret


def present(license_key):
    """
    Remove a license

    license
        License Key to add to license manager


    .. code-block:: yaml

    Remove license from License Manager:
      vmware_license_mgr.present:
        - license: license_key
    """
    ret = __salt__["vmware_license_mgr.add"](license_key)
    return ret
