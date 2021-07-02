# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import salt.exceptions
import saltext.vmware.utils.vmware
from saltext.vmware.utils.connect import get_service_instance

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_cluster"
__proxyenabled__ = ["vmware_cluster"]
__func_alias__ = {"list_": "list", "get_": "get"}


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def list_():
    """
    Returns a dictionary containing a list of clusters for each datacenter.

    .. code-block:: bash

        salt '*' vmware_cluster.list
    """
    ret = {}
    service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    try:
        datacenters = saltext.vmware.utils.vmware.get_datacenters(
            service_instance, get_all_datacenters=True
        )
        for datacenter in datacenters:
            clusters = saltext.vmware.utils.vmware.get_mors_with_properties(
                service_instance,
                vim.ClusterComputeResource,
                container_ref=datacenter,
                property_list=["name"],
            )
            for cluster in clusters:
                ret.setdefault(datacenter.name, []).append(cluster.get("name"))
    except (salt.exceptions.VMwareApiError, salt.exceptions.VMwareObjectRetrievalError) as exc:
        log.error("Error retrieving cluster/datacenter - %s", str(exc))
    return ret


def create(name, datacenter):
    """
    Creates a cluster.

    Supported proxies: esxcluster

    name
        The cluster name

    datacenter
        The datacenter name in which the cluster is to be created

    .. code-block:: bash

        salt '*' vmware_cluster.create dc1 cluster1
    """
    service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    try:
        dc_ref = saltext.vmware.utils.vmware.get_datacenter(service_instance, datacenter)
        cluster_spec = vim.cluster.ConfigSpecEx()
        saltext.vmware.utils.vmware.create_cluster(
            cluster_name=name, dc_ref=dc_ref, cluster_spec=cluster_spec
        )
    except (salt.exceptions.VMwareApiError, salt.exceptions.VMwareRuntimeError) as exc:
        return {name: False, "reason": str(exc)}
    return {name: True}


def get_(name, datacenter):
    """
    Get the properties of a cluster.

    Supported proxies: esxcluster

    name
        The cluster name

    datacenter
        The datacenter name to which the cluster belongs

    .. code-block:: bash

        salt '*' vmware_cluster.get dc1
    """
    ret = {}
    service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    try:
        dc_ref = saltext.vmware.utils.vmware.get_datacenter(service_instance, datacenter)
        cluster_ref = saltext.vmware.utils.vmware.get_cluster(dc_ref=dc_ref, cluster=name)

        # DRS config
        ret["drs_enabled"] = cluster_ref.configurationEx.drsConfig.enabled

        # HA config
        ret["ha_enabled"] = cluster_ref.configurationEx.drsConfig.enabled

        # vSAN
        ret["vsan_enabled"] = cluster_ref.configurationEx.vsanConfigInfo.enabled

    except (salt.exceptions.VMwareApiError, salt.exceptions.VMwareObjectRetrievalError) as exc:
        return {name: False, "reason": str(exc)}
    return ret


def delete(name, datacenter):
    """
    Deletes a cluster.

    Supported proxies: esxcluster

    name
        The cluster name

    datacenter
        The datacenter name to which the cluster belongs

    .. code-block:: bash

        salt '*' vmware_cluster.delete cl1 dc1
    """
    service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    try:
        saltext.vmware.utils.vmware.delete_cluster(service_instance, name, datacenter)
    except (salt.exceptions.VMwareApiError, salt.exceptions.VMwareObjectRetrievalError) as exc:
        return {name: False, "reason": str(exc)}
    return {name: True}
