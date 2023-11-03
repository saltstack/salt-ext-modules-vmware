# SPDX-License-Identifier: Apache-2.0
import functools
import json
import logging

import salt.exceptions
import salt.utils.data
import salt.utils.dictdiffer
import saltext.vmware.modules.esxi as vmware_esxi
import saltext.vmware.utils.connect as connect
import saltext.vmware.utils.drift as drift
import saltext.vmware.utils.esxi as utils_esxi

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


def role_present(name, privilege_ids, esxi_host_name=None, service_instance=None, profile=None):
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

    profile
        Profile to use (optional)

    """
    log.debug("Running vmware_esxi.role_present")
    ret = {"name": name, "result": None, "comment": "", "changes": {}}
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__,
        profile=profile,
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


def role_absent(name, esxi_host_name=None, service_instance=None, profile=None):
    """
    Ensure role is absent on service instance, which may be an ESXi host or vCenter instance.

    role_name
        Role to delete on service instance. (required).

    esxi_host_name
        Connect to this ESXi host using your pillar's service_instance credentials. (optional).

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    """
    log.debug("Running vmware_esxi.role_absent")
    ret = {"name": name, "result": None, "comment": "", "changes": {}}
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__,
        profile=profile,
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
    profile=None,
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

    profile
        Profile to use (optional)

    .. code-block:: yaml

        Save Adapter:
          vmware_esxi.vmkernel_adapter_present:
            - name: vmk1
            - port_group_name: portgroup1
            - dvsswitch_name: vswitch1
    """
    log.debug("Running vmware_esxi.vmkernel_adapter_present")
    ret = {"name": name, "result": None, "comment": "", "changes": {}}
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
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
                        profile=profile,
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
    name,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
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

    profile
        Profile to use (optional)

    .. code-block:: yaml

        Delete Adapter:
          vmware_esxi.vmkernel_adapter_absent:
            - name: vmk1
    """
    log.debug("Running vmware_esxi.vmkernel_adapter_absent")
    ret = {"name": name, "result": None, "comment": "", "changes": {}}
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
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
    profile=None,
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

    profile
        Profile to use (optional)

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
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
    users_by_host = __salt__["vmware_esxi.get_user"](
        user_name=name,
        datacenter_name=datacenter_name,
        cluster_name=cluster_name,
        host_name=host_name,
        service_instance=service_instance,
        profile=profile,
    )
    hosts = __salt__["vmware_esxi.list_hosts"](
        datacenter_name=datacenter_name,
        cluster_name=cluster_name,
        host_name=host_name,
        service_instance=service_instance,
        profile=profile,
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
                    profile=profile,
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
    profile=None,
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

    profile
        Profile to use (optional)

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
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )
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
    profile=None,
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
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

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
            service_instance = service_instance or connect.get_service_instance(
                config=__opts__, profile=profile
            )
            host_refs = (utils_esxi.get_host(name, service_instance),)

    for ref in host_refs:
        # check that host is not all ready in lock state.
        host_state = __salt__["vmware_esxi.in_lockdown_mode"](
            host=ref, service_instance=service_instance, profile=profile
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
                host=ref, catch_task_error=True, service_instance=service_instance, profile=profile
            )
        else:
            host_state = __salt__["vmware_esxi.exit_lockdown_mode"](
                host=ref, catch_task_error=True, service_instance=service_instance, profile=profile
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


def advanced_configs(
    name,
    configs,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Set advanced configuration on matching ESXi hosts.

    configs
        Set of key value pairs to be set on matching ESXi hosts (required)

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)


    .. code-block:: yaml

        ESXi_advanced_config_example:
          vmware_esxi.advanced_configs:
            - configs:
                DCUI.Access: root
                Net.BlockGuestBPDU: 1
    """
    log.debug("Running vmware_esxi.advanced_configs")
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )

    esxi_config_old = __salt__["vmware_esxi.get_advanced_config"](
        config_name="",
        datacenter_name=datacenter_name,
        cluster_name=cluster_name,
        host_name=host_name,
        service_instance=service_instance,
    )

    changes = {}

    for key in configs:
        for host in esxi_config_old:
            if key not in esxi_config_old[host]:
                return {
                    "name": name,
                    "result": False,
                    "comment": f"The config {key} does not exist on host {host}",
                    "changes": changes,
                }

    result = True
    comment = "Config already in correct state"
    for host in esxi_config_old:
        diff = salt.utils.data.recursive_diff(
            esxi_config_old[host], configs, ignore_missing_keys=True
        )
        if "new" in diff:
            changes[host] = diff
            if __opts__["test"]:
                if diff:
                    result = None
                    comment = "Changes would be made"
            else:
                config = __salt__["vmware_esxi.set_advanced_configs"](
                    config_dict=diff["new"],
                    datacenter_name=datacenter_name,
                    cluster_name=cluster_name,
                    host_name=host,
                    service_instance=service_instance,
                )
                comment = "Changes were made"
    return {"name": name, "result": result, "comment": comment, "changes": changes}


def firewall_config(
    name,
    value,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
    less=False,
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

    profile
        Profile to use (optional)

    less
        Default False. If this is set to True, only the changed values will be reported as changes.
    """
    log.debug("Running vmware_esxi.firewall_config")
    ret = {"name": name, "result": None, "comment": "", "changes": {}}
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )

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
            if "allowed_hosts" in value[name][i]:
                value[name][i]["allowed_hosts"] = dict(value[name][i]["allowed_hosts"])

    missing_rules = utils_esxi.get_missing_firewall_rules(value[name], hosts)

    if missing_rules:
        messages = [f"{r[0]} ruleset does not exist on ESXi server {r[1]}." for r in missing_rules]
        comment = "\n".join(messages)
        return {"name": name, "result": False, "comment": comment, "changes": {}}

    old_configs = {}
    for host in hosts:
        old_configs[host.name] = {}
        for ruleset in value[name]:
            rule = ruleset["name"]
            fw_config = utils_esxi.get_firewall_config(
                ruleset_name=rule,
                host_name=host.name,
                service_instance=service_instance,
            )
            old_configs[host.name][rule] = fw_config[host.name][rule]

    if __opts__["test"]:
        for host in hosts:
            ret["changes"][host.name] = {}
            for ruleset in value[name]:
                rule = ruleset["name"]
                ret["changes"][host.name][rule] = {}
                for k in ruleset:
                    if k == "name":
                        continue
                    elif k == "allowed_hosts":
                        for j in ruleset[k]:
                            if old_configs[host.name][rule][k][j] == ruleset[k][j]:
                                if not less:
                                    ret["changes"][host.name][rule][
                                        j
                                    ] = f"{j} is already set to {ruleset[k][j]}"
                            else:
                                if not less:
                                    ret["changes"][host.name][rule][
                                        j
                                    ] = f"{j} will be set to {ruleset[k][j]}"
                                else:
                                    ret["changes"][host.name][rule][j] = old_configs[host.name][
                                        rule
                                    ][k][j]
                    else:
                        if old_configs[host.name][rule][k] == ruleset[k]:
                            if not less:
                                ret["changes"][host.name][rule][
                                    k
                                ] = f"{k} is already set to {ruleset[k]}"
                        else:
                            if not less:
                                ret["changes"][host.name][rule][
                                    k
                                ] = f"{k} will be set to {ruleset[k]}"
                            else:
                                ret["changes"][host.name][rule][k] = old_configs[host.name][rule][k]
        ret["comment"] = "These options are set to change."
        return ret

    ret["result"] = True
    ret["changes"] = {"new": {}, "old": {}}
    ret["comment"] = "Configurations are already in correct state."
    for host in hosts:
        ret["changes"]["new"][host.name] = {}
        ret["changes"]["old"][host.name] = {}
        for ruleset in value[name]:
            rule = ruleset["name"]
            change = False
            ret["changes"]["new"][host.name][rule] = {}
            ret["changes"]["old"][host.name][rule] = {}
            for k in ruleset:
                if k == "name":
                    continue
                ret["changes"]["new"][host.name][rule][k] = {}
                ret["changes"]["old"][host.name][rule][k] = {}
                if k == "allowed_hosts":
                    for j in ruleset[k]:
                        if old_configs[host.name][rule][k][j] != ruleset[k][j]:
                            change = True
                            ret["changes"]["new"][host.name][rule][k][j] = ruleset[k][j]
                            ret["changes"]["old"][host.name][rule][k][j] = old_configs[host.name][
                                rule
                            ][k][j]
                else:
                    if old_configs[host.name][rule][k] != ruleset[k]:
                        change = True
                        ret["changes"]["new"][host.name][rule][k] = ruleset[k]
                        ret["changes"]["old"][host.name][rule][k] = old_configs[host.name][rule][k]
            if change:
                __salt__["vmware_esxi.set_firewall_config"](
                    firewall_config=ruleset,
                    host_name=host.name,
                    service_instance=service_instance,
                )
                ret["comment"] = "Configurations have successfully been changed."

    return ret


def ntp_config(
    name,
    service_running,
    ntp_servers=None,
    service_policy=None,
    service_restart=False,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Set ntp configuration on matching ESXi hosts.

    name
        Name of the state.

    service_running
        Ensures the running state of the ntp daemon for the host. Boolean value where
        ``True`` indicates that ntpd should be running and ``False`` indicates that it
        should be stopped.

    ntp_servers
        A list of servers that should be added to the ESXi host's NTP configuration.

    service_policy
        The policy to set for the NTP service.

        .. note::

            When setting the service policy to ``off`` or ``on``, you *must* quote the
            setting. If you don't, the yaml parser will set the string to a boolean,
            which will cause trouble checking for stateful changes and will error when
            trying to set the policy on the ESXi host.

    service_restart
        If set to ``True``, the ntp daemon will be restarted, regardless of its previous
        running state. Default is ``False``.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: yaml

        Set firewall config:
          vmware_esxi.ntp_config:
            - service_running: True
            - ntp_servers:
              - 192.174.1.100
              - 192.174.1.200
            - service_policy: 'on'
            - service_restart: True
    """
    log.debug("Running vmware_esxi.ntp_config")
    ret = {"name": name, "result": None, "comment": "", "changes": {}}
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )

    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )
    ntpd = "ntpd"

    ntp_config = __salt__["vmware_esxi.get_ntp_config"](service_instance=service_instance)
    ntp_service_state = __salt__["vmware_esxi.list_services"](
        service_name=ntpd, service_instance=service_instance
    )

    for host in hosts:
        if ntp_servers and set(ntp_servers) != set(ntp_config[host.name]["ntp_servers"]):
            ret["changes"][host.name] = {}
            if not __opts__["test"]:
                response = __salt__["vmware_esxi.set_ntp_config"](
                    ntp_servers=ntp_servers, host_name=host.name, service_instance=service_instance
                )
                error = response.get("Error")
                if error:
                    ret["result"] = False
                    ret["comment"] = "Error: {}".format(error)
                    return ret
            # Set changes dictionary for ntp_servers
            ret["changes"][host.name].update(
                {"ntp_servers": {"old": ntp_config[host.name]["ntp_servers"], "new": ntp_servers}}
            )

        # Configure service_running state
        ntp_running = ntp_service_state[host.name][ntpd]["state"] == "running"
        if service_running != ntp_running:
            if host.name not in ret["changes"]:
                ret["changes"][host.name] = {}
            # Only run the command if not using test=True
            if not __opts__["test"]:
                # Start ntdp if service_running=True
                if service_running is True:
                    response = __salt__["vmware_esxi.service_start"](
                        service_name=ntpd, host_name=host.name, service_instance=service_instance
                    )
                # Stop ntpd if service_running=False
                else:
                    response = __salt__["vmware_esxi.service_stop"](
                        service_name=ntpd, host_name=host.name, service_instance=service_instance
                    )
            ret["changes"][host.name].update(
                {"service_running": {"old": ntp_running, "new": service_running}}
            )
        # Configure service_policy
        if service_policy:
            if service_policy != ntp_service_state[host.name][ntpd]["startup_policy"]:
                if host.name not in ret["changes"]:
                    ret["changes"][host.name] = {}
                # Only run the command if not using test=True
                if not __opts__["test"]:
                    response = __salt__["vmware_esxi.service_policy"](
                        service_name=ntpd,
                        startup_policy=service_policy,
                        host_name=host.name,
                        service_instance=service_instance,
                    )
                ret["changes"][host.name].update(
                    {
                        "service_policy": {
                            "old": ntp_service_state[host.name][ntpd]["startup_policy"],
                            "new": service_policy,
                        }
                    }
                )

        # Restart ntp_service if service_restart=True
        if service_restart:
            if host.name not in ret["changes"]:
                ret["changes"][host.name] = {}
            # Only run the command if not using test=True
            if not __opts__["test"]:
                response = __salt__["vmware_esxi.service_restart"](
                    service_name=ntpd, host_name=host.name, service_instance=service_instance
                )
            ret["changes"][host.name].update(
                {"service_restart": {"old": "", "new": "NTP Daemon Restarted."}}
            )

    if __opts__["test"]:
        ret["result"] = None
        ret["comment"] = "NTP state will change."
        return ret

    ret["result"] = True
    if ret["changes"] == {}:
        ret["comment"] = "NTP is already in the desired state."
    return ret


def firewall_configs(
    name,
    config,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
    drift_level=0,
):
    """
    Get/Set firewall configuration on matching ESXi hosts based on drift report.

    name
        Name of configuration. (required).

    config
        Map with configuration values. (required).

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    drift_level
        Defines the tree level at which drift changes will be represented in output (optional)

    .. code-block:: yaml

        firewall_rules_test1:
            vmware_esxi.firewall_configs:
            - configs:
                - name: sshServer
                enabled: True
                - name: sshClient
                enabled: True

        firewall_rules_test2:
            mware_esxi.firewall_configs:
            - profile: vcenter
            - drift_level: 1
            - config:
                - name: sshServer
                enabled: true
                allowed_host:
                    all_ip: false
                    ip_address:
                    - 192.168.0.253
                    - 192.168.10.1
                    ip_network:
                    - 192.168.0.0/24
                - name: sshClient
                enabled: true
    """

    # Keep this structure
    ret = {"name": name, "result": None, "comment": "", "changes": {}}
    # Connect to VMware service
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )

    # Get Host/s list
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    # Clone config input to a Map.
    # Can be used to transform input to internal objects and do validation if needed
    new_configs = {}
    for rule_config in config:
        # Create full representation of the object, default or empty values
        new_config = {
            "enabled": rule_config["enabled"],
            "allowed_host": {
                "all_ip": True,  # by default is True
                "ip_address": [],  # by default is Empty
                "ip_network": [],  # by default is Empty
            },
        }
        # Transform / Validate input vs object, e.g. allowed_host section
        if "allowed_host" in rule_config:
            if "ip_address" in rule_config["allowed_host"]:
                ip_addresses = rule_config["allowed_host"]["ip_address"]
                if ip_addresses:
                    new_config["allowed_host"]["all_ip"] = False
                    new_config["allowed_host"]["ip_address"] = ip_addresses
            if "ip_network" in rule_config["allowed_host"]:
                ip_networks = rule_config["allowed_host"]["ip_network"]
                if ip_networks:
                    new_config["allowed_host"]["all_ip"] = False
                    new_config["allowed_host"]["ip_network"] = ip_networks
        new_configs[rule_config["name"]] = new_config

    # Get all firewall rules per host,
    # old_configs holds only the rules that are in the scope of interest (provided in argument config_input)
    old_configs = {}
    for host in hosts:
        firewall_config = host.configManager.firewallSystem
        if not firewall_config:
            continue

        ruleset_configs = {}
        for ruleset in firewall_config.firewallInfo.ruleset:
            # filter only interesting rules (provided as arguments config_input)
            if ruleset.key in new_configs.keys():
                # all fields are present in vmomi object, hence also in our object
                ruleset_configs[ruleset.key] = {
                    "enabled": ruleset.enabled,
                    "allowed_host": {
                        "all_ip": ruleset.allowedHosts.allIp,
                        "ip_address": list(ruleset.allowedHosts.ipAddress),
                        "ip_network": [
                            f"{n.network}/{n.prefixLength}"
                            for n in list(ruleset.allowedHosts.ipNetwork)
                        ],
                    },
                }
        old_configs[host.name] = ruleset_configs

    # Find rules changes
    hosts_changes = {}
    for host in hosts:
        rule_diff = drift.drift_report(
            {host.name: old_configs[host.name]}, {host.name: new_configs}, diff_level=0
        )
        rule_diff = json.loads(json.dumps(rule_diff))  # clone object
        if rule_diff is not None and host.name in rule_diff:
            ret["changes"][host.name] = rule_diff[host.name]

            # add changes for process if not dry-run
            if host.name not in hosts_changes:
                hosts_changes[host.name] = []
            new_rules = rule_diff[host.name]["new"]
            for rule_name in new_rules:
                # don't use delta like this - ({"name": rule_name} | new_rules[rule_name]), but:
                hosts_changes[host.name].append({**{"name": rule_name}, **new_configs[rule_name]})

        # it's used only in changes representation and drift report is bigger than first level
        if drift_level > 0:
            rule_diff = drift.drift_report(
                {host.name: old_configs[host.name]},
                {host.name: new_configs},
                diff_level=drift_level,
            )
            if rule_diff is not None and host.name in rule_diff:
                ret["changes"][host.name] = rule_diff[host.name]

    # If it's not dry-run and has changes, then apply changes
    if not __opts__["test"] and hosts_changes:
        comments = {}
        success = True
        for host_name in hosts_changes:
            changes = hosts_changes[host_name]
            for new_rule in changes:
                try:
                    vmware_esxi.set_firewall_config(
                        firewall_config=new_rule,
                        host_name=host_name,
                        service_instance=service_instance,
                        profile=profile,
                    )

                    comments[host_name + " " + new_rule["name"]] = {
                        "status": "SUCCESS",
                        "message": f"Rule '{new_rule['name']}' has been changed successfully for host {host_name}.",
                    }
                except Exception as err:
                    success = False
                    comments[host_name + " " + new_rule["name"]] = {
                        "status": "FAILURE",
                        "message": f"Error occured while setting rule '{new_rule['name']}' for host {host_name}: {err}",
                    }
        # ret["comment"] = "\n ".join(comments)
        ret["comment"] = comments  # it's more readable if passed as object
        ret["result"] = success  # at least one success

    return ret


def password_present(
    name,
    password,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Update the password for a given host.

    name
        Existing user to update on matching ESXi hosts. (required)

    password
        The new password to change on the host. (required)

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: yaml

        Set firewall config:
        vmware_esxi.password_present:
            - name: root
            - password: Password1!
    """
    log.debug("Running vmware_esxi.password_present")
    ret = {
        "name": name,
        "result": True,
        "changes": {},
        "comment": "",
    }

    if __opts__["test"]:
        ret["result"] = None
        ret["comment"] = "Host password will change."
        return ret
    else:
        try:
            __salt__["vmware_esxi.update_user"](
                user_name=name,
                password=password,
                datacenter_name=datacenter_name,
                cluster_name=cluster_name,
                host_name=host_name,
                service_instance=service_instance,
                profile=profile,
            )
        except salt.exceptions.CommandExecutionError as err:
            ret["result"] = False
            ret["comment"] = "Error: {}".format(err)
            return ret
    ret["comment"] = "Host password changed."
    return ret


def vsan_config(
    name,
    enabled,
    add_disks_to_vsan=False,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Configures a host's VSAN properties such as enabling or disabling VSAN, or
    adding VSAN-eligible disks to the VSAN system for the host.

    name
        Name of the state.

    enabled
        Ensures whether or not VSAN should be enabled on a host as a boolean
        value where ``True`` indicates that VSAN should be enabled and ``False``
        indicates that VSAN should be disabled.

    add_disks_to_vsan
        If set to ``True``, any VSAN-eligible disks for the given host will be added
        to the host's VSAN system. Default is ``False``.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    Example:
    .. code-block:: yaml

        configure-host-vsan:
          vmware_esxi.vsan_configured:
            - enabled: True
            - add_disks_to_vsan: True
    """
    ret = {"name": name, "result": False, "changes": {}, "comment": ""}

    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )

    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    for host in hosts:
        ret["changes"][host.name] = {}
        current_vsan_enabled = __salt__["vmware_esxi.get_vsan_enabled"](
            host_name=host.name, service_instance=service_instance
        )
        error = current_vsan_enabled.get("Error")
        if error:
            ret["comment"] = "Error: {}".format(error)
            return ret
        current_vsan_enabled = current_vsan_enabled.get(host.name)

        # Configure VSAN Enabled state, if changed.
        if enabled != current_vsan_enabled:
            # Only run the command if not using test=True
            if not __opts__["test"]:
                response = __salt__["vmware_esxi.vsan_enable"](
                    enable=enabled, host_name=host.name, service_instance=service_instance
                )
                error = response.get("Error")
                if error:
                    ret["comment"] = "Error: {}".format(error)
                    return ret
            ret["changes"][host.name].update(
                {"enabled": {"old": current_vsan_enabled, "new": enabled}}
            )

        # Add any eligible disks to VSAN, if requested.
        if add_disks_to_vsan:
            current_eligible_disks = __salt__["vmware_esxi.get_vsan_eligible_disks"](
                host_name=host.name, service_instance=service_instance
            )
            error = current_eligible_disks.get("Error")
            if error:
                ret["comment"] = "Error: {}".format(error)
                return ret
            disks = current_eligible_disks.get("Eligible")
            if disks and isinstance(disks, list):
                # Only run the command if not using test=True
                if not __opts__["test"]:
                    response = __salt__["vmware_esxi.vsan_add_disks"](
                        host_name=host.name, service_instance=service_instance
                    )
                    error = response.get("Error")
                    if error:
                        ret["comment"] = "Error: {}".format(error)
                        return ret

                ret["changes"][host.name].update({"add_disks_to_vsan": {"old": "", "new": disks}})

    ret["result"] = True
    if ret["changes"] == {}:
        ret["comment"] = "VSAN configuration is already in the desired state."
        return ret

    if __opts__["test"]:
        ret["result"] = None
        ret["comment"] = "VSAN configuration will change."

    return ret


def vmotion_configured(
    name,
    enabled,
    device="vmk0",
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
):
    """
    Configures a host's VMotion properties such as enabling VMotion and setting
    the device VirtualNic that VMotion will use.

    name
        Name of the state.  (DGM this could have been returned from name of function)

    enabled
        Ensures whether or not VMotion should be enabled on a host as a boolean
        value where ``True`` indicates that VMotion should be enabled and ``False``
        indicates that VMotion should be disabled.

    device
        The device that uniquely identifies the VirtualNic that will be used for
        VMotion for the host. Defaults to ``vmk0``.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    Example:

    .. code-block:: yaml

        configure-vmotion:
          esxi.vmotion_configured:
            - enabled: True
            - device: sample-device

    """
    log.debug("Running vmware_esxi.firewall_config")
    ret = {"name": name, "result": None, "comment": "", "changes": {}}
    try:
        response_list = __salt__["vmware_esxi.get_vmotion_enabled"](
            datacenter_name=datacenter_name,
            cluster_name=cluster_name,
            host_name=host_name,
            service_instance=service_instance,
        )

        # returns a list of host names with enabled or nota
        log.debug(f"DGM vmotion_configured response_list '{response_list}'")
        for host in response_list:
            current_vmotion_enabled = host.get("VMotion_Enabled")

            # DGM work in progress - pausing while helping with 3006 RC1

            # Configure VMotion Enabled state, if changed.
            if enabled != current_vmotion_enabled:
                # Only run the command if not using test=True
                if not __opts__["test"]:
                    # Enable VMotion if enabled=True
                    if enabled is True:
                        ## response = __salt__[esxi_cmd]("vmotion_enable", device=device).get(host)
                        # DGM work to be done for set_vmotion
                        response = __salt__["vmware_esxi.vmotion_enable"](device=device).get(host)
                        error = response.get("Error")
                        if error:
                            ret["comment"] = "Error: {}".format(error)
                            return ret
                    # Disable VMotion if enabled=False
                    else:
                        ## response = __salt__[esxi_cmd]("vmotion_disable").get(host)
                        # DGM work to be done for set_vmotion
                        response = __salt__["vmware_esxi.vmotion_disable"]().get(host)
                        error = response.get("Error")
                        if error:
                            ret["comment"] = "Error: {}".format(error)
                            return ret
                ret["changes"].update(
                    {host: {"enabled": {"old": current_vmotion_enabled, "new": enabled}}}
                )

        ret["result"] = True
        if ret["changes"] == {}:
            ret["comment"] = "VMotion configuration is already in the desired state."
            return ret

        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = "VMotion configuration will change."

    except salt.exceptions.CommandExecutionError as err:
        ret["result"] = False
        ret["comment"] = "Error: {}".format(err)
        return ret

    return ret
