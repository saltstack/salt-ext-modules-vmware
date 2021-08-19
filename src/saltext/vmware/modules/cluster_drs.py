# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import salt.exceptions
import saltext.vmware.utils.datacenter as utils_datacenter
import saltext.vmware.utils.cluster as utils_cluster
from saltext.vmware.utils.connect import get_service_instance

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_cluster_drs"
__proxyenabled__ = ["vmware_cluster_drs"]
__func_alias__ = {"get_": "get"}


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def configure(
    cluster,
    datacenter,
    enable=False,
    enable_vm_behavior_overrides=True,
    default_vm_behavior=None,
    vmotion_rate=3,
    advanced_settings=None,
):
    """
    Configure a Distributed Resource Scheduler (DRS) for a given cluster

    Supported proxies: esxcluster

    cluster
        The cluster name

    datacenter
        The datacenter name to which the cluster belongs

    enable
        Enable DRS for the cluster

    enable_vm_behavior_overrides
        Flag that dictates whether DRS Behavior overrides for individual virtual machines are enabled.
        The default value is true.
        When this flag is true, overrides the default_vm_behavior.
        When this flag is false, the default_vm_behavior value applies to all virtual machines.

    default_vm_behavior
        Specifies the cluster-wide default DRS behavior for virtual machines.
        Valid Values:

        - ``fullyAutomated``: Specifies that VirtualCenter should automate both the migration of virtual machines
          and their placement with a host at power on.

        - ``manual``: Specifies that VirtualCenter should generate recommendations for virtual machine migration
          and for placement with a host, but should not implement the recommendations automatically.

        - ``partiallyAutomated``: Specifies that VirtualCenter should generate recommendations for virtual
          machine migration and for placement with a host, but should automatically
          implement only the placement at power on.

    vmotion_rate
        Threshold for generated ClusterRecommendations. DRS generates only those recommendations that are above
        the specified vmotionRate. Ratings vary from 1 to 5. This setting applies to manual, partiallyAutomated,
        and fullyAutomated DRS clusters. 1 - Conservative, 5 - Aggressive. Default is 3.

    advanced_settings
        Advanced options for the cluster, to be passed in as a dictionary.

    .. code-block:: bash

        salt '*' vmware_cluster_drs.configure cluster1 dc1 enable=True
    """
    service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    try:
        dc_ref = utils_datacenter.get_datacenter(service_instance, datacenter)
        cluster_ref = utils_cluster.get_cluster(dc_ref=dc_ref, cluster=cluster)
        cluster_spec = vim.cluster.ConfigSpecEx()
        cluster_spec.drsConfig = vim.cluster.DrsConfigInfo()
        cluster_spec.drsConfig.enabled = enable
        cluster_spec.drsConfig.enableVmBehaviorOverrides = enable_vm_behavior_overrides
        cluster_spec.drsConfig.defaultVmBehavior = default_vm_behavior
        cluster_spec.drsConfig.vmotionRate = 6 - vmotion_rate
        cluster_spec.drsConfig.option = []
        for key in advanced_settings or {}:
            cluster_spec.drsConfig.option.append(
                vim.OptionValue(key=key, value=advanced_settings[key])
            )
        utils_cluster.update_cluster(
            cluster_ref=cluster_ref, cluster_spec=cluster_spec
        )
    except (salt.exceptions.VMwareApiError, salt.exceptions.VMwareRuntimeError) as exc:
        return {cluster: False, "reason": str(exc)}
    return {cluster: True}


def get_(cluster, datacenter):
    """
    Get DRS info about a cluster in a datacenter

    cluster
        The cluster name

    datacenter
        The datacenter name to which the cluster belongs
    """
    ret = {}
    service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    try:
        dc_ref = utils_datacenter.get_datacenter(service_instance, datacenter)
        cluster_ref = utils_cluster.get_cluster(dc_ref=dc_ref, cluster=cluster)
        ret["enabled"] = cluster_ref.configurationEx.drsConfig.enabled
        ret[
            "enable_vm_behavior_overrides"
        ] = cluster_ref.configurationEx.drsConfig.enableVmBehaviorOverrides
        ret["default_vm_behavior"] = cluster_ref.configurationEx.drsConfig.defaultVmBehavior
        ret["vmotion_rate"] = 6 - cluster_ref.configurationEx.drsConfig.vmotionRate
        ret["advanced_settings"] = {}
        for obj in cluster_ref.configurationEx.drsConfig.option:
            ret["advanced_settings"][obj.key] = obj.value
    except (salt.exceptions.VMwareApiError, salt.exceptions.VMwareRuntimeError) as exc:
        return {cluster: False, "reason": str(exc)}
    return ret
