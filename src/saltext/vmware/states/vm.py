# SPDX-License-Identifier: Apache-2.0
import logging

import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.connect as connect
import saltext.vmware.utils.vm as utils_vm

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_vm"
__proxyenabled__ = ["vmware_vm"]


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def set_boot_manager(
    name,
    boot_order=["cdrom", "disk", "ethernet", "floppy"],
    delay=0,
    enter_bios_setup=False,
    retry_enabled=False,
    retry_delay=10000,
    efi_secure_boot_enabled=False,
    service_instance=None,
):
    """
    Manage boot option for a virtual machine

    name
        The name of the virtual machine.

    boot_order
        (List of strings) Boot order of devices. Acceptable strings: cdrom, disk, ethernet, floppy

    delay
        (integer, optional) Boot delay. When powering on or resetting, delay boot order by given milliseconds. Defaults to 0.

    enter_bios_setup
        (boolean, optional) During the next boot, force entry into the BIOS setup screen. Defaults to False.

    retry_enabled
        (boolean, optional) If the VM fails to find boot device retry. Defaults to False.

    retry_delay
        (integer, optional) If the VM fails to find boot device, automatically retry after given milliseconds. Defaults to 10000.

    efi_secure_boot_enabled
        (boolean, optional) Defaults to False.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.
    """
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}
    vm = utils_common.get_mor_by_property(service_instance, vim.VirtualMachine, name)
    boot_order_list = utils_vm.options_order_list(vm, boot_order)
    input_opts = {
        "bootOrder": boot_order_list,
        "bootDelay": delay,
        "enterBIOSSetup": enter_bios_setup,
        "bootRetryEnabled": retry_enabled,
        "bootRetryDelay": retry_delay,
        "efiSecureBootEnabled": efi_secure_boot_enabled,
    }
    if utils_vm.compare_boot_options(input_opts, vm.config.bootOptions):
        ret["comment"] = "already configured this way"
        return ret

    ret["changes"] = utils_vm.boot_options_dif(input_opts, vm.config.bootOptions)

    if __opts__["test"]:
        ret["comment"] = "These options are set to change."
        return ret

    result = utils_vm.change_boot_options(vm, input_opts)
    ret["comment"] = result["status"]
    return ret


def snapshot_present(
    name,
    snapshot_name,
    description="",
    memory=False,
    quiesce=False,
    datacenter_name=None,
    service_instance=None,
):
    """
    Create virtual machine snapshot.

    name
        The name of the virtual machine.

    snapshot_name
        The name for the snapshot being created. Not unique

    description
        Description for the snapshot.

    memory
        (boolean, optional) If TRUE, a dump of the internal state of the virtual machine (basically a memory dump) is included in the snapshot.

    quiesce
        (boolean, optional) If TRUE and the virtual machine is powered on when the snapshot is taken, VMware Tools is used to quiesce the file system in the virtual machine.

    datacenter_name
        (optional) The name of the datacenter containing the virtual machine.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.
    """
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}
    if datacenter_name:
        dc_ref = utils_common.get_mor_by_property(service_instance, vim.Datacenter, datacenter_name)
        vm_ref = utils_common.get_mor_by_property(
            service_instance, vim.VirtualMachine, name, "name", dc_ref
        )
    else:
        vm_ref = utils_common.get_mor_by_property(service_instance, vim.VirtualMachine, name)

    if utils_vm.get_snapshot(vm_ref, snapshot_name, None):
        ret["comment"] = "snapshot was already created"
        return ret

    if __opts__["test"]:
        ret["changes"]["new"] = f"Snapshot {snapshot_name} will be created."
        ret["comment"] = "These options are set to change."
        return ret

    snapshot = utils_vm.create_snapshot(vm_ref, snapshot_name, description, memory, quiesce)

    if isinstance(snapshot, vim.vm.Snapshot):
        ret["changes"]["new"] = f"Snapshot {snapshot_name} created."
        ret["comment"] = "created"
        return ret
    else:
        ret["comment"] = "failed to create"
        return ret


def snapshot_absent(
    name,
    snapshot_name,
    snapshot_id=None,
    remove_children=False,
    datacenter_name=None,
    service_instance=None,
):
    """
    Create virtual machine snapshot.

    name
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
    """
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}
    if datacenter_name:
        dc_ref = utils_common.get_mor_by_property(service_instance, vim.Datacenter, datacenter_name)
        vm_ref = utils_common.get_mor_by_property(
            service_instance, vim.VirtualMachine, name, "name", dc_ref
        )
    else:
        vm_ref = utils_common.get_mor_by_property(service_instance, vim.VirtualMachine, name)

    snapshot = utils_vm.get_snapshot(vm_ref, snapshot_name, snapshot_id)

    if snapshot is None:
        ret["comment"] = f"Snapshot {snapshot_name} doesn't exist"
        return ret

    if __opts__["test"]:
        ret["changes"]["new"] = f"Snapshot {snapshot_name} will be destroyed."
        ret["comment"] = "These options are set to change."
        return ret

    utils_vm.destroy_snapshot(snapshot.snapshot, remove_children)

    ret["changes"]["new"] = f"Snapshot {snapshot_name} destroyed."
    ret["comment"] = "destroyed"
    return ret
