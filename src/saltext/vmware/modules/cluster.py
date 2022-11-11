# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import salt.exceptions
import saltext.vmware.utils.cluster as utils_cluster
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.connect as connect
import saltext.vmware.utils.datacenter as utils_datacenter

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_cluster"
__proxyenabled__ = ["vmware_cluster"]
__func_alias__ = {"list_": "list"}


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def list_(service_instance=None, profile=None):
    """
    Returns a dictionary containing a list of clusters for each datacenter.

    .. code-block:: bash

        salt '*' vmware_cluster.list
    """
    ret = {}
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    try:
        datacenters = utils_datacenter.get_datacenters(service_instance, get_all_datacenters=True)
        for datacenter in datacenters:
            clusters = utils_common.get_mors_with_properties(
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


def create(name, datacenter, service_instance=None, profile=None):
    """
    Creates a cluster.

    Supported proxies: esxcluster

    name
        The cluster name

    datacenter
        The datacenter name in which the cluster is to be created

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_cluster.create dc1 cluster1
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    try:
        dc_ref = utils_datacenter.get_datacenter(service_instance, datacenter)
        cluster_spec = vim.cluster.ConfigSpecEx()
        utils_cluster.create_cluster(cluster_name=name, dc_ref=dc_ref, cluster_spec=cluster_spec)
    except (salt.exceptions.VMwareApiError, salt.exceptions.VMwareRuntimeError) as exc:
        return {name: False, "reason": str(exc)}
    return {name: True}


def get(cluster_name, datacenter_name, service_instance=None, profile=None):
    """
    Get the properties of a cluster.

    cluster_name
        The cluster name

    datacenter_name
        The datacenter name to which the cluster belongs

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_cluster.get cluster_name=cl1 datacenter_name=dc1
    """
    ret = {}
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    try:
        dc_ref = utils_datacenter.get_datacenter(service_instance, datacenter_name)
        cluster_ref = utils_cluster.get_cluster(dc_ref=dc_ref, cluster=cluster_name)

        # DRS config
        ret["drs_enabled"] = cluster_ref.configurationEx.drsConfig.enabled
        if ret["drs_enabled"]:
            ret["drs"] = __salt__["vmware_cluster_drs.get"](
                cluster_name=cluster_name,
                datacenter_name=datacenter_name,
                service_instance=service_instance,
            )

        # HA config
        ret["ha_enabled"] = cluster_ref.configurationEx.dasConfig.enabled
        if ret["ha_enabled"]:
            ret["ha"] = __salt__["vmware_cluster_ha.get"](
                cluster_name=cluster_name,
                datacenter_name=datacenter_name,
                service_instance=service_instance,
            )

        # vSAN
        ret["vsan_enabled"] = cluster_ref.configurationEx.vsanConfigInfo.enabled

    except (salt.exceptions.VMwareApiError, salt.exceptions.VMwareObjectRetrievalError) as exc:
        return {cluster_name: False, "reason": str(exc)}
    return ret


def delete(name, datacenter, service_instance=None, profile=None):
    """
    Deletes a cluster.

    Supported proxies: esxcluster

    name
        The cluster name

    datacenter
        The datacenter name to which the cluster belongs

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_cluster.delete cl1 dc1
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    try:
        utils_cluster.delete_cluster(service_instance, name, datacenter)
    except (salt.exceptions.VMwareApiError, salt.exceptions.VMwareObjectRetrievalError) as exc:
        return {name: False, "reason": str(exc)}
    return {name: True}
