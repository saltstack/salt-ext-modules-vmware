# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

# noreorder
import salt.exceptions
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.license_mgr as utils_license_mgr
import saltext.vmware.utils.connect as connect

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_license_mgr"
__proxyenabled__ = ["vmware_license_mgr"]
__func_alias__ = {"list_": "list"}


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
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    datacenter_name
        Datacenter name to use for the operation [default None]

    cluster_name
        Name of the cluster to add license [default None]

    esxi_hostname
        Hostname of the ESXI Server to add license [default None]

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_license_mgr.add license_key=AAAAA-11111-AAAAA-11111-AAAAA datacenter_name=dc1
    """
    ret = {}

    service_instance = kwargs.get("service_instance", None)
    datacenter_name = kwargs.get("datacenter_name", None)
    cluster_name = kwargs.get("cluster_name", None)
    esxi_hostname = kwargs.get("esxi_hostname", None)
    profile = kwargs.get("profile", None)

    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )

    if not utils_license_mgr.is_vcenter(service_instance):
        ret["message"] = "Failed, not connected to a vCenter"
        ret["result"] = False
        return ret

    try:
        if __opts__.get("test", None):
            ret["licenses"] = license_key
            ret["message"] = "Test dry-run, not really connected to a vCenter testing"
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
        salt.exceptions.CommandExecutionError,
    ) as exc:
        log.exception(exc)
        ret["message"] = f"Failed to add a license key due to Exception '{exc}'"
        ret["result"] = False
        return ret

    if not result:
        ret["message"] = f"Failed specified license key was not added to License Manager"
        ret["result"] = False

    return ret


def list_(service_instance=None, profile=None):
    """
    Returns a list of licenses for the specified Service Instance

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_license_mgr.list
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )

    return utils_license_mgr.list_licenses(service_instance)


def remove(license_key, **kwargs):
    """
    Remove a license specified by license_key from a Datacenter, Cluster, ESXI Server or vCenter
    If no datacenter, cluster or ESXI Server is specified, it is assumed the operation is to be applied to a vCenter

    license_key
        License Key which specifies license to remove from the license manager

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    datacenter_name
        Datacenter name to use for the operation [default None]

    cluster_name
        Name of the cluster to add license [default None]

    esxi_hostname
        Hostname of the ESXI Server to add license [default None]

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_license_mgr.remove license_key=AAAAA-11111-AAAAA-11111-AAAAA
    """
    ret = {}

    service_instance = kwargs.get("service_instance", None)
    datacenter_name = kwargs.get("datacenter_name", None)
    cluster_name = kwargs.get("cluster_name", None)
    esxi_hostname = kwargs.get("esxi_hostname", None)
    profile = kwargs.get("profile", None)

    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )

    if not utils_license_mgr.is_vcenter(service_instance):
        ret["message"] = "Failed, not connected to a vCenter"
        ret["result"] = False
        return ret

    try:
        if __opts__.get("test", None):
            ret["licenses"] = license_key
            ret["message"] = "Test dry-run, not really connected to a vCenter testing"
            return ret

        result = utils_license_mgr.remove_license(
            service_instance, license_key, datacenter_name, cluster_name, esxi_hostname
        )
    except (
        salt.exceptions.VMwareApiError,
        salt.exceptions.VMwareObjectRetrievalError,
        salt.exceptions.VMwareRuntimeError,
        salt.exceptions.CommandExecutionError,
    ) as exc:
        log.exception(exc)
        ret["message"] = f"Failed to remove license key due to Exception '{exc}'"
        ret["result"] = False
        return ret

    if not result:
        ret["message"] = f"Failed specified license key was not found in License Manager"
        ret["result"] = False

    return ret
