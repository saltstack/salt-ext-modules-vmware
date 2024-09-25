# SPDX-License-Identifier: Apache-2.0
import json
import logging

import saltext.vmware.modules.roles as roles_module
import saltext.vmware.utils.connect as connect
import saltext.vmware.utils.drift as drift

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vcenter_roles"
__proxyenabled__ = ["vcenter_roles"]


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def config(name, config, service_instance=None, profile=None):
    """
    Get/Set roles configuration based on drift report.

    name
        Name of configuration. (required).

    config
        List of objects with configuration values. (required).

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: yaml

        vcenter_roles_config_example:
            vcenter_roles.config:
                - profile: vcenter
                - config:
                - role: SRM Administrator
                    groups:
                    - group: SRM Protection
                        privileges:
                        - Stop
                        - Protect
                    - group: Recovery History
                        privileges:
                        - Delete History
                        - View Deleted Plans
                    - group: Recovery Plan
                        privileges:
                        - Configure commands
                        - Create
                        - Remove
                        - Modify
                        - Recovery
                    - group: Protection Group
                        privileges:
                        - Assign to plan
                        - Create
                        - Modify
                        - Remove
                        - Remove from plan
    """

    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    ret = {"name": name, "changes": {}, "result": None, "comment": ""}

    # # Clone config input to a Map.
    # # Can be used to transform input to internal objects and do validation if needed
    new_config = {}
    for role_config in config:
        # Create full representation of the object, default or empty values
        new_role_config = {"privileges": {}}
        # Transform / Validate input vs object, e.g. constraints section
        if "groups" in role_config:
            for privilege in role_config["groups"]:
                priv_group = privilege["group"]
                new_role_config["privileges"][priv_group] = []
                for item in privilege["privileges"]:
                    new_role_config["privileges"][priv_group].append(item)
        new_config[role_config["role"]] = new_role_config

    log.debug("---------------NEW--------------")
    log.debug(json.dumps(new_config, indent=2))
    log.debug("---------------NEW--------------")

    # Get all policies from vCenter, the objects are VMOMI objects
    old_configs = roles_module.find(
        role_name=None, service_instance=service_instance, profile=profile
    )

    # old_configs must have only the rules that are in the scope of interest (provided in argument config_input)
    old_config = {}
    for role in old_configs:
        if role["role"] not in new_config.keys():
            continue

        old_config[role["role"]] = {"privileges": role["privileges"]}

    log.debug("--------------OLD---------------")
    log.debug(json.dumps(old_config, indent=2))
    log.debug("--------------OLD---------------")

    # Find rules changes
    changes = []
    diffs = drift.drift_report(old_config, new_config, diff_level=0)
    diffs = json.loads(json.dumps(diffs))  # clone object
    if diffs is not None:
        ret["changes"] = diffs

        log.debug("==============DRIFT===============")
        log.debug(json.dumps(diffs, indent=2))
        log.debug("==============DRIFT===============")

        # add changes for process if not dry-run
        for d_name in diffs:
            new_policy = diffs[d_name]["new"]
            changes.append({**{"role": d_name}, **new_policy})

    # If it's not dry-run and has changes, then apply changes
    if not __opts__["test"] and changes:
        success = True

        log.debug("===============CHANGES==============")
        log.debug(json.dumps(changes, indent=2))
        log.debug("===============CHANGES==============")

        comments = {}
        for change in changes:
            try:
                # save/update rule
                roles_module.save(change, service_instance, profile)
                comments[change["role"]] = {
                    "status": "SUCCESS",
                    "message": f"Role '{change['role']}' has been changed successfully.",
                }
            except Exception as err:
                success = False
                comments[change["role"]] = {
                    "status": "FAILURE",
                    "message": f"Error occured while saving role '{change['role']}': {err}",
                }

        ret["comment"] = comments  # it's more readable if passed as object
        ret["result"] = success  # at least one success

    return ret
