# SPDX-License-Identifier: Apache-2.0
import json
import logging

import saltext.vmware.modules.storage_policies as policy_module
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.connect as connect
import saltext.vmware.utils.drift as drift

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "storage_policy"
__proxyenabled__ = ["storage_policy"]


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def config(name, config, service_instance=None, profile=None):
    """
    Get/Set storage policies configuration based on drift report.

    name
        Name of configuration. (required).

    config
        List of objects with configuration values. (required).

    .. code-block:: yaml

        storage_policies_drift:
            storage_policy.config:
                - profile: vcenter
                - config:
                - policyName: Performance - Thick
                    constraints:
                    - name: VSAN
                        replicaPreference: 1 failures - RAID-1 (Mirroring)
                        hostFailuresToTolerate: 2
                        checksumDisabled: true
                        stripeWidth: 2
                        proportionalCapacity: 50
                        cacheReservation: 0
                - policyName: New VM Storage Policy
                    constraints:
                    - name: VSAN
                        hostFailuresToTolerate: 2
                        replicaPreference: 2 failures - RAID-1 (Mirroring)
                        proportionalCapacity: 1

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)
    """

    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    ret = {"name": name, "changes": {}, "result": None, "comment": ""}

    # Clone config input to a Map.
    # Can be used to transform input to internal objects and do validation if needed
    new_config = {}
    for policy_config in config:
        # Create full representation of the object, default or empty values
        new_policy_config = {"constraints": {}}
        # Transform / Validate input vs object, e.g. constraints section
        if "constraints" in policy_config:
            for constraint in policy_config["constraints"]:
                subProfileName = constraint["name"]
                new_policy_config["constraints"][subProfileName] = {}
                for key in constraint.keys():
                    if key != "name":
                        new_policy_config["constraints"][subProfileName][key] = constraint[key]
        new_config[policy_config["policyName"]] = new_policy_config

    log.debug("---------------NEW--------------")
    log.debug(json.dumps(new_config, indent=2))
    log.debug("---------------NEW--------------")

    # Get all policies from vCenter, the objects are VMOMI objects
    old_configs = policy_module.find(
        policy_name=None, service_instance=service_instance, profile=profile
    )

    # make JSON representation of current policies
    # old_configs holds only the rules that are in the scope of interest (provided in argument config_input)
    old_config = {}
    for policy in old_configs:
        if policy["policyName"] not in new_config.keys():
            continue

        policy_json = {"constraints": {}}

        for constraint in policy["constraints"]:
            subProfileName = constraint["name"]
            policy_json["constraints"][subProfileName] = {}
            for key in constraint.keys():
                if key != "name":
                    policy_json["constraints"][subProfileName][key] = constraint[key]

        old_config[policy["policyName"]] = policy_json

    log.debug("--------------OLD---------------")
    log.debug(json.dumps(old_config, indent=2))
    log.debug("--------------OLD---------------")

    # Find rules changes
    changes = []
    rule_diff = drift.drift_report(old_config, new_config, diff_level=0)
    policies_diff = json.loads(json.dumps(rule_diff))  # clone object
    if policies_diff is not None:
        ret["changes"] = policies_diff

        log.debug("==============DRIFT===============")
        log.debug(json.dumps(rule_diff, indent=2))
        log.debug("==============DRIFT===============")

        # add changes for process if not dry-run
        for policy_name in policies_diff:
            new_policy = policies_diff[policy_name]["new"]
            changes.append({**{"name": policy_name}, **new_policy})

    # If it's not dry-run and has changes, then apply changes
    if not __opts__["test"] and changes:
        success = True

        log.debug("===============CHANGES==============")
        log.debug(json.dumps(changes, indent=2))
        log.debug("===============CHANGES==============")

        comments = {}
        for change in changes:
            try:
                # convert change report to configuration object
                new_constraints = []
                for constr_name in change["constraints"].keys():
                    constr_props = change["constraints"][constr_name].copy()
                    constr_props["name"] = constr_name
                    new_constraints.append(constr_props)
                update = {"policyName": change["name"], "constraints": new_constraints}
                # save policy
                policy_module.save(update, service_instance, profile)
                comments[change["name"]] = {
                    "status": "SUCCESS",
                    "message": f"Storage policy '{change['name']}' has been changed successfully.",
                }
            except Exception as err:
                success = False
                comments[change["name"]] = {
                    "status": "FAILURE",
                    "message": f"Error occured while save storage policy '{change['name']}': {err}",
                }

        ret["comment"] = comments  # it's more readable if passed as object
        ret["result"] = success  # at least one success

    return ret
