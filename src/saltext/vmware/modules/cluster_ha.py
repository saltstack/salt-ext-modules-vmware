# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import salt.exceptions
import saltext.vmware.utils.cluster as utils_cluster
import saltext.vmware.utils.connect as connect
import saltext.vmware.utils.datacenter as utils_datacenter
import saltext.vmware.utils.esxi as utils_esxi

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_cluster_ha"
__proxyenabled__ = ["vmware_cluster_ha"]


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def _set_slot_based_admission_control_params(cluster_spec, admission_control_policy):
    """
    Set slot based admission control params
    """
    cluster_spec.dasConfig.admissionControlPolicy = (
        vim.cluster.FailoverLevelAdmissionControlPolicy()
    )
    cluster_spec.dasConfig.admissionControlPolicy.failoverLevel = admission_control_policy.get(
        "slot_based_admission_control", {}
    ).get("failover_level")
    cluster_spec.dasConfig.admissionControlPolicy.resourceReductionToToleratePercent = (
        admission_control_policy.get("slot_based_admission_control", {}).get(
            "resource_reduction_to_tolerate_percent"
        )
    )
    cluster_spec.dasConfig.admissionControlEnabled = True


def _set_failover_host_admission_control_params(
    cluster_spec, admission_control_policy, service_instance, datacenter, cluster
):
    """
    Set failover host admission control params
    """
    cluster_spec.dasConfig.admissionControlPolicy = vim.cluster.FailoverHostAdmissionControlPolicy()
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        datacenter_name=datacenter,
        cluster_name=cluster,
        host_names=admission_control_policy.get("failover_host_admission_control", {}).get(
            "failover_hosts"
        ),
    )
    cluster_spec.dasConfig.admissionControlPolicy.failoverHosts = hosts
    cluster_spec.dasConfig.admissionControlPolicy.failoverLevel = admission_control_policy.get(
        "failover_host_admission_control", {}
    ).get("failover_level")
    cluster_spec.dasConfig.admissionControlPolicy.resourceReductionToToleratePercent = (
        admission_control_policy.get("failover_host_admission_control", {}).get(
            "resource_reduction_to_tolerate_percent"
        )
    )
    cluster_spec.dasConfig.admissionControlEnabled = True


def _set_reservation_based_admission_control_params(cluster_spec, admission_control_policy):
    """
    Set reservation based admission control params
    """
    cluster_spec.dasConfig.admissionControlPolicy = (
        vim.cluster.FailoverResourcesAdmissionControlPolicy()
    )
    cluster_spec.dasConfig.admissionControlPolicy.failoverLevel = admission_control_policy.get(
        "reservation_based_admission_control", {}
    ).get("failover_level")
    autocompute_percentages = admission_control_policy.get(
        "reservation_based_admission_control", {}
    ).get("autocompute_percentages")
    cluster_spec.dasConfig.admissionControlPolicy.autoComputePercentages = autocompute_percentages
    if not autocompute_percentages:
        cluster_spec.dasConfig.admissionControlPolicy.cpuFailoverResourcesPercent = (
            admission_control_policy.get("reservation_based_admission_control", {}).get(
                "cpu_failover_resources_percent"
            )
        )
        cluster_spec.dasConfig.admissionControlPolicy.memoryFailoverResourcesPercent = (
            admission_control_policy.get("reservation_based_admission_control", {}).get(
                "memory_failover_resources_percent"
            )
        )
    cluster_spec.dasConfig.admissionControlPolicy.resourceReductionToToleratePercent = (
        admission_control_policy.get("reservation_based_admission_control", {}).get(
            "resource_reduction_to_tolerate_percent"
        )
    )
    cluster_spec.dasConfig.admissionControlEnabled = True


def _set_admission_control_params(
    cluster_spec, admission_control_policy, service_instance, datacenter, cluster
):
    """
    Set admission control params
    """
    cluster_spec.dasConfig.admissionControlEnabled = False
    if "slot_based_admission_control" in admission_control_policy:
        _set_slot_based_admission_control_params(cluster_spec, admission_control_policy)
    elif "failover_host_admission_control" in admission_control_policy:
        _set_failover_host_admission_control_params(
            cluster_spec, admission_control_policy, service_instance, datacenter, cluster
        )

    elif "reservation_based_admission_control" in admission_control_policy:
        _set_reservation_based_admission_control_params(cluster_spec, admission_control_policy)


def configure(
    cluster,
    datacenter,
    enable=False,
    host_monitoring=vim.cluster.DasConfigInfo.ServiceState.enabled,
    vm_monitoring=vim.cluster.DasConfigInfo.VmMonitoringState.vmMonitoringDisabled,
    vm_component_protecting=vim.cluster.DasConfigInfo.ServiceState.disabled,
    vm_min_up_time=120,
    vm_max_failure_window=-1,
    vm_max_failures=3,
    vm_failure_interval=30,
    isolation_response=vim.cluster.DasVmSettings.IsolationResponse.powerOff,
    restart_priority=vim.cluster.DasVmSettings.RestartPriority.medium,
    restart_priority_timeout=120,
    enable_apd_timeout_for_hosts=False,
    vm_reaction_on_apd_cleared="none",
    vm_storage_protection_for_apd="warning",
    vm_storage_protection_for_pdl="warning",
    vm_terminate_delay_for_apd_sec=180,
    admission_control_policy=None,
    advanced_options=None,
    service_instance=None,
    profile=None,
):
    """
    Configure HA for a given cluster

    Supported proxies: esxcluster

    cluster
        The cluster name

    datacenter
        The datacenter name to which the cluster belongs

    enable
        Enable HA for the cluster

    host_monitoring
        Determines whether HA restarts virtual machines after a host fails. Valid values - enabled, disabled. Default - enabled.

    vm_monitoring
        Specifies the level of HA Virtual Machine Health Monitoring Service. Valid values - vmAndAppMonitoring, vmMonitoringDisabled
        and vmMonitoringOnly. Default - vmMonitoringDisabled.

    vm_component_protecting
        Indicates if vSphere HA VM Component Protection service is enabled. Valid values - enabled, disabled. Default - disabled.

    vm_min_up_time
        The number of seconds for the virtual machine's heartbeats to stabilize after the virtual machine has been powered on.
        This time should include the guest operating system boot-up time. The virtual machine monitoring will begin only after this period.
        Default - 120 seconds.

    vm_max_failure_window
        The number of seconds for the window during which up to maxFailures resets can occur before automated responses stop.
        If set to -1, no failure window is specified. Default -1.

    vm_max_failures
        Maximum number of failures and automated resets allowed during the time that maxFailureWindow specifies.
        If maxFailureWindow is -1 (no window), this represents the absolute number of failures after which automated response is stopped.
        If a virtual machine exceeds this threshold, in-depth problem analysis is usually needed.
        The default value is 3.

    vm_failure_interval
        If no heartbeat has been received for at least the specified number of seconds, the virtual machine is declared as failed.
        The default value is 30.

    isolation_response
        Indicates whether or not the virtual machine should be powered off if a host determines that it is isolated from the rest of the compute resource.
        If not specified at either the cluster level or the virtual machine level, this will default to powerOff.

    restart_priority
        Restart priority for a virtual machine.
        If not specified at either the cluster level or the virtual machine level, this will default to medium.

    restart_priority_timeout
        This setting is used to specify a maximum time the lower priority VMs should wait for the higher priority VMs to be ready.
        If the higher priority Vms are not ready by this time, then the lower priority VMs are restarted irrespective of the VM ready state.
        This timeout can be used to prevent the failover of lower priority VMs to be stuck infinitely.
        Default - 120

    enable_apd_timeout_for_hosts
        This property indicates if APD timeout will be enabled for all the hosts in the cluster when vSphere HA is configured.
        Default - False

    vm_reaction_on_apd_cleared
        Action taken by VM Component Protection service for a powered on VM when APD condition clears after APD timeout.
        Default - none

    vm_storage_protection_for_apd
        VM storage protection setting for storage failures categorized as All Paths Down (APD).
        Valid values - disabled, warning, restartConservative, restartAggressive, clusterDefault. Default - warning

    vm_storage_protection_for_pdl
        VM storage protection setting for storage failures categorized as Permenant Device Loss (PDL).
        Valid values - disabled, warning, restartConservative, restartAggressive, clusterDefault. Default - warning

    vm_terminate_delay_for_apd_sec
        The time interval after an APD timeout has been declared and before VM Component Protection service will terminate the VM.
        Default 180 seconds.

    admission_control_policy
        Specify the admission control policy for the cluster as a dictionary.

        .. code-block:: json

            {
              "slot_based_admission_control": {
                "failover_level": 1,
                "resource_reduction_to_tolerate_percent": 20
              }
            }

            {
              "failover_host_admission_control": {
                "failover_level": 10,
                "resource_reduction_to_tolerate_percent": 30,
                "failover_hosts": ["host1", "host2"]
              }
            }

            {
                "reservation_based_admission_control": {
                    "failover_level": 22,
                    "resource_reduction_to_tolerate_percent": 33,
                    "autocompute_percentages": false,
                    "cpu_failover_resources_percent": 45,
                    "memory_failover_resources_percent": 56
                }
            }

    advanced_settings
        Advanced options for the cluster, to be passed in as a dictionary.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_cluster_ha.configure cluster1 dc1 enable=True
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    admission_control_policy = admission_control_policy or {}
    try:
        dc_ref = utils_datacenter.get_datacenter(service_instance, datacenter)
        cluster_ref = utils_cluster.get_cluster(dc_ref=dc_ref, cluster=cluster)
        cluster_spec = vim.cluster.ConfigSpecEx()
        cluster_spec.dasConfig = vim.cluster.DasConfigInfo()
        cluster_spec.dasConfig.enabled = enable
        cluster_spec.dasConfig.hostMonitoring = host_monitoring
        cluster_spec.dasConfig.vmMonitoring = vm_monitoring
        cluster_spec.dasConfig.vmComponentProtecting = vm_component_protecting

        vm_tool_spec = vim.cluster.VmToolsMonitoringSettings()
        vm_tool_spec.vmMonitoring = vm_monitoring
        vm_tool_spec.minUpTime = vm_min_up_time
        vm_tool_spec.maxFailureWindow = vm_max_failure_window
        vm_tool_spec.maxFailures = vm_max_failures
        vm_tool_spec.failureInterval = vm_failure_interval

        das_spec = vim.cluster.DasVmSettings()
        das_spec.isolationResponse = isolation_response
        das_spec.restartPriority = restart_priority
        das_spec.restartPriorityTimeout = restart_priority_timeout
        das_spec.vmToolsMonitoringSettings = vm_tool_spec

        component_protection_spec = vim.cluster.VmComponentProtectionSettings()
        component_protection_spec.enableAPDTimeoutForHosts = enable_apd_timeout_for_hosts
        component_protection_spec.vmReactionOnAPDCleared = vm_reaction_on_apd_cleared
        component_protection_spec.vmStorageProtectionForAPD = vm_storage_protection_for_apd
        component_protection_spec.vmStorageProtectionForPDL = vm_storage_protection_for_pdl
        component_protection_spec.vmTerminateDelayForAPDSec = vm_terminate_delay_for_apd_sec
        das_spec.vmComponentProtectionSettings = component_protection_spec

        _set_admission_control_params(
            cluster_spec=cluster_spec,
            admission_control_policy=admission_control_policy,
            service_instance=service_instance,
            datacenter=datacenter,
            cluster=cluster,
        )

        cluster_spec.dasConfig.defaultVmSettings = das_spec

        cluster_spec.dasConfig.option = []
        for key in advanced_options or {}:
            cluster_spec.dasConfig.option.append(
                vim.OptionValue(key=key, value=advanced_options[key])
            )
        utils_cluster.update_cluster(cluster_ref=cluster_ref, cluster_spec=cluster_spec)
    except (salt.exceptions.VMwareApiError, salt.exceptions.VMwareRuntimeError) as exc:
        return {cluster: False, "reason": str(exc)}
    return {cluster: True}


def get(cluster_name, datacenter_name, service_instance=None, profile=None):
    """
    Get HA info about a cluster in a datacenter

    cluster_name
        The cluster name

    datacenter_name
        The datacenter name to which the cluster belongs

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_cluster_ha.get cluster_name=cl1 datacenter_name=dc1
    """
    ret = {}
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    try:
        dc_ref = utils_datacenter.get_datacenter(service_instance, datacenter_name)
        cluster_ref = utils_cluster.get_cluster(dc_ref=dc_ref, cluster=cluster_name)
        das_config = cluster_ref.configurationEx.dasConfig
        ret["enabled"] = das_config.enabled
        ret["host_monitoring"] = das_config.hostMonitoring
        ret["vm_monitoring"] = das_config.vmMonitoring
        ret["vm_component_protecting"] = das_config.vmComponentProtecting

        if das_config.defaultVmSettings:
            vm_tools_monitoring_settings = das_config.defaultVmSettings.vmToolsMonitoringSettings
            ret["vm_monitoring"] = vm_tools_monitoring_settings.vmMonitoring
            ret["vm_min_up_time"] = vm_tools_monitoring_settings.minUpTime
            ret["vm_max_failure_window"] = vm_tools_monitoring_settings.maxFailureWindow
            ret["vm_max_failures"] = vm_tools_monitoring_settings.maxFailures
            ret["vm_failure_interval"] = vm_tools_monitoring_settings.failureInterval
            ret["isolation_response"] = das_config.defaultVmSettings.isolationResponse
            ret["restart_priority"] = das_config.defaultVmSettings.restartPriority
            ret["restart_priority_timeout"] = das_config.defaultVmSettings.restartPriorityTimeout

            component_protection_settings = (
                das_config.defaultVmSettings.vmComponentProtectionSettings
            )
            ret[
                "enable_apd_timeout_for_hosts"
            ] = component_protection_settings.enableAPDTimeoutForHosts
            ret["vm_reaction_on_apd_cleared"] = component_protection_settings.vmReactionOnAPDCleared
            ret[
                "vm_storage_protection_for_apd"
            ] = component_protection_settings.vmStorageProtectionForAPD
            ret[
                "vm_storage_protection_for_pdl"
            ] = component_protection_settings.vmStorageProtectionForPDL
            ret[
                "vm_terminate_delay_for_apd_sec"
            ] = component_protection_settings.vmTerminateDelayForAPDSec

            ret["admission_control_enabled"] = das_config.admissionControlEnabled
            ret["admission_control_policy"] = None
            ret["failover_level"] = das_config.admissionControlPolicy.failoverLevel
            ret[
                "resource_reduction_to_tolerate_percent"
            ] = das_config.admissionControlPolicy.resourceReductionToToleratePercent
            if isinstance(
                das_config.admissionControlPolicy,
                vim.cluster.FailoverLevelAdmissionControlPolicy,
            ):
                ret["admission_control_policy"] = "slot_based_admission_control"
            elif isinstance(
                das_config.admissionControlPolicy,
                vim.cluster.FailoverHostAdmissionControlPolicy,
            ):
                ret["admission_control_policy"] = "failover_host_admission_control"
                ret["failover_hosts"] = [
                    h.name for h in das_config.admissionControlPolicy.failoverHosts
                ]
            elif isinstance(
                das_config.admissionControlPolicy,
                vim.cluster.FailoverResourcesAdmissionControlPolicy,
            ):
                ret["admission_control_policy"] = "reservation_based_admission_control"
                ret[
                    "autocompute_percentages"
                ] = das_config.admissionControlPolicy.autoComputePercentages
                ret[
                    "cpu_failover_resources_percent"
                ] = das_config.admissionControlPolicy.cpuFailoverResourcesPercent
                ret[
                    "memory_failover_resources_percent"
                ] = das_config.admissionControlPolicy.memoryFailoverResourcesPercent

        ret["advanced_settings"] = {}
        for obj in cluster_ref.configurationEx.dasConfig.option:
            ret["advanced_settings"][obj.key] = obj.value
    except (salt.exceptions.VMwareApiError, salt.exceptions.VMwareRuntimeError) as exc:
        return {cluster_name: False, "reason": str(exc)}
    return ret
