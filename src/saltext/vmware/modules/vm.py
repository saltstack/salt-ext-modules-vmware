# SPDX-License-Identifier: Apache-2.0
import logging

import salt.exceptions
import salt.utils.platform
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.connect as connect
import saltext.vmware.utils.datastore as utils_datastore
import saltext.vmware.utils.vm as utils_vm

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False

__virtualname__ = "vmware_vm"
__proxyenabled__ = ["vmware_vm"]
__func_alias__ = {"list_": "list"}


def __virtual__():
    return __virtualname__


def list_(service_instance=None):
    """
    Returns virtual machines.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vm.list
    """
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)
    return utils_vm.list_vms(service_instance)


def list_templates(service_instance=None):
    """
    Returns virtual machines tempates.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vm.list_templates
    """
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)
    return utils_vm.list_vm_templates(service_instance)


def path(vm_name, service_instance=None):
    """
    Returns specified virtual machine path.

    vm_name
        The name of the virtual machine.

    service_instance
        The Service Instance from which to obtain managed object references.

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vm.path vm_name=vm01
    """
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)
    vm_ref = utils_common.get_mor_by_property(
        service_instance,
        vim.VirtualMachine,
        vm_name,
    )
    return utils_common.get_path(vm_ref, service_instance)


def _deploy_ovf(name, host_name, ovf, service_instance=None):
    """
    Helper fuctions that takes in a OVF file to create a virtual machine.

    Returns virtual machine reference.

    name
        The name of the virtual machine to be created.

    host_name
        The name of the esxi host to create the vitual machine on.

    ovf_path
        The path to the Open Virtualization Format that contains a configuration of a virtual machine.

    service_instance
        The Service Instance from which to obtain managed object references.
    """
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)

    vms = list_(service_instance)
    if name in vms:
        raise salt.exceptions.CommandExecutionError("Duplicate virtual machine name.")

    content = service_instance.content
    manager = content.ovfManager
    spec_params = vim.OvfManager.CreateImportSpecParams(entityName=name)

    resources = utils_common.deployment_resources(host_name, service_instance)

    import_spec = manager.CreateImportSpec(
        ovf, resources["resource_pool"], resources["destination_host"].datastore[0], spec_params
    )
    errors = [e.msg for e in import_spec.error]
    if errors:
        log.exception(errors)
        raise salt.exceptions.VMwareApiError(errors)
    vm_ref = utils_vm.create_vm(
        name,
        import_spec.importSpec.configSpec,
        resources["datacenter"].vmFolder,
        resources["resource_pool"],
        resources["destination_host"],
    )
    return vm_ref


def deploy_ovf(vm_name, host_name, ovf_path, service_instance=None):
    """
    Deploy a virtual machine from an OVF

    vm_name
        The name of the virtual machine to be created.

    host_name
        The name of the esxi host to create the vitual machine on.

    ovf_path
        The path to the Open Virtualization Format that contains a configuration of a virtual machine.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vm.deploy_ovf vm_name=vm01 host_name=host1 ovf_path=/tmp/appliance.ovf
    """
    ovf = utils_vm.read_ovf_file(ovf_path)
    _deploy_ovf(vm_name, host_name, ovf, service_instance)
    return {"deployed": True}


def deploy_ova(vm_name, host_name, ova_path, service_instance=None):
    """
    Deploy a virtual machine from an OVA

    vm_name
        The name of the virtual machine to be created.

    host_name
        The name of the esxi host to create the vitual machine on.

    ova_path
        The path to the Open Virtualization Appliance that contains a compressed configuration of a virtual machine.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vm.deploy_ova vm_name=vm01 host_name=host1 ova_path=/tmp/appliance.ova
    """
    ovf = utils_vm.read_ovf_from_ova(ova_path)
    _deploy_ovf(vm_name, host_name, ovf, service_instance)
    return {"deployed": True}


def deploy_template(vm_name, template_name, host_name, service_instance=None):
    """
    Deploy a virtual machine from a template virtual machine.

    vm_name
        The name of the virtual machine to be created.

    template_name
        The name of the template to clone from.

    host_name
        The name of the esxi host to create the vitual machine on.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vm.deploy_template vm_name=vm01 template_name=template1 host_name=host1
    """
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)

    vms = list_(service_instance)
    if vm_name in vms:
        raise salt.exceptions.CommandExecutionError("Duplicate virtual machine name.")

    template_vms = list_templates(service_instance)
    if template_name not in template_vms:
        raise salt.exceptions.CommandExecutionError("Template does not exist.")

    template = utils_common.get_mor_by_property(service_instance, vim.VirtualMachine, template_name)
    resources = utils_common.deployment_resources(host_name, service_instance)

    relospec = vim.vm.RelocateSpec()
    relospec.pool = resources["resource_pool"]

    clonespec = vim.vm.CloneSpec()
    clonespec.location = relospec

    utils_vm.clone_vm(vm_name, resources["datacenter"].vmFolder, template, clonespec)
    return {"deployed": True}


def info(vm_name=None, service_instance=None):
    """
    Return basic info about a vSphere VM guest

    vm_name
        (optional) The name of the virtual machine to get info on.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vm.info vm_name=vm01
    """
    vms = []
    info = {}
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)

    if vm_name:
        vms.append(
            utils_common.get_mor_by_property(
                service_instance,
                vim.VirtualMachine,
                vm_name,
            )
        )

    else:
        for dc in service_instance.content.rootFolder.childEntity:
            for i in dc.vmFolder.childEntity:
                if isinstance(i, vim.VirtualMachine):
                    vms.append(i)

    for vm in vms:
        datacenter_ref = utils_common.get_parent_type(vm, vim.Datacenter)
        mac_address = utils_vm.get_mac_address(vm)
        network = utils_vm.get_network(vm)
        tags = []
        for tag in vm.tag:
            tags.append(tag.name)
        folder_path = utils_common.get_path(vm, service_instance)
        info[vm.summary.config.name] = {
            "guest_name": vm.summary.config.name,
            "guest_fullname": vm.summary.guest.guestFullName,
            "power_state": vm.summary.runtime.powerState,
            "ip_address": vm.summary.guest.ipAddress,
            "mac_address": mac_address,
            "uuid": vm.summary.config.uuid,
            "vm_network": network,
            "esxi_hostname": vm.summary.runtime.host.name,
            "datacenter": datacenter_ref.name,
            "cluster": vm.summary.runtime.host.parent.name,
            "tags": tags,
            "folder": folder_path,
            "moid": vm._moId,
        }
    return info


def power_state(vm_name, state, datacenter_name=None, service_instance=None):
    """
    Manages the power state of a virtual machine.

    vm_name
        The name of the virtual machine.

    state
        The state you want the specified virtual machine in (powered-on,powered-off,suspend,reset).

    datacenter_name
        (optional) The name of the datacenter containing the virtual machine you want to manage.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vm.power_state vm_name=vm01 state=powered-on datacenter_name=dc1
    """
    log.trace(f"Managing power state of virtual machine {vm_name} to {state}")
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)

    if datacenter_name:
        dc_ref = utils_common.get_mor_by_property(service_instance, vim.Datacenter, datacenter_name)
        vm_ref = utils_common.get_mor_by_property(
            service_instance, vim.VirtualMachine, vm_name, "name", dc_ref
        )
    else:
        vm_ref = utils_common.get_mor_by_property(service_instance, vim.VirtualMachine, vm_name)
    if state == "powered-on" and vm_ref.summary.runtime.powerState == "poweredOn":
        result = {
            "comment": "Virtual machine is already powered on",
            "changes": {"state": vm_ref.summary.runtime.powerState},
        }
        return result
    elif state == "powered-off" and vm_ref.summary.runtime.powerState == "poweredOff":
        result = {
            "comment": "Virtual machine is already powered off",
            "changes": {"state": vm_ref.summary.runtime.powerState},
        }
        return result
    elif state == "suspend" and vm_ref.summary.runtime.powerState == "suspended":
        result = {
            "comment": "Virtual machine is already suspended",
            "changes": {"state": vm_ref.summary.runtime.powerState},
        }
        return result
    result_ref_vm = utils_vm.power_cycle_vm(vm_ref, state)
    result = {
        "comment": f"Virtual machine {state} action succeeded",
        "changes": {"state": result_ref_vm.summary.runtime.powerState},
    }
    return result


def boot_manager(
    vm_name,
    order=["cdrom", "disk", "ethernet", "floppy"],
    delay=0,
    enter_bios_setup=False,
    retry_delay=0,
    efi_secure_boot_enabled=False,
    service_instance=None,
):
    """
    Manage boot option for a virtual machine

    vm_name
        The name of the virtual machine.

    order
        (List of strings) Boot order of devices. Acceptable strings: cdrom, disk, ethernet, floppy

    delay
        (integer, optional) Boot delay. When powering on or resetting, delay boot order by given milliseconds. Defaults to 0.

    enter_bios_setup
        (boolean, optional) During the next boot, force entry into the BIOS setup screen. Defaults to False.

    retry_delay
        (integer, optional) If the VM fails to find boot device, automatically retry after given milliseconds. Defaults to 0 (do not retry).

    efi_secure_boot_enabled
        (boolean, optional) Defaults to False.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vm.boot_manager vm_name=vm01 order='["cdrom", "disk", "ethernet"]' delay=5000 enter_bios_setup=False retry_delay=5000 efi_secure_boot_enabled=False
    """
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)

    vm = utils_common.get_mor_by_property(service_instance, vim.VirtualMachine, vm_name)

    boot_order_list = utils_vm.options_order_list(vm, order)

    # we removed the ability to individually set bootRetryEnabled, easily implemented if asked for
    input_opts = {
        "bootOrder": boot_order_list,
        "bootDelay": delay,
        "enterBIOSSetup": enter_bios_setup,
        "bootRetryEnabled": bool(retry_delay),
        "bootRetryDelay": retry_delay,
        "efiSecureBootEnabled": efi_secure_boot_enabled,
    }

    if utils_vm.compare_boot_options(input_opts, vm.config.bootOptions):
        return {"status": "already configured this way"}
    ret = utils_vm.change_boot_options(vm, input_opts)

    return ret


def create_snapshot(
    vm_name,
    snapshot_name,
    description="",
    include_memory=False,
    quiesce=False,
    datacenter_name=None,
    service_instance=None,
):
    """
    Create snapshot of given vm.

    vm_name
        The name of the virtual machine.

    snapshot_name
        The name for the snapshot being created. Not unique

    description
        Description for the snapshot.

    include_memory
        (boolean, optional) If TRUE, a dump of the internal state of the virtual machine (basically a memory dump) is included in the snapshot.

    quiesce
        (boolean, optional) If TRUE and the virtual machine is powered on when the snapshot is taken, VMware Tools is used to quiesce the file system in the virtual machine.

    datacenter_name
        (optional) The name of the datacenter containing the virtual machine.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vm.create_snapshot vm_name=vm01 snapshot_name=backup_snapshot_1 description="This snapshot is a backup of vm01" include_memory=False quiesce=True datacenter_name=dc1
    """

    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)

    if datacenter_name:
        dc_ref = utils_common.get_mor_by_property(service_instance, vim.Datacenter, datacenter_name)
        vm_ref = utils_common.get_mor_by_property(
            service_instance, vim.VirtualMachine, vm_name, "name", dc_ref
        )
    else:
        vm_ref = utils_common.get_mor_by_property(service_instance, vim.VirtualMachine, vm_name)

    snapshot = utils_vm.create_snapshot(vm_ref, snapshot_name, description, include_memory, quiesce)

    if isinstance(snapshot, vim.vm.Snapshot):
        return {"snapshot": "created"}
    else:
        return {"snapshot": "failed to create"}


def destroy_snapshot(
    vm_name,
    snapshot_name,
    snapshot_id=None,
    remove_children=False,
    datacenter_name=None,
    service_instance=None,
):
    """
    Destroy snapshot of given vm.

    vm_name
        The name of the virtual machine.

    snapshot_name
        The name for the snapshot being destroyed. Not unique

    snapshot_id
        (optional) ID of snapshot to be destroyed.

    remove_children
        (optional, Bool) Remove snapshots below snapshot being removed in tree.

    datacenter_name
        (optional) The name of the datacenter containing the virtual machine.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vm.destroy_snapshot vm_name=vm01 snapshot_name=backup_snapshot_1 snapshot_id=1 remove_children=False datacenter_name=dc1
    """
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)

    if datacenter_name:
        dc_ref = utils_common.get_mor_by_property(service_instance, vim.Datacenter, datacenter_name)
        vm_ref = utils_common.get_mor_by_property(
            service_instance, vim.VirtualMachine, vm_name, "name", dc_ref
        )
    else:
        vm_ref = utils_common.get_mor_by_property(service_instance, vim.VirtualMachine, vm_name)

    snap_ref = utils_vm.get_snapshot(vm_ref, snapshot_name, snapshot_id)
    utils_vm.destroy_snapshot(snap_ref.snapshot, remove_children)
    return {"snapshot": "destroyed"}


def snapshot(vm_name, datacenter_name=None, service_instance=None):
    """
    Return info about a virtual machine snapshots

    vm_name
        (optional) The name of the virtual machine to get info on.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vm.snapshot vm_name=vm01 datacenter_name=dc1
    """
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)

    if datacenter_name:
        dc_ref = utils_common.get_mor_by_property(service_instance, vim.Datacenter, datacenter_name)
        vm_ref = utils_common.get_mor_by_property(
            service_instance, vim.VirtualMachine, vm_name, "name", dc_ref
        )
    else:
        vm_ref = utils_common.get_mor_by_property(service_instance, vim.VirtualMachine, vm_name)

    snapshots = utils_vm.get_snapshots(vm_ref)

    return {"snapshots": snapshots}


def relocate(vm_name, new_host_name, datastore_name, service_instance=None):
    """
    Relocates a virtual machine to the location specified.

    vm_name
        The name of the virtual machine to relocate.

    new_host_name
        The name of the host you want to move the virtual machine to.

    datastore_name
        The name of the datastore you want to move the virtual machine to.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vm.relocate vm_name=vm01 new_host_name=host1 datastore_name=ds01
    """
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)
    vm_ref = utils_common.get_mor_by_property(service_instance, vim.VirtualMachine, vm_name)
    resources = utils_common.deployment_resources(new_host_name, service_instance)
    assert isinstance(datastore_name, str)
    datastores = utils_datastore.get_datastores(
        service_instance, datastore_name=datastore_name, datacenter_name=datacenter_name
    )
    datastore_ref = datastores[0] if datastores else None
    ret = utils_vm.relocate(
        vm_ref, resources["destination_host"], datastore_ref, resources["resource_pool"]
    )
    if ret == "success":
        return {"virtual_machine": "moved"}
    return {"virtual_machine": "failed to move"}
