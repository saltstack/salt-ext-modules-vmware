# SPDX-License-Identifier: Apache-2.0
import logging
from salt.loader.lazy import global_injector_decorator
import saltext.vmware.states.esxi as esxi
import states.vsphere as state_storage_policy

log = logging.getLogger(__name__)

__virtualname__ = "vmware_drift_report"


def __virtual__():
    return __virtualname__


def report(name, firewall_config, advanced_config, storage_policy):
    """
    Creates drift report
    policies
        Policy list to set state to
    """
    context = {"__opts__": __opts__, "__salt__": __salt__, "__pillar__": __pillar__}
    firewall_result = global_injector_decorator(context)(esxi.firewall_config)(**firewall_config)["changes"]
    advanced_result = global_injector_decorator(context)(esxi.advanced_config)(**advanced_config)["changes"]
    storage_policy_result = global_injector_decorator(context)(state_storage_policy.storage_policy)(**storage_policy)["changes"]

    esxi_result = {host: {"firewall_config": firewall_result[host],
                          "advanced_config": advanced_result[host]} for host in firewall_result}

    ret = {"name": name, "result": True, "comment": "",
           "changes": {"esxi": esxi_result, "storagePolicies": storage_policy_result}}
    return ret