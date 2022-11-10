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
    service_instance=None,
    profile=None,
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

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_cluster_drs.configure cluster1 dc1 enable=True
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
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
        utils_cluster.update_cluster(cluster_ref=cluster_ref, cluster_spec=cluster_spec)
    except (salt.exceptions.VMwareApiError, salt.exceptions.VMwareRuntimeError) as exc:
        return {cluster: False, "reason": str(exc)}
    return {cluster: True}


def get(cluster_name, datacenter_name, service_instance=None, profile=None):
    """
    Get DRS info about a cluster in a datacenter

    cluster_name
        The cluster name

    datacenter_name
        The datacenter name to which the cluster belongs

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_cluster_drs.get cluster_name=cl1 datacenter_name=dc1
    """
    ret = {}
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    try:
        dc_ref = utils_datacenter.get_datacenter(service_instance, datacenter_name)
        cluster_ref = utils_cluster.get_cluster(dc_ref=dc_ref, cluster=cluster_name)
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
        return {cluster_name: False, "reason": str(exc)}
    return ret


def vm_affinity_rule(
    name,
    affinity,
    vm_names,
    cluster_name,
    datacenter_name,
    enabled=True,
    mandatory=None,
    service_instance=None,
    profile=None,
):
    """
    Configure a virtual machine to virtual machine DRS rule

    name
        The name of the rule.

    affinity
        (boolean) Describes whether to make affinity or anti affinity rule.

    vm_names
        List of virtual machines associated with DRS rule.

    cluster_name
        The name of the cluster to configure a rule on.

    datacenter_name
        The name of the datacenter where the cluster exists.

    enabled
        (optional, boolean) Enable the DRS rule being created. Defaults to True.

    mandatory
        (optional, boolean) Sets whether the rule being created is mandatory. Defaults to False.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.

    profile
        Profile to use (optional)

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_cluster_drs.vm_affinity_rule name="Example Anti-Affinity Rule" affinity=False vm_names='["vm1", "vm2"]' cluster_name=cl1 datacenter_name=dc1 mandatory=True
    """
    log.debug(f"Configuring a vm to vm DRS rule {name} on cluster {cluster_name}.")
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    dc_ref = utils_common.get_datacenter(service_instance, datacenter_name)
    cluster_ref = utils_cluster.get_cluster(dc_ref, cluster_name)
    vm_refs = []
    missing_vms = []
    for vm_name in vm_names:
        vm_ref = utils_common.get_mor_by_property(service_instance, vim.VirtualMachine, vm_name)
        if not vm_ref:
            missing_vms.append(vm_name)
        vm_refs.append(vm_ref)
    if missing_vms:
        raise salt.exceptions.VMwareApiError({f"Could not find virtual machines {missing_vms}"})
    rules = cluster_ref.configuration.rule
    rule_ref = None
    if rules:
        for rule in rules:
            if rule.name == name:
                rule_info = utils_cluster.drs_rule_info(rule)
                if utils_cluster.check_affinity(rule) != affinity:
                    return {
                        "updated": False,
                        "message": f"Existing rule of name {name} has an affinity of {not affinity} and cannot be changed, make new rule.",
                    }
                if (
                    rule_info["vms"] == vm_names
                    and rule_info["enabled"] == enabled
                    and rule_info["mandatory"] == mandatory
                ):
                    return {
                        "updated": True,
                        "message": "Exact rule already exists.",
                    }
                rule_ref = rule

    if rule_ref:
        utils_cluster.update_drs_rule(rule_ref, vm_refs, enabled, mandatory, cluster_ref)
        return {"updated": True}
    else:
        utils_cluster.create_drs_rule(name, affinity, vm_refs, enabled, mandatory, cluster_ref)
        return {"created": True}


def rule_info(cluster_name, datacenter_name, rule_name=None, service_instance=None, profile=None):
    """
    Return a list of all the DRS rules on a given cluster, or one DRS rule if filtered by rule_name.

    cluster_name
        The name of the cluster to get rules from.

    datacenter_name
        The name of the datacenter where the cluster exists.

    rule_name
        (optional) Return only the rule with rule_name

    service_instance
        (optional) The Service Instance from which to obtain managed object references.

    profile
        Profile to use (optional)

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_cluster_drs.rule_info cluster_name=cl1 datacenter_name=dc1
    """
    log.debug(f"Getting rules info on cluster {cluster_name}.")
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    dc_ref = utils_common.get_datacenter(service_instance, datacenter_name)
    cluster_ref = utils_cluster.get_cluster(dc_ref, cluster_name)
    rules = cluster_ref.configuration.rule
    info = []
    if rule_name:
        for rule in rules:
            if rule.name == rule_name:
                return utils_cluster.drs_rule_info(rule)
    else:
        for rule in rules:
            info.append(utils_cluster.drs_rule_info(rule))
        return info
    raise salt.exceptions.VMwareApiError({f"Rule name {rule_name} not found."})
