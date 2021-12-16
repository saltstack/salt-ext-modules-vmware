# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import pudb
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.license_mgr as utils_license_mgr
from saltext.vmware.utils.connect import get_service_instance

import salt.exceptions

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


def add(license_key, **kwargs):
    """
    Add a license specified by license key to a Datacenter, Cluster, ESXI Server or vCenter
    If no datacenter, cluster or ESXI Server is specified, it is assumed the operation is to be applied to a vCenter

    license_key
        License Key which specifies license to add to license manager

    service_instance
        Use this vCenter service connection instance instead of creating a new one [default None]

    datacenter_name
        Datacenter name to use for the operation [default None]

    cluster_name
        Name of the cluster to add license [default None]

    esxi_hostname
        Hostname of the ESXI Server to add license [default None]

    CLI Example:

    .. code-block: bash

        salt '*' vmware_license_mgr.add license_key datacenter_name=dc1
    """
    pu.db

    log.debug("start vmware ext license_mgr add license_key")

    ret = {}
    op = {}
    for key, value in kwargs.items():
        op[key] = value

    service_instance = op.pop("service_instance", None)
    datacenter_name = op.pop("datacenter_name", None)
    cluster_name = op.pop("cluster_name", None)
    esxi_hostname = op.pop("esxi_hostname", None)

    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)

    ## log.debug(
    ##     f"vmware ext license_mgr add lic retrieved service_instance, with opts '{__opts__}', pillar '{__pillar__}'"
    ## )

    if not utils_license_mgr.is_vcenter(service_instance):
        ret["comment"] = "Failed, not connected to a vCenter"
        ret["result"] = False
        return ret

    try:
        if "test" in __opts__ and __opts__["test"]:
            ret["licenses"] = license_key
            ret["comment"] = "Test dry-run, not really connected to a vCenter testing"
            return ret

        result = utils_license_mgr.add_license(
            service_instance, license_key, datacenter_name, cluster_name, esxi_hostname
        )
        if result:
            ret["licenses"] = license_key

    except (
        salt.exceptions.VMwareApiError,
        salt.exceptions.VMwareObjectRetrievalError,
        salt.exceptions.VMwareRuntimeError,
    ) as exc:
        ret["comment"] = f"Failed to add a license due to Exception '{str(exc)}'"
        ret["result"] = False
        return ret

    if not result:
        ret["comment"] = f"Failed specified license was not added to License Manager"
        ret["result"] = False

    return ret


def get_(service_instance=None):
    """
    Get the properties of a License Manager

    service_instance
        Use this vCenter service connection instance instead of creating a new one [default None]

    .. code-block:: bash

        salt '*' vmware_license_mgr.get
    """
    pu.db
    ret = {}
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    try:
        licmgr_ref = utils_license_mgr.get_license_mgr(service_instance)
        licmgr = utils_common.get_mors_with_properties(
            service_instance,
            vim.LicenseManager,
            property_list=None,
            container_ref=licmgr_ref,
            traversal_spec=None,
            local_properties=True,
        )
        if licmgr:
            log.debug(f"license manager mors and properties '{licmgr[0]}'")

            # TBD need a better way to pass back the dictionary
            ret["mors_properties"] = licmgr[0]
    except (salt.exceptions.VMwareApiError, salt.exceptions.VMwareObjectRetrievalError) as exc:
        return {name: False, "reason": str(exc)}
    return ret


def list_(service_instance=None):
    """
    Returns a list of licenses for the specified Service Instance

    service_instance
        Use this vCenter service connection instance instead of creating a new one [default None]

    .. code-block:: bash

        salt '*' vmware_license_mgr.list
    """
    pu.db
    log.debug("start vmware ext license_mgr list")
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)

    ## log.debug(
    ##     f"vmware ext license_mgr list retrieved service_instance, with opts '{__opts__}', pillar '{__pillar__}'"
    ## )

    if "test" in __opts__ and __opts__["test"]:
        ret["licenses"] = "DGMTT-FAKED-TESTS-LICEN-SE012"
        ret["comment"] = "Test dry-run, not really connected to a vCenter testing"
        return ret

    return utils_license_mgr.list_licenses(service_instance)


def remove(license_key, **kwargs):
    """
    Remove a license specified by license_key from a Datacenter, Cluster, ESXI Server or vCenter
    If no datacenter, cluster or ESXI Server is specified, it is assumed the operation is to be applied to a vCenter

    license_key
        License Key which specifies license to remove from the license manager

    service_instance
        Use this vCenter service connection instance instead of creating a new one [default None]

    datacenter_name
        Datacenter name to use for the operation [default None]

    cluster_name
        Name of the cluster to add license [default None]

    esxi_hostname
        Hostname of the ESXI Server to add license [default None]

    CLI Example:

    .. code-block: bash

        salt '*' vmware_license_mgr.remove license_key
    """
    log.debug("start vmware ext license_mgr remove license_key")
    pu.db

    ret = {}
    op = {}
    for key, value in kwargs.items():
        op[key] = value

    service_instance = op.pop("service_instance", None)
    datacenter_name = op.pop("datacenter_name", None)
    cluster_name = op.pop("cluster_name", None)
    esxi_hostname = op.pop("esxi_hostname", None)

    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)

    ## log.debug(
    ##     f"vmware ext license_mgr remove lic retrieved service_instance, with opts '{__opts__}', pillar '{__pillar__}'"
    ## )

    if not utils_license_mgr.is_vcenter(service_instance):
        ret["comment"] = "Failed, not connected to a vCenter"
        ret["result"] = False
        return ret

    try:
        if "test" in __opts__ and __opts__["test"]:
            ret["licenses"] = license_key
            ret["comment"] = "Test dry-run, not really connected to a vCenter testing"
            return ret

        result = utils_license_mgr.remove_license(
            service_instance, license_key, datacenter_name, cluster_name, esxi_hostname
        )
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
