# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import salt.exceptions
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.connect as connect
import saltext.vmware.utils.datacenter as utils_datacenter

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_datacenter"
__proxyenabled__ = ["vmware_datacenter"]
__func_alias__ = {"list_": "list"}


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def list_(service_instance=None, profile=None):
    """
    Returns a list of datacenters for the specified host.

    .. code-block:: bash

        salt '*' vmware_datacenter.list
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    return utils_datacenter.list_datacenters(service_instance)


def create(name, service_instance=None, profile=None):
    """
    Creates a datacenter.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    Supported proxies: esxdatacenter

    name
        The datacenter name

    .. code-block:: bash

        salt '*' vmware_datacenter.create dc1
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    try:
        utils_datacenter.create_datacenter(service_instance, name)
    except salt.exceptions.VMwareApiError as exc:
        return {name: False, "reason": str(exc)}
    return {name: True}


def get(name, service_instance=None, profile=None):
    """
    Get the properties of a datacenter.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    Supported proxies: esxdatacenter

    name
        The datacenter name

    .. code-block:: bash

        salt '*' vmware_datacenter.get dc1
    """
    ret = {}
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    try:
        dc_ref = utils_datacenter.get_datacenter(service_instance, name)
        dc = utils_common.get_mors_with_properties(
            service_instance, vim.Datacenter, container_ref=dc_ref, local_properties=True
        )
        if dc:
            ret = dc[0]
    except (salt.exceptions.VMwareApiError, salt.exceptions.VMwareObjectRetrievalError) as exc:
        return {name: False, "reason": str(exc)}
    return ret


def delete(name, service_instance=None, profile=None):
    """
    Deletes a datacenter.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    Supported proxies: esxdatacenter

    name
        The datacenter name

    .. code-block:: bash

        salt '*' vmware_datacenter.delete dc1
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    try:
        utils_datacenter.delete_datacenter(service_instance, name)
    except (salt.exceptions.VMwareApiError, salt.exceptions.VMwareObjectRetrievalError) as exc:
        return {name: False, "reason": str(exc)}
    return {name: True}
