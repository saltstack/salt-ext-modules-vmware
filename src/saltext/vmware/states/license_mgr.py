# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging


log = logging.getLogger(__name__)

try:
    import pyVmomi

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_license_mgr"
__proxyenabled__ = ["vmware_license_mgr"]


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def absent(license_key, **kwargs):
    """
    Remove a license from specified Cluster, ESXI Server or vCenter
    If no datacenter, cluster or ESXI Server is specified, it is assumed the operation is to be applied to a vCenter

    Parameters:
      Required:
        * license
            License Key to remove from license manager

      Optional:
        * datacenter_name
            Datacenter name to use for the operation [default None]

        * cluster_name
            Name of the cluster from which to remove license [default None]

        * esxi_hostname
            Hostname of the ESXI Server from which to remove the license [default None]

    CLI Example:

    .. code-block:: yaml

    Remove license from License Manager:
      vmware_license_mgr.absent:
        - license: license_key
        - datacenter_name: dc1

    """
    ret = __salt__["vmware_license_mgr.remove"](license_key, **kwargs)
    return ret


def present(license_key, datacenter_name=None, cluster_name=None, esxi_hostname=None):
    """
    Add a license to specified Cluster, ESXI Server or vCenter
    If no datacenter, cluster or ESXI Server is specified, it is assumed the operation is to be applied to a vCenter

    Parameters:
      Required:
        * license
            License Key to add to license manager

      Optional:
        * datacenter_name
            Datacenter name to use for the operation [default None]

        * cluster_name
            Name of the cluster to add license [default None]

        * esxi_hostname
            Hostname of the ESXI Server to add license [default None]

    CLI Example:

    .. code-block:: yaml

    Add license to License Manager:
      vmware_license_mgr.present:
        - license: license_key
        - datacenter_name: dc1
    """
    ret = __salt__["vmware_license_mgr.add"](
        license_key, datacenter_name, cluster_name, esxi_hostname
    )
    return ret
