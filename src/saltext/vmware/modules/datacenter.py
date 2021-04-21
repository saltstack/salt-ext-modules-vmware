import logging
import sys

import saltext.vmware.utils.vmware

from salt.utils.decorators import depends, ignores_kwargs

log = logging.getLogger(__name__)

try:
    # pylint: disable=no-name-in-module
    from pyVmomi import (
        vim,
        vmodl,
        pbm,
        VmomiSupport,
    )

    # pylint: enable=no-name-in-module

    # We check the supported vim versions to infer the pyVmomi version
    if (
        "vim25/6.0" in VmomiSupport.versionMap
        and sys.version_info > (2, 7)
        and sys.version_info < (2, 7, 9)
    ):

        log.debug(
            "pyVmomi not loaded: Incompatible versions " "of Python. See Issue #29537."
        )
        raise ImportError()
    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_datacenter"


def __virtual__():
    return __virtualname__


@depends(HAS_PYVMOMI)
@ignores_kwargs("credstore")
def list_datacenters():
    """
    Returns a list of datacenters for the specified host.
    """
    if salt.utils.platform.is_proxy():
        service_instance = _get_service_instance_via_proxy()
    else:
        service_instance = _get_service_instance()

    return saltext.vmware.utils.vmware.list_datacenters(service_instance)

@depends(HAS_PYVMOMI)
def create_datacenter(datacenter_name):
    """
    Creates a datacenter.

    Supported proxies: esxdatacenter

    datacenter_name
        The datacenter name

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.create_datacenter dc1
    """
    service_instance = saltext.vmware.utils.vmware.get
    if salt.utils.platform.is_proxy():
        service_instance = _get_service_instance_via_proxy()
    else:
        service_instance = _get_service_instance()

    saltext.vmware.utils.vmware.create_datacenter(service_instance, datacenter_name)
    return {"create_datacenter": True}

