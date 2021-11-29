# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# pylint: disable=no-name-in-module
import logging

import salt.exceptions
import salt.modules.cmdmod
import salt.utils.path
import salt.utils.platform
import salt.utils.stringutils
import saltext.vmware.utils.cluster as utils_cluster
import saltext.vmware.utils.datacenter as utils_datacenter
import saltext.vmware.utils.esxi as utils_esxi
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


def add_license(
    service_instance, license, datacenter_name=None, cluster_name=None, esxi_hostname=None
):
    """
    Add license to the pool of available licenses associated with the License Manager
    and assign it to the specified Cluster, ESXI Server or vCenter

    If no datacenter, cluster or ESXI Server is specified, it is assumed the operation is to be applied to a vCenter

    service_instance:
        Service Instance containing a License Manager

    license
        License to add to license manager

    datacenter_name
        Datacenter name to use for the operation [default None]

    cluster_name
        Name of the cluster to add license [default None]

    esxi_hostname
        Hostname of the ESXI Server to add license [default None]

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
        datacenter_ref = None
        if datacenter_name:
            # need to get named datacenter's reference
            datacenter_ref = utils_datacenter.get_datacenter(service_instance, datacenter_name)
            log.debug(
                f"retrieved datacenter ref '{datacenter_ref }' for datacenter '{datacenter_name}'"
            )

        if cluster_name:
            # need to get named cluster's reference
            cluster_ref = utils_cluster.get_cluster(dc_ref=datacenter_ref, cluster=cluster_name)
            entityId = cluster_ref._moId
            log.debug(
                f"retrieved entityId '{entityId}' from cluster ref '{cluster_ref }' for cluster '{cluster_name}' and datacenter '{datacenter_name}'"
            )
        elif esxi_hostname:
            # need to get named esxi server
            esxi_hosts = utils_esxi.get_hosts(service_instance, None, esxi_hostname)

            # returns hosts list of dicts
            if not esxi_hosts:
                log.debug(f"Failed to find esxi hostname '{esxi_hostname}'")
                return False

            if len(esxi_hosts) > 1:
                log.error(
                    f"Failed, found multiple instances of esxi hostname '{esxi_hostname}', hosts returned '{esxi_hosts}'"
                )
                return False

            entityID = esxi_hosts[0]["object"]._moId
            if "esx" not in license.editionKey:
                log.error(
                    f"Error, License '{license}' does not contain a suitable Edition key '{license.editionKey}' for an ESXi Server"
                )
                return False
        else:
            # default to applying to vCenter
            srv_content = get_service_content(service_instance)
            entity_id = srv_content.about.instanceUuid

        lic_assign_mgr = get_license_assignment_mgr(service_instance)
        if entity_id:
            assigned_lic = lic_assign_mgr.QueryAssignedLicenses(entityId=entity_id)

            log.debug(
                f"assigning license, entity identifier '{entity_id}' has assigned license '{assigned_lic}'"
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


def remove_license(
    service_instance, license, datacenter_name=None, cluster_name=None, esxi_hostname=None
):
    """
    Remove license from the pool of available licenses associated with the License Manager
    and unassign it from the specified Cluster, ESXI Server or vCenter

    If no datacenter, cluster or ESXI Server is specified, it is assumed the operation is to be applied to a vCenter

    service_instance:
        Service Instance containing a License Manager

    license
        License to remove from the license manager

    datacenter_name
        Datacenter name to use for the operation [default None]

    cluster_name
        Name of the cluster to add license [default None]

    esxi_hostname
        Hostname of the ESXI Server to add license [default None]

    Returns:
        True - if successful, license removed
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

    # TBD need to determine if can 'RemoveAssignedLicense' or if simple
    # 'RemoveLicense' will unassign any assigned licenses when the license
    # is removed
    try:
        lic_mgr.RemoveLicense(licenseKey=license)
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)

    return True
