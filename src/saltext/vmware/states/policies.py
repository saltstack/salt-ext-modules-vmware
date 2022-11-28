# SPDX-License-Identifier: Apache-2.0
import logging
import json

import saltext.vmware.modules.policies as policy_module
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.connect as connect
import saltext.vmware.utils.misc as misc

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vsphere_policy"
__proxyenabled__ = ["vsphere_policy"]


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def storage_policies_config(name, config_input, service_instance=None, profile=None):
    """
    Get/Set storage policies configuration based on drift report.

    name
        Name of configuration. (required).

    config_input
        Map with configuration values. (required).
        
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
    for policy_config in config_input:
        # Create full representation of the object, default or empty values
        new_policy_config = {
            "constraints": {}
        }
        # Transform / Validate input vs object, e.g. constraints section
        if "constraints" in policy_config:
            for constraint in policy_config["constraints"]:
                subProfileName = constraint["name"]
                new_policy_config["constraints"][subProfileName] = {}
                for key in constraint.keys():
                    if key != 'name':
                        new_policy_config["constraints"][subProfileName][key] = constraint[key]
        new_config[policy_config["policyName"]] = new_policy_config

    # print('-----------------------------')
    # print(json.dumps(new_config, indent=2))
    # print('-----------------------------')

    # Get all policies from vCenter, the objects are VMOMI objects
    policies = policy_module.find_storage_policies(policy_name=None, service_instance=service_instance, profile=profile)

    # make JSON representation of current policies
    # old_configs holds only the rules that are in the scope of interest (provided in argument config_input)
    old_config = {}
    for policy in policies:
        if policy.name not in new_config.keys():
            continue
        
        policy_json = {
            # "description": policy.description
        }
        policy_json['constraints'] = {}
        try:
            for sub_profile in policy.constraints.subProfiles:
                if sub_profile.name not in policy_json['constraints']:
                    policy_json['constraints'][sub_profile.name] = {}
 
                for capability in sub_profile.capability:
                    for constraint in capability.constraint:
                        for prop in constraint.propertyInstance:
                            policy_json['constraints'][sub_profile.name][prop.id] = prop.value
        except Exception as err:
            pass # skip if there is no subProfiles in policy.constraints
            
        old_config[policy.name] = policy_json

    # print('-----------------------------')
    # print(json.dumps(old_config, indent=2))
    # print('-----------------------------')

     # Find rules changes
    changes = []
    rule_diff = misc.drift_report(
        old_config, 
        new_config, 
        diff_level=0)
    policies_diff = json.loads(json.dumps(rule_diff)) # clone object
    if policies_diff is not None:
        ret["changes"] = policies_diff
        
        # print('=============================')
        # print(json.dumps(rule_diff, indent=2))
        # print('=============================')
        
        # add changes for process if not dry-run
        for policy_name in policies_diff:
            new_policy = policies_diff[policy_name]["new"]
            changes.append({"name": policy_name} | new_policy)

    # If it's not dry-run and has changes, then apply changes
    if not __opts__["test"] and changes:
        success = True
        
        print('=============================')
        print(json.dumps(changes, indent=2))
        print('=============================')
        
        ret["comment"] = "" # it's more readable if passed as object
        ret["result"] = success # at least one success

    return ret
