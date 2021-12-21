# SPDX-License-Identifier: Apache-2.0
import logging

import salt
from saltext.vmware.utils.connect import get_service_instance


log = logging.getLogger(__name__)

try:
    import pyVmomi

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_esxi"
__proxyenabled__ = ["vmware_esxi"]


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def role_present(
    name,
    privilege_ids,
    esxi_host_name=None,
    service_instance=None,
):
    """
    Ensure role is present on service instance, which may be an ESXi host or vCenter instance.

    role_name
        Role to create/update on service instance. (required).

    privilege_ids
        List of privileges for the role. (required).
        Refer: https://docs.vmware.com/en/VMware-vSphere/7.0/com.vmware.vsphere.security.doc/GUID-ED56F3C4-77D0-49E3-88B6-B99B8B437B62.html
        Example: ['Folder.Create', 'Folder.Delete'].

    esxi_host_name
        Connect to this ESXi host using your pillar's service_instance credentials. (optional).

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    """
    log.debug("Running vmware_esxi.role_present")
    ret = {"name": name, "result": None, "comment": "", "changes": {}}
    if not service_instance:
        service_instance = get_service_instance(
            opts=__opts__,
            pillar=__pillar__,
            esxi_host=esxi_host_name,
        )
    role = __salt__["vmware_esxi.get_role"](role_name=name, service_instance=service_instance)
    sys_privs = {"System.Anonymous", "System.Read", "System.View"}
    del_privs = list(set(role.get("privilege_ids", [])) - sys_privs - set(privilege_ids))
    new_privs = list(set(privilege_ids) - set(role.get("privilege_ids", [])) - sys_privs)
    changes = {
        "new": {
            "role_id": role.get("role_id"),
            "role_name": name,
            "privilege_ids": {
                "added": new_privs,
                "removed": del_privs,
                "current": sorted(list(set(privilege_ids) | sys_privs)),
            },
        },
        "old": role,
    }
    if not role:
        if __opts__["test"]:
            ret["comment"] = "Role {} will be created.".format(name)
            ret["result"] = None
        else:
            role = __salt__["vmware_esxi.add_role"](
                role_name=name, privilege_ids=privilege_ids, service_instance=service_instance
            )
            changes["new"]["role_id"] = role["role_id"]
            ret["comment"] = "Role {} created.".format(name)
            ret["result"] = True
            ret["changes"] = changes
    elif not new_privs and not del_privs:
        ret["comment"] = "Role {} is in the correct state".format(name)
        ret["result"] = None
    elif __opts__["test"]:
        ret[
            "comment"
        ] = "Role {} will be updated. {} privileges will be added. {} privileges will be removed.".format(
            name, ",".join(new_privs) or "No", ",".join(del_privs) or "No"
        )
        ret["result"] = None
    else:
        __salt__["vmware_esxi.update_role"](
            role_name=name, privilege_ids=privilege_ids, service_instance=service_instance
        )
        ret["comment"] = "Role {} updated.".format(name)
        ret["result"] = True
        ret["changes"] = changes
    return ret


def role_absent(
    name,
    esxi_host_name=None,
    service_instance=None,
):
    """
    Ensure role is absent on service instance, which may be an ESXi host or vCenter instance.

    role_name
        Role to delete on service instance. (required).

    esxi_host_name
        Connect to this ESXi host using your pillar's service_instance credentials. (optional).

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    """
    log.debug("Running vmware_esxi.role_absent")
    ret = {"name": name, "result": None, "comment": "", "changes": {}}
    if not service_instance:
        service_instance = get_service_instance(
            opts=__opts__,
            pillar=__pillar__,
            esxi_host=esxi_host_name,
        )
    role = __salt__["vmware_esxi.get_role"](role_name=name, service_instance=service_instance)
    if not role:
        ret["comment"] = "Role {} is not present.".format(name)
        ret["result"] = None
    elif __opts__["test"]:
        ret["comment"] = "Role {} will be deleted.".format(name)
        ret["result"] = None
    else:
        __salt__["vmware_esxi.remove_role"](role_name=name, service_instance=service_instance)
        ret["comment"] = "Role {} deleted.".format(name)
        ret["result"] = True
    return ret


def user_present(
    name,
    password,
    description=None,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
):
    """
    Add local users_by_host on matching ESXi hosts.

    name
        User to create on matching ESXi hosts. (required).

    password
        Password for the users_by_host. (required).

    description
        Description of the users_by_host. (optional).

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: yaml

    Create User:
      vmware_esxi.user_present:
        - name: local_user
        - password: secret

    """
    log.debug("Running vmware_esxi.user_present")
    ret = {"name": name, "result": None, "comment": "", "changes": {}}
    create = update = 0
    failed_hosts = []
    diff = {}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    users_by_host = __salt__["vmware_esxi.get_user"](
        user_name=name,
        datacenter_name=datacenter_name,
        cluster_name=cluster_name,
        host_name=host_name,
        service_instance=service_instance,
    )
    hosts = __salt__["vmware_esxi.list_hosts"](
        datacenter_name=datacenter_name,
        cluster_name=cluster_name,
        host_name=host_name,
        service_instance=service_instance,
    )
    for host in hosts:
        if host in users_by_host:
            # Cannot determine if password is changed. So, when the users_by_host is found on the host, update it.
            diff[host] = {
                "old": {"name": name, "description": users_by_host[host][name]["description"]},
                "new": {"name": name, "description": description},
                "action": "update",
            }
            update += 1
        else:
            diff[host] = {"new": {"name": name, "description": description}, "action": "create"}
            create += 1
    for host in diff.copy():
        if __opts__["test"]:
            ret[
                "comment"
            ] = "User {} will be created on {} host(s) and updated on {} host(s).".format(
                name, create, update
            )
            ret["result"] = None
        elif diff[host]["action"] == "update":
            try:
                __salt__["vmware_esxi.update_user"](
                    user_name=name,
                    password=password,
                    description=description,
                    datacenter_name=datacenter_name,
                    cluster_name=cluster_name,
                    host_name=host,
                    service_instance=service_instance,
                )
            except salt.exceptions.SaltException as exc:
                update -= 1
                failed_hosts.append(host)
                diff.pop(host)
                ret[
                    "comment"
                ] = "User {} created on {} host(s), updated on {} host(s), failed on {} host(s). List of failed host(s) - {}. Sample Error: {}".format(
                    name, create, update, len(failed_hosts), ",".join(failed_hosts), exc
                )
                ret["changes"] = diff
                ret["result"] = False
            if not ret["comment"]:
                ret["comment"] = "User {} created on {} host(s) and updated on {} host(s).".format(
                    name, create, update
                )
                ret["changes"] = diff
                ret["result"] = True
        else:
            try:
                __salt__["vmware_esxi.add_user"](
                    user_name=name,
                    password=password,
                    description=description,
                    datacenter_name=datacenter_name,
                    cluster_name=cluster_name,
                    host_name=host,
                    service_instance=service_instance,
                )
            except salt.exceptions.SaltException as exc:
                create -= 1
                failed_hosts.append(host)
                diff.pop(host)
                ret[
                    "comment"
                ] = "User {} created on {} host(s), updated on {} host(s), failed on {} host(s). List of failed host(s) - {}. Sample Error: {}".format(
                    name, create, update, len(failed_hosts), ",".join(failed_hosts), exc
                )
                ret["changes"] = diff
                ret["result"] = False
            if not ret["comment"]:
                ret["comment"] = "User {} created on {} host(s) and updated on {} host(s).".format(
                    name, create, update
                )
                ret["changes"] = diff
                ret["result"] = True
    return ret


def user_absent(
    name,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
):
    """
    Remove local users_by_host on matching ESXi hosts.

    name
        User to create on matching ESXi hosts. (required).

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: yaml

    Remove User:
      vmware_esxi.user_absent:
        - name: local_user

    """
    log.debug("Running vmware_esxi.user_absent")
    ret = {"name": name, "result": None, "comment": "", "changes": {}}
    delete = no_user = 0
    failed_hosts = []
    diff = {}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    users_by_host = __salt__["vmware_esxi.get_user"](
        user_name=name,
        datacenter_name=datacenter_name,
        cluster_name=cluster_name,
        host_name=host_name,
        service_instance=service_instance,
    )
    hosts = __salt__["vmware_esxi.list_hosts"](
        datacenter_name=datacenter_name,
        cluster_name=cluster_name,
        host_name=host_name,
        service_instance=service_instance,
    )
    for host in hosts:
        if host in users_by_host:
            delete += 1
            diff[host] = {name: True}
        else:
            no_user += 1
            diff[host] = {name: False}

    for host in diff.copy():
        if __opts__["test"]:
            if not ret["comment"]:
                ret["comment"] = "User {} will be deleted on {} host(s).".format(name, delete)
                ret["result"] = None
        elif diff[host][name]:
            try:
                __salt__["vmware_esxi.remove_user"](
                    user_name=name,
                    datacenter_name=datacenter_name,
                    cluster_name=cluster_name,
                    host_name=host,
                    service_instance=service_instance,
                )
            except salt.exceptions.SaltException as exc:
                delete -= 1
                failed_hosts.append(host)
                diff.pop(host)
                ret[
                    "comment"
                ] = "User {} removed on {} host(s), failed on {} host(s). List of failed host(s) - {}. Sample Error: {}".format(
                    name, delete, len(failed_hosts), ",".join(failed_hosts), exc
                )
                ret["changes"] = diff
                ret["result"] = False
            if not ret["comment"]:
                ret["comment"] = "User {} removed on {} host(s).".format(name, delete)
                ret["changes"] = diff
                ret["result"] = True
    if not ret["comment"]:
        ret["comment"] = "User {} doesn't exist on {} host(s).".format(name, no_user)
        ret["result"] = None
    return ret
