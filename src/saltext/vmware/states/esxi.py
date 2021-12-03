# SPDX-License-Identifier: Apache-2.0
import logging

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
    Add local user on matching ESXi hosts.

    name
        User to create on matching ESXi hosts. (required).

    password
        Password for the user. (required).

    description
        Description of the user. (optional).

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
    diff = {}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    user = __salt__["vmware_esxi.get_user"](
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
        if host in user:
            # Cannot determine if password is changed. So, when the user is found on the host, update it.
            diff[host] = {
                "old": {"name": name, "description": user[host][name]["description"]},
                "new": {"name": name, "description": description},
                "action": "update",
            }
            update += 1
        else:
            diff[host] = {"new": {"name": name, "description": description}, "action": "create"}
            create += 1
    for host in diff:
        if __opts__["test"]:
            ret[
                "comment"
            ] = "User {} will be created on {} host(s) and updated on {} host(s).".format(
                name, create, update
            )
            ret["result"] = None
        elif diff[host]["action"] == "update":
            __salt__["vmware_esxi.update_user"](
                user_name=name,
                password=password,
                description=description,
                datacenter_name=datacenter_name,
                cluster_name=cluster_name,
                host_name=host,
                service_instance=service_instance,
            )
            ret["comment"] = "User {} created on {} host(s) and updated on {} host(s).".format(
                name, create, update
            )
            ret["changes"] = diff
            ret["result"] = True
        else:
            __salt__["vmware_esxi.add_user"](
                user_name=name,
                password=password,
                description=description,
                datacenter_name=datacenter_name,
                cluster_name=cluster_name,
                host_name=host,
                service_instance=service_instance,
            )
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
    Remove local user on matching ESXi hosts.

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
    delete = 0
    diff = {}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    user = __salt__["vmware_esxi.get_user"](
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
        if host in user:
            delete += 1
            diff[host] = {name: True}
        else:
            diff[host] = {name: False}

    for host in diff:
        if __opts__["test"]:
            ret["comment"] = "User {} will be deleted on {} host(s).".format(name, delete)
            ret["result"] = None
        elif diff[host][name]:
            __salt__["vmware_esxi.remove_user"](
                user_name=name,
                datacenter_name=datacenter_name,
                cluster_name=cluster_name,
                host_name=host,
                service_instance=service_instance,
            )
            ret["comment"] = "User {} removed on {} host(s).".format(name, delete)
            ret["changes"] = diff
            ret["result"] = True
        else:
            ret["comment"] = "User {} doesn't exist on {} host(s).".format(name, delete)
            ret["result"] = None
    return ret
