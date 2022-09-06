# SPDX-License-Identifier: Apache-2.0
import functools
import logging
from bisect import bisect_right

import salt
import saltext.vmware.utils.esxi as utils_esxi
from saltext.vmware.utils.connect import get_service_instance

log = logging.getLogger(__name__)

try:
    import pyVmomi
    from pyVmomi import vmodl, vim, VmomiSupport

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
            name, ",".join(sorted(new_privs)) or "No", ",".join(sorted(del_privs)) or "No"
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


def vmkernel_adapter_present(
    name,
    port_group_name,
    dvswitch_name=None,
    vswitch_name=None,
    enable_fault_tolerance=None,
    enable_management_traffic=None,
    enable_provisioning=None,
    enable_replication=None,
    enable_replication_nfc=None,
    enable_vmotion=None,
    enable_vsan=None,
    mtu=1500,
    network_default_gateway=None,
    network_ip_address=None,
    network_subnet_mask=None,
    network_tcp_ip_stack="default",
    network_type="static",
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
):
    """
    Ensure VMKernel Adapter exists on matching ESXi hosts.

    name
        The name of the VMKernel interface to update. (required).

    port_group_name
        The name of the port group for the VMKernel interface. (required).

    dvswitch_name
        The name of the vSphere Distributed Switch (vDS) where to update the VMKernel interface.

    vswitch_name
        The name of the vSwitch where to update the VMKernel interface.

    enable_fault_tolerance
        Enable Fault Tolerance traffic on the VMKernel adapter. Valid values: True, False.

    enable_management_traffic
        Enable Management traffic on the VMKernel adapter. Valid values: True, False.

    enable_provisioning
        Enable Provisioning traffic on the VMKernel adapter. Valid values: True, False.

    enable_replication
        Enable vSphere Replication traffic on the VMKernel adapter. Valid values: True, False.

    enable_replication_nfc
        Enable vSphere Replication NFC traffic on the VMKernel adapter. Valid values: True, False.

    enable_vmotion
        Enable vMotion traffic on the VMKernel adapter. Valid values: True, False.

    enable_vsan
        Enable VSAN traffic on the VMKernel adapter. Valid values: True, False.

    mtu
        The MTU for the VMKernel interface.

    network_default_gateway
        Default gateway (Override default gateway for this adapter).

    network_type
        Type of IP assignment. Valid values: "static", "dhcp".

    network_ip_address
        Static IP address. Required if type = 'static'.

    network_subnet_mask
        Static netmask required. Required if type = 'static'.

    network_tcp_ip_stack
        The TCP/IP stack for the VMKernel interface. Valid values: "default", "provisioning", "vmotion", "vxlan".

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: yaml

        Save Adapter:
          vmware_esxi.vmkernel_adapter_present:
            - name: vmk1
            - port_group_name: portgroup1
            - dvsswitch_name: vswitch1
    """
    log.debug("Running vmware_esxi.vmkernel_adapter_present")
    ret = {"name": name, "result": None, "comment": "", "changes": {}}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    adapters = __salt__["vmware_esxi.get_vmkernel_adapters"](
        adapter_name=name,
        datacenter_name=datacenter_name,
        cluster_name=cluster_name,
        host_name=host_name,
        service_instance=service_instance,
    )
    add_on_hosts = []
    update_on_hosts = []
    for h in hosts:
        if name and adapters[h.name] and name in adapters[h.name]:
            update_on_hosts.append(h.name)
        else:
            add_on_hosts.append(h.name)

    if __opts__["test"]:
        ret[
            "comment"
        ] = "vmkernel adapter {!r} will be created on {} host(s) and updated on {} host(s).".format(
            name, len(add_on_hosts), len(update_on_hosts)
        )
        ret["result"] = None
    elif not add_on_hosts and not update_on_hosts:
        ret[
            "comment"
        ] = "vmkernel adapter {!r} not created/updated on any host. No changes made.".format(name)
        ret["result"] = True
    else:
        hosts_in_error = []
        sample_exception = None
        for action, hosts in [("add", add_on_hosts), ("update", update_on_hosts)]:
            for host in hosts:
                try:
                    func = None
                    if action == "add":
                        func = functools.partial(__salt__["vmware_esxi.create_vmkernel_adapter"])
                    else:
                        func = functools.partial(
                            __salt__["vmware_esxi.update_vmkernel_adapter"], adapter_name=name
                        )
                    ret_save = func(
                        port_group_name=port_group_name,
                        dvswitch_name=dvswitch_name,
                        vswitch_name=vswitch_name,
                        enable_fault_tolerance=enable_fault_tolerance,
                        enable_management_traffic=enable_management_traffic,
                        enable_provisioning=enable_provisioning,
                        enable_replication=enable_replication,
                        enable_replication_nfc=enable_replication_nfc,
                        enable_vmotion=enable_vmotion,
                        enable_vsan=enable_vsan,
                        mtu=mtu,
                        network_default_gateway=network_default_gateway,
                        network_ip_address=network_ip_address,
                        network_subnet_mask=network_subnet_mask,
                        network_tcp_ip_stack=network_tcp_ip_stack,
                        network_type=network_type,
                        datacenter_name=datacenter_name,
                        cluster_name=cluster_name,
                        host_name=host,
                        service_instance=service_instance,
                    )
                    ret["changes"].update(ret_save)
                except salt.exceptions.SaltException as exc:
                    hosts_in_error.append(host)
                    sample_exception = str(exc)
        ret["comment"] = "vmkernel adapter {!r} created on {}, updated on {}.".format(
            name,
            ",".join(sorted(set(add_on_hosts) - set(hosts_in_error))) or "-",
            ",".join(sorted(set(update_on_hosts) - set(hosts_in_error))) or "-",
        )
        ret["result"] = True
        if hosts_in_error:
            ret["comment"] += "erred on {}. Sample exception - {}".format(
                ",".join(sorted(hosts_in_error)), sample_exception
            )
            ret["result"] = False
    return ret


def vmkernel_adapter_absent(
    name, datacenter_name=None, cluster_name=None, host_name=None, service_instance=None
):
    """
    Ensure VMKernel Adapter exists on matching ESXi hosts.

    name
        The name of the VMKernel interface to update. (required).

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: yaml

        Delete Adapter:
          vmware_esxi.vmkernel_adapter_absent:
            - name: vmk1
    """
    log.debug("Running vmware_esxi.vmkernel_adapter_absent")
    ret = {"name": name, "result": None, "comment": "", "changes": {}}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    adapters = __salt__["vmware_esxi.get_vmkernel_adapters"](
        adapter_name=name,
        datacenter_name=datacenter_name,
        cluster_name=cluster_name,
        host_name=host_name,
        service_instance=service_instance,
    )
    delete_on_hosts = [h.name for h in hosts if adapters[h.name]]
    if __opts__["test"]:
        ret["comment"] = "vmkernel adapter {!r} will be deleted on {} host(s).".format(
            name, len(delete_on_hosts)
        )
        ret["result"] = None
    elif not delete_on_hosts:
        ret["comment"] = "vmkernel adapter {!r} absent on all hosts. No changes made.".format(name)
    else:
        hosts_in_error = []
        sample_exception = None
        for host in delete_on_hosts:
            try:
                ret_delete = __salt__["vmware_esxi.delete_vmkernel_adapter"](
                    adapter_name=name,
                    datacenter_name=datacenter_name,
                    cluster_name=cluster_name,
                    host_name=host,
                    service_instance=service_instance,
                )
                ret["changes"].update(ret_delete)
            except salt.exceptions.SaltException as exc:
                hosts_in_error.append(host)
                sample_exception = str(exc)
        ret["comment"] = "vmkernel adapter {!r} deleted on {}.".format(
            name, ",".join(sorted(set(delete_on_hosts) - set(hosts_in_error)))
        )
        ret["result"] = True
        if hosts_in_error:
            ret["comment"] += "erred on {}. Sample exception - {}".format(
                ",".join(sorted(hosts_in_error)), sample_exception
            )
            ret["result"] = False
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
                    name, create, update, len(failed_hosts), ",".join(sorted(failed_hosts)), exc
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
                    name, create, update, len(failed_hosts), ",".join(sorted(failed_hosts)), exc
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
                    name, delete, len(failed_hosts), ",".join(sorted(failed_hosts)), exc
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


def maintenance_mode(
    name,
    enter_maintenance_mode,
    timeout=0,
    evacuate_powered_off_vms=False,
    maintenance_spec=None,
    service_instance=None,
):
    """
    Put host into or out of maintenance mode.

    name
        Host IP or HostSystem/ManagedObjectReference (required).

    enter_maintenance_mode
        If True, put host into maintenance mode.
        If False, put host out of maintenance mode.

    timeout
        If value is greater than 0 then task will timeout if not completed with in window (optional).

    evacuate_powered_off_vms
        Only supported by VirtualCenter (optional).
         If True, for DRS will fail unless all powered-off VMs have been manually registered.
         If False, task will successed with powered-off VMs.
         Only relevant if enter_maintenance_mode must be True.

    maintenance_spec
        HostMaintenanceSpec (optional).
         Only relevant if enter_maintenance_mode must be True.

    service_instance
        Use this vCenter service connection instance instead of creating a new one (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.maintenance_mode '192.0.2.117'
    .. code-block:: yaml

        Maintenance Mode:
          vmware_esxi.maintenance_mode:
            - host: '192.0.2.117'
            - enter_maintenance_mode: true
    """
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}

    # check that host is not all ready in maintenance state.
    host_state = __salt__["vmware_esxi.in_maintenance_mode"](
        host=name, service_instance=service_instance
    )
    if (host_state["maintenanceMode"] == "inMaintenance") == enter_maintenance_mode:
        ret["comment"] = f"Already in {'Maintenance' if enter_maintenance_mode else 'Normal'} mode."
        return ret

    if __opts__["test"]:
        ret["result"] = None
        ret["changes"] = {
            "new": f"Host will enter {'Maintenance' if enter_maintenance_mode else 'Normal'} mode."
        }
        ret["comment"] = "These options are set to change."
        return ret

    if enter_maintenance_mode:
        host_state = __salt__["vmware_esxi.maintenance_mode"](
            host=name,
            timeout=timeout,
            evacuate_powered_off_vms=evacuate_powered_off_vms,
            maintenance_spec=maintenance_spec,
            catch_task_error=True,
            service_instance=service_instance,
        )
    else:
        host_state = __salt__["vmware_esxi.exit_maintenance_mode"](
            host=name, timeout=timeout, catch_task_error=True, service_instance=service_instance
        )

    ret["result"] = (host_state["maintenanceMode"] == "inMaintenance") == enter_maintenance_mode
    if ret["result"]:
        ret["changes"] = {
            "new": f"Host entered {'Maintenance' if enter_maintenance_mode else 'Normal'} mode."
        }
    else:
        ret[
            "comment"
        ] = f"Failed to put host {str(name)} in {'Maintenance' if enter_maintenance_mode else 'Normal'} mode."
    return ret


def lockdown_mode(
    name,
    enter_lockdown_mode,
    datacenter_name=None,
    cluster_name=None,
    get_all_hosts=False,
    service_instance=None,
):
    """
    Pust a hosts into or out of lockdown.

    name
        IP of single host or list of host_names. If wanting to get a cluster just past an empty list (required).

    enter_lockdown_mode
        If True, put host into lockdown mode.
        If False, put host out of lockdown mode (required)

    datacenter_name
        The datacenter name. Default is None (optional).

    host_names
        The host_names to be retrieved. Default is None (optional).

    cluster_name
        The cluster name - used to restrict the hosts retrieved. Only used if
        the datacenter is set.  This argument is optional (optional).

    get_all_hosts
        Specifies whether to retrieve all hosts in the container.
        Default value is False (optional).

    service_instance
        The Service Instance Object from which to obtain the hosts (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.lockdown_mode '192.0.2.117'
    .. code-block:: yaml

        Lockdown Mode:
          vmware_esxi.lockdown_mode:
            - host: '192.0.2.117'
            - enter_lockdown_mode: true
    """
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}
    if not isinstance(name, str):
        host_refs = utils_esxi.get_hosts(
            service_instance=service_instance,
            datacenter_name=datacenter_name,
            host_names=name,
            cluster_name=cluster_name,
            get_all_hosts=get_all_hosts,
        )
    else:
        if isinstance(name, vim.HostSystem):
            host_refs = (name,)
        else:
            if service_instance is None:
                service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
            host_refs = (utils_esxi.get_host(name, service_instance),)

    for ref in host_refs:
        # check that host is not all ready in lock state.
        host_state = __salt__["vmware_esxi.in_lockdown_mode"](
            host=ref, service_instance=service_instance
        )
        if (host_state["lockdownMode"] == "inLockdown") == enter_lockdown_mode:
            ret[
                "comment"
            ] += f"{ref.name} already in {'Lockdown' if enter_lockdown_mode else 'Normal'} mode.\n"
            continue

        if __opts__["test"]:
            ret["result"] = None
            ret["changes"].setdefault("new", []).append(
                f"{ref.name} will enter {'Lockdown' if enter_lockdown_mode else 'Normal'} mode."
            )
            continue

        if enter_lockdown_mode:
            host_state = __salt__["vmware_esxi.lockdown_mode"](
                host=ref,
                catch_task_error=True,
                service_instance=service_instance,
            )
        else:
            host_state = __salt__["vmware_esxi.exit_lockdown_mode"](
                host=ref, catch_task_error=True, service_instance=service_instance
            )
        ref_results = (host_state["lockdownMode"] == "inLockdown") == enter_lockdown_mode
        if ret["result"]:
            ret["result"] = ref_results
        if ref_results:
            ret["changes"].setdefault("new", []).append(
                f"{ref.name} entered {'Lockdown' if enter_lockdown_mode else 'Normal'} mode."
            )
        else:
            ret[
                "comment"
            ] += f"Failed to put host {ref.name} in {'Lockdown' if enter_lockdown_mode else 'Normal'} mode.\n"
    if ret["result"]:
        ret["comment"] += f"Task was successfully!\n"
    elif ret["result"] is None:
        ret["comment"] += "These options are set to change."
    return ret


def advanced_config(
    name,
    value,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
):
    """
    Set advanced configuration on matching ESXi hosts.

    name
        Name of configuration on matching ESXi hosts. (required).

    value
        Value for configuration on matching ESXi hosts. (required).

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
          vmware_esxi.advanced_configs:
            - name: Annotations.WelcomeMessage
            - value: Hello

    """
    log.debug("Running vmware_esxi.advanced_config")
    ret = {"name": name, "result": None, "comment": "", "changes": {}}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)

    esxi_config_old = __salt__["vmware_esxi.get_advanced_config"](
        config_name=name,
        datacenter_name=datacenter_name,
        cluster_name=cluster_name,
        host_name=host_name,
        service_instance=service_instance,
    )
    if __opts__["test"]:
        ret["result"] = None
        ret["changes"] = {"new": {}}
        for host in esxi_config_old:
            ret["changes"]["new"][host] = f"{name} will be set to {value}"
        ret["comment"] = "These options are set to change."
        return ret

    ret["result"] = True
    ret["changes"] = {"new": {}, "old": {}}
    change = False
    for host in esxi_config_old:
        if esxi_config_old[host][name] != value:
            change = True
            config = __salt__["vmware_esxi.set_advanced_configs"](
                config_dict={name: value},
                datacenter_name=datacenter_name,
                cluster_name=cluster_name,
                host_name=host,
                service_instance=service_instance,
            )
            ret["changes"]["old"][host] = f"{name} was {esxi_config_old[host][name]}"
            ret["changes"]["new"][host] = f"{name} was changed to {config[host][name]}"

    if change:
        ret["comment"] = "Configurations have successfully been changed."
    else:
        ret["comment"] = "Configurations are already in correct state."
    return ret


def firewall_config(
    name,
    value,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
):
    """
    Set firewall configuration on matching ESXi hosts.

    name
        Name of configuration in value. (required).

    value
        Value for configuration on matching ESXi hosts. (required).

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: yaml

        Set firewall config:
          vmware_esxi.firewall_config:
            - name: prod
    """
    log.debug("Running vmware_esxi.firewall_config")
    ret = {"name": name, "result": None, "comment": "", "changes": {}}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)

    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )
    if isinstance(value[name], list):
        for i in range(len(value[name])):
            value[name][i] = dict(value[name][i])
            if "allowed_host" in value[name][i]:
                value[name][i]["allowed_host"] = dict(value[name][i]["allowed_host"])
    old_configs = {}
    for host in hosts:
        for firewall_conf in value[name]:
            if host.name in old_configs:
                fw_config = utils_esxi.get_firewall_config(
                    ruleset_name=firewall_conf["name"],
                    host_name=host.name,
                    service_instance=service_instance,
                )
                old_configs[host.name][firewall_conf["name"]] = fw_config[host.name][
                    firewall_conf["name"]
                ]
            else:
                fw_config = utils_esxi.get_firewall_config(
                    ruleset_name=firewall_conf["name"],
                    host_name=host.name,
                    service_instance=service_instance,
                )
                old_configs[host.name] = {}
                old_configs[host.name][firewall_conf["name"]] = fw_config[host.name][
                    firewall_conf["name"]
                ]

    if __opts__["test"]:
        ret["result"] = None
        ret["changes"] = {}
        for host in hosts:
            ret["changes"][host.name] = {}
            for firewall_config in value[name]:
                ret["changes"][host.name][firewall_config["name"]] = {}
                for k in firewall_conf:
                    if k == "name":
                        continue
                    elif k == "allowed_host":
                        for j in firewall_conf[k]:
                            if (
                                old_configs[host.name][firewall_config["name"]][k][j]
                                == firewall_conf[k][j]
                            ):
                                ret["changes"][host.name][firewall_config["name"]][
                                    j
                                ] = f"{j} is already set to {firewall_conf[k][j]}"
                            else:
                                ret["changes"][host.name][firewall_config["name"]][
                                    j
                                ] = f"{j} will be set to {firewall_conf[k][j]}"
                    else:
                        if old_configs[host.name][firewall_config["name"]][k] == firewall_conf[k]:
                            ret["changes"][host.name][firewall_config["name"]][
                                k
                            ] = f"{k} is already set to {firewall_conf[k]}"
                        else:
                            ret["changes"][host.name][firewall_config["name"]][
                                k
                            ] = f"{k} will be set to {firewall_conf[k]}"
        ret["comment"] = "These options are set to change."
        return ret

    ret["result"] = True
    ret["changes"] = {"new": {}, "old": {}}
    ret["comment"] = "Configurations are already in correct state."
    for host in hosts:
        ret["changes"]["new"][host.name] = {}
        ret["changes"]["old"][host.name] = {}
        for firewall_config in value[name]:
            change = False
            ret["changes"]["new"][host.name][firewall_config["name"]] = {}
            ret["changes"]["old"][host.name][firewall_config["name"]] = {}
            for k in firewall_conf:
                if k == "name":
                    continue
                ret["changes"]["new"][host.name][firewall_config["name"]][k] = {}
                ret["changes"]["old"][host.name][firewall_config["name"]][k] = {}
                if k == "allowed_host":
                    for j in firewall_conf[k]:
                        if (
                            old_configs[host.name][firewall_config["name"]][k][j]
                            != firewall_conf[k][j]
                        ):
                            change = True
                            ret["changes"]["new"][host.name][firewall_config["name"]][k][
                                j
                            ] = firewall_conf[k][j]
                            ret["changes"]["old"][host.name][firewall_config["name"]][k][
                                j
                            ] = old_configs[host.name][firewall_config["name"]][k][j]
                else:
                    if old_configs[host.name][firewall_config["name"]][k] != firewall_conf[k]:
                        change = True
                        ret["changes"]["new"][host.name][firewall_config["name"]][
                            k
                        ] = firewall_conf[k]
                        ret["changes"]["old"][host.name][firewall_config["name"]][k] = old_configs[
                            host.name
                        ][firewall_config["name"]][k]
            if change:
                __salt__["vmware_esxi.set_firewall_config"](
                    firewall_config=firewall_config,
                    host_name=host.name,
                    service_instance=service_instance,
                )
                ret["comment"] = "Configurations have successfully been changed."

    return ret
