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
        if role_name is not None and role_name != role.name:
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

    return result


def save(role_config, service_instance=None, profile=None):
    """
    Update role with given configuration.

    role_config
        Role name and configuration values.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )

    authorizationManager = service_instance.RetrieveContent().authorizationManager

    privilege_groups_desc = {}
    for desciption in authorizationManager.description.privilegeGroup:
        privilege_groups_desc[desciption.key] = {
            "label": desciption.label,
            "summary": desciption.summary,
        }

    # Collect privilages by group label and privilege name
    privilege_groups = {}
    for privilege in authorizationManager.privilegeList:
        desciption_group = privilege_groups_desc[privilege.privGroupName]
        group_label = desciption_group["label"]
        if group_label not in privilege_groups:
            privilege_groups[group_label] = []
        privilege_groups[group_label].append(privilege)

    role_name = role_config["role"]

    # find role to store or update
    role = None
    for role_obj in authorizationManager.roleList:
        if role_obj.info.label == role_name:
            role = role_obj
            break

    # Create if role doesn't exist
    if role is None:
        if not role_name:
            raise salt.exceptions.CommandExecutionError(f"Role name is required!")

        return {"status": "created"}
    else:
        # otherwise update existing role
        print(role)

        new_privileges = []
        for group in role_config["privileges"]:
            for priv in privilege_groups[group]:
                new_privileges.append(priv.name)

        print("New:::::")
        print(new_privileges)

        old_privileges = []
        for priv_name in role.privileges:
            for priv in privilege_groups[group]:
                old_privileges.append(priv.name)

        print(new_privileges)

        return {"status": "updated"}
