# SPDX-License-Identifier: Apache-2.0
import logging

# Import salt libs
import salt.exceptions

# Import salt extension libs
import saltext.vmware.utils.vmware
from saltext.vmware.utils.connect import get_service_instance

log = logging.getLogger(__name__)

try:
    import pyVmomi

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_datacenter"
__proxyenabled__ = ["vmware_datacenter"]


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def list_datacenters():
    """
    Returns a list of datacenters for the specified host.

    .. code-block:: bash

        salt '*' vmware_datacenter.list_datacenters
    """
    service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    return saltext.vmware.utils.vmware.list_datacenters(service_instance)


def create_datacenter(datacenter_name):
    """
    Creates a datacenter.

    Supported proxies: esxdatacenter

    datacenter_name
        The datacenter name

    .. code-block:: bash

        salt '*' vmware_datacenter.create_datacenter dc1
    """
    service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    try:
        saltext.vmware.utils.vmware.create_datacenter(service_instance, datacenter_name)
    except salt.exceptions.VMwareApiError as exc:
        return {datacenter_name: False, "reason": str(exc)}
    return {datacenter_name: True}


def delete_datacenter(datacenter_name):
    """
    Deletes a datacenter.

    Supported proxies: esxdatacenter

    datacenter_name
        The datacenter name

    .. code-block:: bash

        salt '*' vmware_datacenter.delete_datacenter dc1
    """
    service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    try:
        saltext.vmware.utils.vmware.delete_datacenter(service_instance, datacenter_name)
    except (salt.exceptions.VMwareApiError, salt.exceptions.VMwareObjectRetrievalError) as exc:
        return {datacenter_name: False, "reason": str(exc)}
    return {datacenter_name: True}
