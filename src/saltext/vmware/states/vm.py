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
    boot_order,
    delay=0,
    enter_bois_setup=False,
    retry_enabled=False,
    retry_delay=10000,
    efi_secure_boot_enabled=False,
    service_instance=None,
):
    """
    Manage boot option for a virtual machine

    boot_order
        (List of strings) Boot order of devices. Acceptable strings: cdrom, disk, ethernet, floppy

    delay
        (integer, optional) Boot delay. When powering on or resetting, delay boot order by given milliseconds. Defaults to 0.

    enter_bois_setup
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
    check_bo = utils_vm.check_boot_options(
        vm,
        boot_order_list,
        delay,
        enter_bois_setup,
        retry_enabled,
        retry_delay,
        efi_secure_boot_enabled,
    )
    ret["changes"] = check_bo["changes"]
    if __opts__["test"]:
        ret["comment"] = "These options are set to change."
        return ret

    result = utils_vm.change_boot_options(
        vm,
        boot_order_list,
        delay,
        enter_bois_setup,
        retry_enabled,
        retry_delay,
        efi_secure_boot_enabled,
    )
    ret["comment"] = result["status"]
    return ret
