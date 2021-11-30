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


def add(license, **kwargs):
    """
    Add a license to specified Cluster, ESXI Server or vCenter
    If no datacenter, cluster or ESXI Server is specified, it is assumed the operation is to be applied to a vCenter

    Parameters:
      Required:
        * license
            License Key to add to license manager

      Optional:
        * service_instance
            Use this vCenter service connection instance instead of creating a new one [default None]

        * datacenter_name
            Datacenter name to use for the operation [default None]

        * cluster_name
            Name of the cluster to add license [default None]

        * esxi_hostname
            Hostname of the ESXI Server to add license [default None]

    CLI Example:

    .. code-block: bash

        salt '*' vmware_license_mgr.add license datacenter_name=dc1
    """
    log.debug("DGM vmware ext license_mgr add lic entered")
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

    log.debug(
        "DGM vmware ext license_mgr add lic retrieved service_instance, with opts '{__opts__}', pillar '{__pillar__}'"
    )

    if not utils_license_mgr.is_vcenter(service_instance):
        ret["comment"] = "Failed, not connected to a vCenter"
        ret["result"] = False
        return ret

    try:
        result = utils_license_mgr.add_license(
            service_instance, license, datacenter_name, cluster_name, esxi_hostname
        )
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
            ret["stdout"] = licmgr[0]
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
    log.debug("DGM vmware ext license_mgr list entered")
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    log.debug(
        "DGM vmware ext license_mgr list retrieved service_instance, with opts '{__opts__}', pillar '{__pillar__}'"
    )
    return utils_license_mgr.list_licenses(service_instance)


def remove(license, **kwargs):
    """
    Remove a license from specified Cluster, ESXI Server or vCenter
    If no datacenter, cluster or ESXI Server is specified, it is assumed the operation is to be applied to a vCenter

    Parameters:
      Required:
        * license
            License Key to add to license manager

      Optional:
        * service_instance
            Use this vCenter service connection instance instead of creating a new one [default None]

        * datacenter_name
            Datacenter name to use for the operation [default None]

        * cluster_name
            Name of the cluster to add license [default None]

        * esxi_hostname
            Hostname of the ESXI Server to add license [default None]

    CLI Example:

    .. code-block: bash

        salt '*' vmware_license_mgr.remove license
    """
    log.debug("DGM vmware ext license_mgr remove lic entered")
    ## service_instance = None
    ## datacenter_name = None
    ## cluster_name = None
    ## esxi_hostname = None

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

    log.debug(
        "DGM vmware ext license_mgr remove lic retrieved service_instance, with opts '{__opts__}', pillar '{__pillar__}'"
    )

    if not utils_license_mgr.is_vcenter(service_instance):
        ret["comment"] = "Failed, not connected to a vCenter"
        ret["result"] = False
        return ret

    try:
        result = utils_license_mgr.remove_license(
            service_instance, license, datacenter_name, cluster_name, esxi_hostname
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
