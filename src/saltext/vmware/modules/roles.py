# Copyright 2021 VMware, Inc.
# SPDX-License: Apache-2.0
import json
import logging

import salt.exceptions
import saltext.vmware.utils.connect as connect

log = logging.getLogger(__name__)

try:
    from pyVmomi import pbm, VmomiSupport, SoapStubAdapter, vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vcenter_roles"


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def find(role_name=None, service_instance=None, profile=None):
    """
    Gets vCenter roles. Returns list.

    role_name
        Filter by role name, if None returns all policies

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    Returns:
        List of all roles or filtered by role_name

    .. code-block:: json
    {
        "role": "SRM Administrator",
        "privileges": {
            "Protection Group": [
                "Assign to plan",
                "Create",
                "Modify",
                "Remove",
                "Remove from plan"
            ],
            "Recovery Plan": [
                "Configure commands",
                "Create",
                "Remove",
                "Modify",
                "Recovery"
            ]
        }
    }
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )

    authorizationManager = service_instance.RetrieveContent().authorizationManager

    # Collect priviliges descriptions
    privileges_desc = {}
    privilege_groups_desc = {}
    for desciption in authorizationManager.description.privilege:
        privileges_desc[desciption.key] = {"label": desciption.label, "summary": desciption.summary}
    for desciption in authorizationManager.description.privilegeGroup:
        privilege_groups_desc[desciption.key] = {
            "label": desciption.label,
            "summary": desciption.summary,
        }

    # Collect all privilages with their descriptions
    privileges = {}
    for privilege in authorizationManager.privilegeList:
        desciption = privileges_desc[privilege.privId]
        desciption_group = privilege_groups_desc[privilege.privGroupName]
        privileges[privilege.privId] = {
            "name": privilege.name,
            "label": desciption["label"],
            "summary": desciption["summary"],
            "groupName": privilege.privGroupName,
            "groupLabel": desciption_group["label"],
            "onParent": privilege.onParent,
        }

    # make JSON representation of current policies
    # old_configs holds only the rules that are in the scope of interest (provided in argument config_input)
    result = []
    for role in authorizationManager.roleList:
        if role_name is not None and role_name != role.info.label:
            continue

        role_json = {
            "id": role.roleId,
            "roleName": role.name,
            "label": role.info.label,
            "description": role.info.summary,
            "system": role.system,
        }
        role_json["privileges"] = []
        for privilage_id in role.privilege:
            role_privilege = privileges[privilage_id]
            role_json["privileges"].append(
                {
                    "id": privilage_id,
                    "name": role_privilege["label"],
                    "description": role_privilege["summary"],
                    "groupName": role_privilege["groupName"],
                    "groupLabel": role_privilege["groupLabel"],
                    "onParent": role_privilege["onParent"],
                }
            )
        result.append(role_json)

    # make JSON representation of current policies
    roles_config = []
    for role in result:
        role_json = {"role": role["label"], "privileges": {}}
        for privilege in role["privileges"]:
            priv_name = privilege["name"]
            group_name = privilege["groupLabel"]
            if group_name not in role_json["privileges"]:
                role_json["privileges"][group_name] = []
            role_json["privileges"][group_name].append(priv_name)
        roles_config.append(role_json)

    return roles_config


def save(role_config, service_instance=None, profile=None):
    """
    Create new role with given configuration, if it doesn't exist.
    Otherwise update existing role.
    Apply changes only for particular group from configuration.
    Roles outside the groups mentioned in configuration are kept unchanged.

    role_config
        Role name and configuration values.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: json
    {
        "role": "SRM Administrator",
        "privileges": {
            "Protection Group": [
                "Assign to plan",
                "Create",
                "Modify",
                "Remove",
                "Remove from plan"
            ],
            "Recovery Plan": [
                "Configure commands",
                "Create",
                "Remove",
                "Modify",
                "Recovery"
            ]
        }
    }
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )

    authorizationManager = service_instance.RetrieveContent().authorizationManager

    privileges_desc = {}
    privilege_groups_desc = {}
    for desciption in authorizationManager.description.privilege:
        privileges_desc[desciption.key] = {"label": desciption.label, "summary": desciption.summary}
    for desciption in authorizationManager.description.privilegeGroup:
        privilege_groups_desc[desciption.key] = {
            "label": desciption.label,
            "summary": desciption.summary,
        }

    # Collect privilages by group label and privilege name
    group_privileges = {}
    privilege_group_map = {}
    for privilege in authorizationManager.privilegeList:
        desciption_group = privilege_groups_desc[privilege.privGroupName]
        group_label = desciption_group["label"]
        if group_label not in group_privileges:
            group_privileges[group_label] = []
        group_privileges[group_label].append(privilege)
        privilege_group_map[privilege.privId] = group_label

    role_name = role_config["role"]

    # find role to store or update
    role = None
    for role_obj in authorizationManager.roleList:
        if role_obj.info.label == role_name:
            role = role_obj
            break

    # group new privileges
    new_privileges_by_groups = {}
    for group in role_config["privileges"]:
        if group not in new_privileges_by_groups:
            new_privileges_by_groups[group] = []
        privileges_in_group = role_config["privileges"][group]
        for priv in group_privileges[group]:
            priv_label = privileges_desc[priv.privId]["label"]
            if priv_label in privileges_in_group:
                # collect new privileges
                new_privileges_by_groups[group].append(priv.privId)

    # Create if role doesn't exist
    if role is None:
        if not role_name:
            raise salt.exceptions.CommandExecutionError(f"Role name is required!")

        log.debug("")
        log.debug("*********************************")
        log.debug("Create Role: " + role_name)
        log.debug("")

        role_privileges = []
        for group in new_privileges_by_groups:
            role_privileges += new_privileges_by_groups[group]

        log.debug("Privileges:")
        log.debug(json.dumps(list(role_privileges), indent=2))

        authorizationManager.AddAuthorizationRole(role_name, role_privileges)
        log.debug("*********************************")

        return {"status": "created"}
    else:
        # otherwise update existing role
        # apply changes only for particular group from configuration
        # roles outside the groups mentioned in configuration are kept unchanged

        role_privileges = []
        old_privileges_by_groups = {}
        for priv_name in role.privilege:
            role_privileges.append(priv_name)
            if priv_name in privilege_group_map:
                group = privilege_group_map[priv_name]
                if group not in old_privileges_by_groups:
                    old_privileges_by_groups[group] = []
                # collect current privileges
                old_privileges_by_groups[group].append(priv_name)

        log.debug("")
        log.debug("*********************************")
        log.debug("Update Role: " + role_name)
        log.debug("")
        add_privileges = []
        remove_priviliges = []
        for group in new_privileges_by_groups:
            if group in old_privileges_by_groups:
                # merge group privileges
                add_privileges += set(new_privileges_by_groups[group]).difference(
                    old_privileges_by_groups[group]
                )
                remove_priviliges += set(old_privileges_by_groups[group]).difference(
                    new_privileges_by_groups[group]
                )
            else:
                # add new group with privileges
                add_privileges += new_privileges_by_groups[group]

        log.debug("Add privileges:")
        log.debug(json.dumps(list(add_privileges), indent=2))
        log.debug("Remove privileges:")
        log.debug(json.dumps(list(remove_priviliges), indent=2))
        log.debug("---------------------------")

        # remove privileges from role
        for priv in remove_priviliges:
            role_privileges.remove(priv)

        # add privileges to role
        for priv in add_privileges:
            role_privileges.append(priv)

        log.debug("Final privileges:")
        log.debug(json.dumps(list(role_privileges), indent=2))

        authorizationManager.UpdateAuthorizationRole(role.roleId, role.name, role_privileges)
        log.debug("*********************************")

        return {"status": "updated"}
