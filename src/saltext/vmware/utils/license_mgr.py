# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# pylint: disable=no-name-in-module
import logging

import salt.exceptions
import salt.modules.cmdmod
import salt.utils.path
import salt.utils.platform
import salt.utils.stringutils
from saltext.vmware.utils.common import get_service_content as get_service_content

try:
    from pyVmomi import vim, vmodl

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False

log = logging.getLogger(__name__)


def _list_lic_keys(licenses):
    """
    Return a list of license keys

    licenses:
       vCenter licenses as made available from licenseAssignmentManager

    Note:
        skips evaluation licenses
    """
    log.debug("started _list_lic_keys")
    lic_keys = []
    for lic in licenses:
        if lic.used is None:
            continue
        lic_keys.append(lic.licenseKey)
    return lic_keys


def is_vcenter(service_instance):
    """
    Test if service_instance represents vCenter,
    otherwise assume represents an ESXi server

    service_instance
        The Service Instance to check if it represents a vCenter

    Return:
        True  - vCenter
        False - ESXi server
        None - neither of the above
    """
    try:
        srv_content = get_service_content(service_instance)
        apitype = srv_content.about.apiType
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)

    if apitype == "VirtualCenter":
        return True
    elif apitype == "HostAgent":
        return False

    return None


def get_license_mgr(service_instance):
    """
    Return a license manager from specified Service Instance

    Note: returns LicenseManager
    """
    lic_mgr = None

    if not is_vcenter(service_instance):
        return lic_mgr

    srv_content = get_service_content(service_instance)
    lic_mgr = srv_content.licenseManager
    return lic_mgr


def get_license_assignment_mgr(service_instance):
    """
    Return a license assignment manager from specified Service Instance

    Note: returns LicenseAssignmentManager
    """
    lic_mgr = None

    if not is_vcenter(service_instance):
        return lic_mgr

    srv_content = get_service_content(service_instance)
    lic_mgr = srv_content.licenseManager.licenseAssignmentManager
    return lic_mgr


def list_licenses(service_instance):
    """
    Returns a list of licenses associated with specified Service Instance.

    service_instance
        The Service Instance Object from which to obtain licenses.
    """
    log.debug("start list of License Managers")

    ret = {}
    lic_mgr = get_license_mgr(service_instance)
    log.debug(f"listing licenses from License Manager '{lic_mgr}'")
    if not lic_mgr:
        ret["comment"] = "Failed, not connected to a vCenter"
        ret["result"] = False
        return ret

    ret["licenses"] = _list_lic_keys(lic_mgr.licenses)
    return ret


def add_license(service_instance, license):
    """
    Add a license to the License Manager associated with the specified Service Instance
    Adds the license to the pool of available licenses associated with the License Manager

    service_instance:
        Service Instance containing a License Manager

    license
        License to add to the license manager

    Returns:
        True - if successful or license already present
    """
    lic_mgr = get_license_mgr(service_instance)
    if not lic_mgr:
        return False

    lic_keys = _list_lic_keys(lic_mgr.licenses)
    log.debug(
        f"attempting to add license '{license}' to list of existing license keys '{lic_keys}'"
    )

    try:
        if not license in lic_keys:
            lic_mgr.AddLicense(licenseKey=license)

        # need to extract entity this license is intended for so that it can be assigned.
        # choices are:
        #   1 vCenter - entity_id = service_instance.content.about.instanceUuid
        #   2 ESXi - entity_id = esxi host _moId, need to check it is for an 'esx' license.editionKey
        #   3 cluster - entity_id = cluster _moId

        entity_id = None  # TBD miracle happens here and have value

        # TBD do vCenter for now
        srv_content = get_service_content(service_instance)
        entity_id = srv_content.about.instanceUuid
        lic_assign_mgr = get_license_assignment_mgr(service_instance)
        if entity_id:
            assigned_lic = lic_assign_mgr.QueryAssignedLicenses(entityId=entity_id)

            log.debug(
                "assigning license, entity identifier '{entity_id}' has assigned license '{assigned_lic}'"
            )
            if not assigned_lic or (
                len(assigned_lic) != 0 and assigned_lic[0].assignedLicense.licenseKey != license
            ):
                lic_assign_mgr.UpdateAssignedLicense(entity=entity_id, licenseKey=license)

    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)

    return True


def remove_license(service_instance, license):
    """
    Remove specified license from the License Manager associated with the specified Service Instance
    Removes the license from the pool of available licenses associated with the License Manager

    service_instance:
        Service Instance containing a License Manager

    license
        License to remove from the license manager

    Returns:
        True - if successful or license already present
    """
    lic_mgr = get_license_mgr(service_instance)
    if not lic_mgr:
        return False

    lic_keys = _list_lic_keys(lic_mgr.licenses)
    log.debug(
        f"attempting to remove license '{license}' from list of existing license keys '{lic_keys}'"
    )
    if license not in lic_keys:
        return False

    try:
        lic_mgr.RemoveLicense(licenseKey=license)
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)

    return True
