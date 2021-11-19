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


def list_(service_instance=None):
    """
    Returns a list of license managers for the specified host.

    .. code-block:: bash

        salt '*' vmware_license_mgr.list
    """
    pu.db

    log.debug("DGM vmware ext license_mgr list entered")
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    log.debug("DGM vmware ext license_mgr list retrieved service_instance")
    return utils_license_mgr.list_license_mgrs(service_instance)


## def create(name, service_instance=None):
##     """
##     Creates a datacenter.
##
##     Supported proxies: esxdatacenter
##
##     name
##         The datacenter name
##
##     .. code-block:: bash
##
##         salt '*' vmware_datacenter.create dc1
##     """
##     if service_instance is None:
##         service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
##     try:
##         utils_datacenter.create_datacenter(service_instance, name)
##     except salt.exceptions.VMwareApiError as exc:
##         return {name: False, "reason": str(exc)}
##     return {name: True}


def get_(name, service_instance=None):
    """
    Get the properties of a License Manager

    name
        The vcenter name

    .. code-block:: bash

        salt '*' vmware_license_mgr.get dc1
    """
    log.debug(f"DGM vmware ext license_mgr get entered, with name '{name}'")
    ret = {}
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    try:
        licmgr_ref = utils_lic_mgr.get_license_mgr(service_instance, name)
        licmgr = utils_common.get_mors_with_properties(
            service_instance,
            vim.LicenseAssignmentManager,
            container_ref=vc_ref,
            local_properties=True,
        )
        if licmgr:
            ret = licmgr[0]
    except (salt.exceptions.VMwareApiError, salt.exceptions.VMwareObjectRetrievalError) as exc:
        return {name: False, "reason": str(exc)}
    return ret


## def delete(name, service_instance=None):
##     """
##     Deletes a datacenter.
##
##     Supported proxies: esxdatacenter
##
##     name
##         The datacenter name
##
##     .. code-block:: bash
##
##         salt '*' vmware_datacenter.delete dc1
##     """
##     if service_instance is None:
##         service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
##     try:
##         utils_datacenter.delete_datacenter(service_instance, name)
##     except (salt.exceptions.VMwareApiError, salt.exceptions.VMwareObjectRetrievalError) as exc:
##         return {name: False, "reason": str(exc)}
##     return {name: True}
