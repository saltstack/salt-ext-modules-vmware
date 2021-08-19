# SPDX-License-Identifier: Apache-2.0
import tarfile
import logging
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.datacenter as utils_datacenter
import salt.exceptions

# pylint: disable=no-name-in-module
try:
    from pyVmomi import vim, vmodl

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False

log = logging.getLogger(__name__)


def power_cycle_vm(virtual_machine, action="on"):
    """
    Powers on/off a virtual machine specified by its name.

    virtual_machine
        vim.VirtualMachine object to power on/off virtual machine

    action
        Operation option to power on/off the machine
    """
    if action == "on":
        try:
            task = virtual_machine.PowerOn()
            task_name = "power on"
        except vim.fault.NoPermission as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareApiError(
                "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
            )
        except vim.fault.VimFault as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareApiError(exc.msg)
        except vmodl.RuntimeFault as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareRuntimeError(exc.msg)
    elif action == "off":
        try:
            task = virtual_machine.PowerOff()
            task_name = "power off"
        except vim.fault.NoPermission as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareApiError(
                "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
            )
        except vim.fault.VimFault as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareApiError(exc.msg)
        except vmodl.RuntimeFault as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareRuntimeError(exc.msg)
    else:
        raise salt.exceptions.ArgumentValueError("The given action is not supported")
    try:
        utils_common.wait_for_task(task, utils_common.get_managed_object_name(virtual_machine), task_name)
    except salt.exceptions.VMwareFileNotFoundError as exc:
        raise salt.exceptions.VMwarePowerOnError(
            " ".join(
                [
                    "An error occurred during power",
                    "operation, a file was not found: {}".format(exc),
                ]
            )
        )
    return virtual_machine


def create_vm(vm_name, vm_config_spec, folder_object, resourcepool_object, host_object=None):
    """
    Creates virtual machine from config spec

    vm_name
        Virtual machine name to be created

    vm_config_spec
        Virtual Machine Config Spec object

    folder_object
        vm Folder managed object reference

    resourcepool_object
        Resource pool object where the machine will be created

    host_object
        Host object where the machine will ne placed (optional)

    return
        Virtual Machine managed object reference
    """
    try:
        if host_object and isinstance(host_object, vim.HostSystem):
            task = folder_object.CreateVM_Task(
                vm_config_spec, pool=resourcepool_object, host=host_object
            )
        else:
            task = folder_object.CreateVM_Task(vm_config_spec, pool=resourcepool_object)
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    vm_object = utils_common.wait_for_task(task, vm_name, "CreateVM Task", 10, "info")
    return vm_object


def register_vm(datacenter, name, vmx_path, resourcepool_object, host_object=None):
    """
    Registers a virtual machine to the inventory with the given vmx file, on success
    it returns the vim.VirtualMachine managed object reference

    datacenter
        Datacenter object of the virtual machine, vim.Datacenter object

    name
        Name of the virtual machine

    vmx_path:
        Full path to the vmx file, datastore name should be included

    resourcepool
        Placement resource pool of the virtual machine, vim.ResourcePool object

    host
        Placement host of the virtual machine, vim.HostSystem object
    """
    try:
        if host_object:
            task = datacenter.vmFolder.RegisterVM_Task(
                path=vmx_path,
                name=name,
                asTemplate=False,
                host=host_object,
                pool=resourcepool_object,
            )
        else:
            task = datacenter.vmFolder.RegisterVM_Task(
                path=vmx_path, name=name, asTemplate=False, pool=resourcepool_object
            )
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    try:
        vm_ref = utils_common.wait_for_task(task, name, "RegisterVM Task")
    except salt.exceptions.VMwareFileNotFoundError as exc:
        raise salt.exceptions.VMwareVmRegisterError(
            "An error occurred during registration operation, the "
            "configuration file was not found: {}".format(exc)
        )
    return vm_ref


def update_vm(vm_ref, vm_config_spec):
    """
    Updates the virtual machine configuration with the given object

    vm_ref
        Virtual machine managed object reference

    vm_config_spec
        Virtual machine config spec object to update
    """
    vm_name = utils_common.get_managed_object_name(vm_ref)
    log.trace("Updating vm '%s'", vm_name)
    try:
        task = vm_ref.ReconfigVM_Task(vm_config_spec)
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    vm_ref = utils_common.wait_for_task(task, vm_name, "ReconfigureVM Task")
    return vm_ref


def delete_vm(vm_ref):
    """
    Destroys the virtual machine

    vm_ref
        Managed object reference of a virtual machine object
    """
    vm_name = utils_common.get_managed_object_name(vm_ref)
    log.trace("Destroying vm '%s'", vm_name)
    try:
        task = vm_ref.Destroy_Task()
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    utils_common.wait_for_task(task, vm_name, "Destroy Task")


def unregister_vm(vm_ref):
    """
    Destroys the virtual machine

    vm_ref
        Managed object reference of a virtual machine object
    """
    vm_name = utils_common.get_managed_object_name(vm_ref)
    log.trace("Destroying vm '%s'", vm_name)
    try:
        vm_ref.UnregisterVM()
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        raise salt.exceptions.VMwareRuntimeError(exc.msg)


def list_vms(service_instance):
    """
    Returns a list of VMs associated with a given service instance.

    service_instance
        The Service Instance Object from which to obtain VMs.
    """
    return utils_common.list_objects(service_instance, vim.VirtualMachine)


def get_vm_by_property(
    service_instance,
    name,
    datacenter=None,
    vm_properties=None,
    traversal_spec=None,
    parent_ref=None,
):
    """
    Get virtual machine properties based on the traversal specs and properties list,
    returns Virtual Machine object with properties.

    service_instance
        Service instance object to access vCenter

    name
        Name of the virtual machine.

    datacenter
        Datacenter name

    vm_properties
        List of vm properties.

    traversal_spec
        Traversal Spec object(s) for searching.

    parent_ref
        Container Reference object for searching under a given object.
    """
    if datacenter and not parent_ref:
        parent_ref = utils_datacenter.get_datacenter(service_instance, datacenter)
    if not vm_properties:
        vm_properties = [
            "name",
            "config.hardware.device",
            "summary.storage.committed",
            "summary.storage.uncommitted",
            "summary.storage.unshared",
            "layoutEx.file",
            "config.guestFullName",
            "config.guestId",
            "guest.net",
            "config.hardware.memoryMB",
            "config.hardware.numCPU",
            "config.files.vmPathName",
            "summary.runtime.powerState",
            "guest.toolsStatus",
        ]
    vm_list = utils_common.get_mors_with_properties(
        service_instance,
        vim.VirtualMachine,
        vm_properties,
        container_ref=parent_ref,
        traversal_spec=traversal_spec,
    )
    vm_formatted = [vm for vm in vm_list if vm["name"] == name]
    if not vm_formatted:
        raise salt.exceptions.VMwareObjectRetrievalError("The virtual machine was not found.")
    elif len(vm_formatted) > 1:
        raise salt.exceptions.VMwareMultipleObjectsError(
            " ".join(
                [
                    "Multiple virtual machines were found with the"
                    "same name, please specify a container."
                ]
            )
        )
    return vm_formatted[0]


def read_ovf_file(ovf_path):
    """
    Read in OVF file.
    """
    try:
        with open(ovf_path) as ovf_file:
            return ovf_file.read()
    except Exception:
        exit(f"Could not read file: {ovf_path}")


def read_ovf_from_ova(ova_path):
    """
    Read in OVF file from OVA.
    """
    try:
        with tarfile.open(ova_path) as tf:
            for entry in tf:
                if entry.name.endswith(".ovf"):
                    ovf = tf.extractfile(entry)
                    return ovf.read().decode()
    except Exception:
        exit(f"Could not read file: {ova_path}")