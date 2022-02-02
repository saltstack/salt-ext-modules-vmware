import logging

import salt.exceptions
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.datacenter as utils_datacenter

# pylint: disable=no-name-in-module
try:
    from pyVmomi import vim, vmodl

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False

log = logging.getLogger(__name__)


def get_clusters(service_instance, datacenter_name=None, cluster_name=None):
    """
    Returns clusters in a vCenter.

    service_instance
        The Service Instance Object from which to obtain cluster.

    datacenter_name
        (Optional) Datacenter name to filter by.

    cluster_name
        (Optional) Exact cluster name to filter by. Requires datacenter_name.
    """
    if cluster_name and not datacenter_name:
        raise salt.exceptions.ArgumentValueError(
            "datacenter_name is required when looking up by cluster_name"
        )

    clusters = []
    for cluster in utils_common.get_mors_with_properties(
        service_instance, vim.ClusterComputeResource, property_list=["name"]
    ):
        if cluster_name and cluster_name != cluster["name"]:
            continue
        if (
            datacenter_name
            and datacenter_name
            != utils_common.get_parent_of_type(cluster["object"], vim.Datacenter).name
        ):
            continue
        clusters.append(cluster["object"])
    return clusters


def get_cluster(dc_ref, cluster):
    """
    Returns a cluster in a datacenter.

    dc_ref
        The datacenter reference

    cluster
        The cluster to be retrieved
    """
    dc_name = utils_common.get_managed_object_name(dc_ref)
    log.trace("Retrieving cluster '%s' from datacenter '%s'", cluster, dc_name)
    si = utils_common.get_service_instance_from_managed_object(dc_ref, name=dc_name)
    traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(
        path="hostFolder",
        skip=True,
        type=vim.Datacenter,
        selectSet=[
            vmodl.query.PropertyCollector.TraversalSpec(
                path="childEntity", skip=False, type=vim.Folder
            )
        ],
    )
    items = [
        i["object"]
        for i in utils_common.get_mors_with_properties(
            si,
            vim.ClusterComputeResource,
            container_ref=dc_ref,
            property_list=["name"],
            traversal_spec=traversal_spec,
        )
        if i["name"] == cluster
    ]
    if not items:
        raise salt.exceptions.VMwareObjectRetrievalError(
            "Cluster '{}' was not found in datacenter " "'{}'".format(cluster, dc_name)
        )
    return items[0]


def create_cluster(dc_ref, cluster_name, cluster_spec):
    """
    Creates a cluster in a datacenter.

    dc_ref
        The parent datacenter reference.

    cluster_name
        The cluster name.

    cluster_spec
        The cluster spec (vim.ClusterConfigSpecEx).
        Defaults to None.
    """
    dc_name = utils_common.get_managed_object_name(dc_ref)
    log.trace("Creating cluster '%s' in datacenter '%s'", cluster_name, dc_name)
    try:
        dc_ref.hostFolder.CreateClusterEx(cluster_name, cluster_spec)
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)


def update_cluster(cluster_ref, cluster_spec):
    """
    Updates a cluster in a datacenter.

    cluster_ref
        The cluster reference.

    cluster_spec
        The cluster spec (vim.ClusterConfigSpecEx).
        Defaults to None.
    """
    cluster_name = utils_common.get_managed_object_name(cluster_ref)
    log.trace("Updating cluster '%s'", cluster_name)
    try:
        task = cluster_ref.ReconfigureComputeResource_Task(cluster_spec, modify=True)
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    utils_common.wait_for_task(task, cluster_name, "ClusterUpdateTask")


def delete_cluster(service_instance, cluster_name, datacenter_name):
    """
    Deletes a datacenter.

    service_instance
        The Service Instance Object

    cluster_name
        The name of the cluster to delete

    datacenter_name
        The datacenter name to which the cluster belongs
    """
    root_folder = utils_common.get_root_folder(service_instance)
    log.trace("Deleting cluster '%s' in '%s'", cluster_name, datacenter_name)
    try:
        dc_obj = utils_datacenter.get_datacenter(service_instance, datacenter_name)
        cluster_obj = get_cluster(dc_ref=dc_obj, cluster=cluster_name)
        task = cluster_obj.Destroy_Task()
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: {}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    utils_common.wait_for_task(task, cluster_name, "DeleteClusterTask")


def list_clusters(service_instance):
    """
    Returns a list of clusters associated with a given service instance.

    service_instance
        The Service Instance Object from which to obtain clusters.
    """
    return utils_common.list_objects(service_instance, vim.ClusterComputeResource)


def create_drs_rule(name, affinity, vm_refs, enabled, mandatory, cluster_ref):
    """
    Create a virtual machine to virtual machine affinity or anti affinity DRS rule

    name
        The name of the rule.

    affinity
        (boolean) Describes whether to make affinity or anti affinity rule.

    vm_refs
        Array of virtual machines associated with DRS rule.

    enabled
        (boolean) Enable the DRS rule being created.

    mandatory
        (boolean) Sets whether the rule being created is mandatory.

    cluster_ref
        Reference to cluster DRS rule is being created on.
    """
    if affinity:
        rule_spec = vim.cluster.AffinityRuleSpec()
    else:
        rule_spec = vim.cluster.AntiAffinityRuleSpec()
    rule_spec.vm = vm_refs
    rule_spec.enabled = enabled
    rule_spec.mandatory = mandatory
    rule_spec.name = name
    spec = vim.cluster.RuleSpec(info=rule_spec, operation="add")
    config_spec = vim.cluster.ConfigSpecEx(rulesSpec=[spec])
    task = cluster_ref.ReconfigureEx(config_spec, modify=True)
    utils_common.wait_for_task(task, "Cluster", "Create DRS rule Task")


def update_drs_rule(rule_ref, vm_refs, enabled, mandatory, cluster_ref):
    """
    Update a virtual machine to virtual machine affinity or anti affinity DRS rule

    rule_ref
        Reference to rule with same name.

    vm_refs
        Array of virtual machines associated with DRS rule.

    enabled
        (boolean) Enable the DRS rule being created. Defaults to True.

    mandatory
        (optional, boolean) Sets whether the rule being created is mandatory. Defaults to None.

    cluster_ref
        Reference to cluster DRS rule is being created on.
    """
    rule_ref.vm = vm_refs
    rule_ref.enabled = enabled
    rule_ref.mandatory = mandatory
    spec = vim.cluster.RuleSpec(info=rule_ref, operation="edit")
    config_spec = vim.cluster.ConfigSpecEx(rulesSpec=[spec])
    task = cluster_ref.ReconfigureEx(config_spec, modify=True)
    utils_common.wait_for_task(task, "Cluster", "Create DRS rule Task")


def drs_rule_info(rule):
    """
    Returns info on a DRS rule.

    rule
        Reference to DRS rule.
    """
    rule_info = {
        "name": rule.name,
        "uuid": rule.ruleUuid,
        "enabled": rule.enabled,
        "mandatory": rule.mandatory,
        "key": rule.key,
        "in_compliance": rule.inCompliance,
    }
    if type(rule) == vim.cluster.AntiAffinityRuleSpec or type(rule) == vim.cluster.AffinityRuleSpec:
        vms = []
        for vm in rule.vm:
            vms.append(vm.name)
        rule_info["type"] = "vm_affinity_rule"
        rule_info["vms"] = vms
        rule_info["affinity"] = check_affinity(rule)
    elif type(rule) == vim.cluster.VmHostRuleInfo:
        rule_info["type"] = "vm_host_rule"
        rule_info["vm_group_name"] = rule.vmGroupName
        rule_info["affine_host_group_name"] = rule.affineHostGroupName
        rule_info["anti_affine_host_group_name"] = rule.antiAffineHostGroupName
    elif type(rule) == vim.cluster.DependencyRuleInfo:
        rule_info["type"] = "dependency_rule"
        rule_info["vm_group"] = rule.vmGroup
        rule_info["depends_on_vm_group"] = rule.dependsOnVmGroup
    else:
        raise salt.exceptions.VMwareApiError({f"Unknown affinity rule type {type(rule)}"})
    return rule_info


def check_affinity(rule):
    """
    returns True if rule is Affine, or False if rule is AntiAffine.

    rule
        Reference to DRS rule.
    """
    if type(rule) == vim.cluster.AntiAffinityRuleSpec:
        return False
    elif type(rule) == vim.cluster.AffinityRuleSpec:
        return True
    else:
        raise Exception(f"Rule type {type(rule)} has no affinity.")
