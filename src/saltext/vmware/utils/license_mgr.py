# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# pylint: disable=no-name-in-module
import logging

# noreorder
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
       vCenter licenses as made available from licenseManager

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


def _find_lic_for_key(licenses, license_key):
    """
    Return license which matches specified license_key

    licenses:
       vCenter licenses as made available from licenseManager

    license_key
        license key to search for

    Note:
        skips evaluation licenses
    """
    log.debug("started _find_lic_for_key")
    lic_keys = []
    for lic in licenses:
        if lic.used is None:
            continue
        if license_key == lic.licenseKey:
            return lic
    return None


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
    except AttributeError as exc:
        log.exception(exc)
        raise salt.exceptions.CommandExecutionError(exc.msg)
    except TypeError as exc:
        log.exception(exc)
        raise salt.exceptions.CommandExecutionError(exc.msg)

    if apitype == "VirtualCenter":
        return True
    elif apitype == "HostAgent":
        return False

    return None


def get_license_mgr(service_instance):
    """
    Return a license manager from specified Service Instance

    service_instance
        vCenter service connection instance

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

    service_instance
        vCenter service connection instance

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
    log.debug(f"License Manager listing of licenses '{lic_mgr.licenses}'")

    if not lic_mgr:
        ret["message"] = "Failed, not connected to a vCenter"
        ret["result"] = False
        return ret

    ret["licenses"] = _list_lic_keys(lic_mgr.licenses)
    return ret


def add_license(
    service_instance, license_key, datacenter_name=None, cluster_name=None, esxi_hostname=None
):
    """
    Add license to the pool of available licenses associated with the License Manager
    and assign it to the specified Cluster, ESXI Server or vCenter

    If no datacenter, cluster or ESXI Server is specified, it is assumed the operation is to be applied to a vCenter

    service_instance:
        Service Instance containing a License Manager

    license_key
        License key which specifies license to add to license manager

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
        f"attempting to add license key '{license_key}' to list of existing license keys '{lic_keys}'"
    )

    try:
        if not license_key in lic_keys:
            licMgrLicInfo = lic_mgr.AddLicense(licenseKey=license_key)
            log.debug(f"attempted AddLicense, returned license into '{licMgrLicInfo}'")
            props_list = []
            for prop in licMgrLicInfo.properties:
                props_list.append({prop.key: prop.value})

            # check for failure to add license
            license_add_failure = False
            license_add_failure_msg = ""
            for prop_dict in props_list:
                if "lc_error" in prop_dict:
                    log.error(f"Failed AddLicense for license key '{license_key}'")
                    license_add_failure = True
                if "diagnostic" in prop_dict:
                    license_add_failure_msg = prop_dict["diagnostic"]
            if license_add_failure:
                log.error(
                    f"Failed to add license key '{license_key}', reason '{license_add_failure_msg}'"
                )
                raise salt.exceptions.CommandExecutionError(license_add_failure_msg)

        # get license just added for specified license key
        addedLic = _find_lic_for_key(lic_mgr.licenses, license_key)
        if not addedLic:
            log.error(f"Unable to find license for recently added license_key '{license_key}'")
            return False

        # need to extract entity this license is intended for so that it can be assigned.
        # choices are:
        #   1 vCenter - entity_id = service_instance.content.about.instanceUuid
        #   2 ESXi - entity_id = esxi host _moId, need to check it is for an 'esx' license.editionKey
        #   3 cluster - entity_id = cluster _moId

        entity_id = None  # TBD miracle happens here and have value
        datacenter_ref = None
        if datacenter_name or cluster_name or esxi_hostname:
            if datacenter_name:
                # need to get named datacenter's reference
                datacenter_ref = utils_datacenter.get_datacenter(service_instance, datacenter_name)
                log.debug(
                    f"retrieved datacenter ref '{datacenter_ref }' for datacenter '{datacenter_name}'"
                )

            if cluster_name:
                # need to get named cluster's reference
                cluster_ref = utils_cluster.get_cluster(dc_ref=datacenter_ref, cluster=cluster_name)
                entity_id = cluster_ref._moId
                log.debug(
                    f"retrieved entityId '{entity_id}' from cluster ref '{cluster_ref }' for cluster '{cluster_name}' and datacenter '{datacenter_name}'"
                )

            if esxi_hostname:
                # need to get named esxi server
                esxi_hosts = utils_esxi.get_hosts(service_instance, datacenter_name, esxi_hostname)

                # returns hosts list of dicts
                if not esxi_hosts:
                    log.debug(f"Failed to find esxi hostname '{esxi_hostname}'")
                    return False

                if len(esxi_hosts) > 1:
                    log.error(
                        f"Failed, found multiple instances of esxi hostname '{esxi_hostname}', hosts returned '{esxi_hosts}'"
                    )
                    return False

                entity_id = esxi_hosts[0]._moId
                if "esx" not in addedLic.editionKey:
                    log.error(
                        f"Error, License '{license_key}' does not contain a suitable Edition key '{license.editionKey}' for an ESXi Server"
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
                len(assigned_lic) != 0 and assigned_lic[0].assignedLicense.licenseKey != license_key
            ):
                lic_assign_mgr.UpdateAssignedLicense(entity=entity_id, licenseKey=license_key)

    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    except AttributeError as exc:
        log.exception(exc)
        raise salt.exceptions.CommandExecutionError(exc.msg)
    except TypeError as exc:
        log.exception(exc)
        raise salt.exceptions.CommandExecutionError(exc.msg)

    return True


def remove_license(
    service_instance, license_key, datacenter_name=None, cluster_name=None, esxi_hostname=None
):
    """
    Remove license from the pool of available licenses associated with the License Manager
    and unassign it from the specified Cluster, ESXI Server or vCenter

    If no datacenter, cluster or ESXI Server is specified, it is assumed the operation is to be applied to a vCenter

    service_instance:
        Service Instance containing a License Manager

    license_key
        License key which specifies license to remove from the license manager

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
        log.debug(
            f"attempting to remove license '{license_key}' but unable to find license manager"
        )
        return False

    lic_keys = _list_lic_keys(lic_mgr.licenses)
    log.debug(
        f"attempting to remove license '{license_key}' from list of existing license keys '{lic_keys}'"
    )
    if license_key not in lic_keys:
        log.debug(
            f"cannot remove license '{license_key}' since not found in list of existing license keys '{lic_keys}'"
        )
        return False

    # Need to fine where license key is assigned and then un-assign it,
    # and only then can the license actually be removed, that is, RemoveLicense is a noop
    # if the license is assigned
    #
    # RemoveAssignedLicense takes entityId, reason to find were license key is assigned
    # Note: an entity can only have one license assigned

    try:
        # need to extract entity this license is intended to be removed from
        # choices are:
        #   1 vCenter - entity_id = service_instance.content.about.instanceUuid
        #   2 ESXi - entity_id = esxi host _moId
        #   3 cluster - entity_id = cluster _moId

        entity_id = None  # TBD miracle happens here and have value
        datacenter_ref = None
        if datacenter_name or cluster_name or esxi_hostname:
            if datacenter_name:
                # need to get named datacenter's reference
                datacenter_ref = utils_datacenter.get_datacenter(service_instance, datacenter_name)
                log.debug(
                    f"retrieved datacenter ref '{datacenter_ref }' for datacenter '{datacenter_name}'"
                )

            if cluster_name:
                # need to get named cluster's reference
                cluster_ref = utils_cluster.get_cluster(dc_ref=datacenter_ref, cluster=cluster_name)
                entity_id = cluster_ref._moId
                log.debug(
                    f"retrieved entityId '{entity_id}' from cluster ref '{cluster_ref }' for cluster '{cluster_name}' and datacenter '{datacenter_name}'"
                )

            if esxi_hostname:
                # need to get named esxi server
                esxi_hosts = utils_esxi.get_hosts(service_instance, datacenter_name, esxi_hostname)

                # returns hosts list of dicts
                if not esxi_hosts:
                    log.debug(f"Failed to find esxi hostname '{esxi_hostname}'")
                    return False

                if len(esxi_hosts) > 1:
                    log.error(
                        f"Failed, found multiple instances of esxi hostname '{esxi_hostname}', hosts returned '{esxi_hosts}'"
                    )
                    return False

                entity_id = esxi_hosts[0]._moId
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
            if assigned_lic and assigned_lic[0].assignedLicense.licenseKey == license_key:
                log.debug(
                    f"Unassigning license key '{license_key}' from entity identifer '{entity_id}'"
                )
                lic_assign_mgr.RemoveAssignedLicense(entityId=entity_id)

            else:
                log.debug(
                    f"no assigned license found, or the assigned license key for entity identifier '{entity_id}' did not match license key '{license_key}'"
                )
                return False

            log.debug(
                f"Removing license key '{license_key}' from License Managers pool of licenses"
            )
            lic_mgr.RemoveLicense(licenseKey=license_key)
        else:
            log.debug(
                f"Unable to find entity for specified inputs when attempting to remove license key '{license_key}'"
            )
            return False

    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    except AttributeError as exc:
        log.exception(exc)
        raise salt.exceptions.CommandExecutionError(exc.msg)
    except TypeError as exc:
        log.exception(exc)
        raise salt.exceptions.CommandExecutionError(exc.msg)

    return True
