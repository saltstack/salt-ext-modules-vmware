# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import pudb
import salt.exceptions
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.license_mgr as utils_license_mgr
from saltext.vmware.utils.connect import get_service_instance

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_license_mgr"
__proxyenabled__ = ["vmware_license_mgr"]
__func_alias__ = {"list_": "list", "get_": "get"}


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def add(license, service_instance=None):
    """
    Add a license manager

    Supported proxies: esxi host

    license:
        License to remove from license manager

    .. code-block: bash

        salt '*' vmware_license_mgr.add license
    """
    log.debug("DGM vmware ext license_mgr add lic entered")
    ret = {}
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    log.debug("DGM vmware ext license_mgr add lic retrieved service_instance")

    if not utils_license_mgr.is_vcenter(service_instance):
        ret["comment"] = "Failed, not connected to a vCenter"
        ret["result"] = False
        return ret

    try:
        result = utils_license_mgr.add_license(service_instance, license)
    except (
        salt.exceptions.VMwareApiError,
        salt.exceptions.VMwareObjectRetrievalError,
        salt.exceptions.VMwareRuntimeError,
    ) as exc:
        ret["comment"] = f"Failed to remove a license due to Exception '{str(exc)}'"
        ret["result"] = False
        return ret

    if not result:
        ret["comment"] = f"Failed specified license was not added to License Manager"
        ret["result"] = False

    return ret


def get_(service_instance=None):
    """
    Get the properties of a License Manager

    name
        The vcenter name

    .. code-block:: bash

        salt '*' vmware_license_mgr.get
    """
    ret = {}
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    try:
        licmgr_ref = utils_lic_mgr.get_license_mgr(service_instance)
        licmgr = utils_common.get_mors_with_properties(
            service_instance,
            vim.LicenseManager,
            container_ref=vc_ref,
            local_properties=True,
        )
        if licmgr:
            ret = licmgr[0]
    except (salt.exceptions.VMwareApiError, salt.exceptions.VMwareObjectRetrievalError) as exc:
        return {name: False, "reason": str(exc)}
    return ret


def list_(service_instance=None):
    """
    Returns a list of licenses for the specified Service Instance

    .. code-block:: bash

        salt '*' vmware_license_mgr.list
    """
    pu.db

    log.debug("DGM vmware ext license_mgr list entered")
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    log.debug("DGM vmware ext license_mgr list retrieved service_instance")
    return utils_license_mgr.list_licenses(service_instance)


def remove(license, service_instance=None):
    """
    Remove a license manager

    Supported proxies: esxi host

    license:
        License to remove from license manager

    .. code-block: bash

        salt '*' vmware_license_mgr.remove license
    """
    log.debug("DGM vmware ext license_mgr remove lic entered")
    ret = {}
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)

    log.debug("DGM vmware ext license_mgr remove lic retrieved service_instance")

    if not utils_license_mgr.is_vcenter(service_instance):
        ret["comment"] = "Failed, not connected to a vCenter"
        ret["result"] = False
        return ret

    try:
        result = utils_license_mgr.remove_license(service_instance, license)
    except (
        salt.exceptions.VMwareApiError,
        salt.exceptions.VMwareObjectRetrievalErrori,
        salt.exceptions.VMwareRuntimeError,
    ) as exc:
        ret["comment"] = f"Failed to remove a license due to Exception '{str(exc)}'"
        ret["result"] = False
        return ret

    if not result:
        ret["comment"] = f"Failed specified license was not found in License Manager"
        ret["result"] = False

    return ret
