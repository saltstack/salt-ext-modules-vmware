# SPDX-License-Identifier: Apache-2.0
import logging

import salt.exceptions
import salt.utils.platform
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
__func_alias__ = {"list_": "list"}


def __virtual__():
    return __virtualname__


def list_(service_instance=None):
    """
    Returns virtual machines.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.
    """
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)
    return utils_vm.list_vms(service_instance)


def list_templates(service_instance=None):
    """
    Returns virtual machines tempates.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.
    """
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)
    return utils_vm.list_vm_templates(service_instance)


def path(name, service_instance=None):
    """
    Returns specified virtual machine path.

    name
        The name of the virtual machine.

    service_instance
        The Service Instance from which to obtain managed object references.
    """
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)
    vm_ref = utils_common.get_mor_by_property(
        service_instance,
        vim.VirtualMachine,
        name,
    )
    return utils_common.get_path(vm_ref, service_instance)


def _deployment_resources(host_name, service_instance):
    """
    Returns the dict representation of deployment resources from given host name.

    host_name
        The name of the esxi host to obtain esxi reference.

    """
    destination_host_ref = utils_common.get_mor_by_property(
        service_instance,
        vim.HostSystem,
        host_name,
    )
    datacenter_ref = utils_common.get_parent_type(destination_host_ref, vim.Datacenter)
    cluster_ref = utils_common.get_parent_type(destination_host_ref, vim.ClusterComputeResource)
    resource_pool = cluster_ref.resourcePool

    return {
        "destination_host": destination_host_ref,
        "datacenter": datacenter_ref,
        "cluster": cluster_ref,
        "resource_pool": resource_pool,
    }


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

    resources = _deployment_resources(host_name, service_instance)

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


def deploy_ovf(name, host_name, ovf_path, service_instance=None):
    """
    Deploy a virtual machine from an OVF

    name
        The name of the virtual machine to be created.

    host_name
        The name of the esxi host to create the vitual machine on.

    ovf_path
        The path to the Open Virtualization Format that contains a configuration of a virtual machine.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.
    """
    ovf = utils_vm.read_ovf_file(ovf_path)
    _deploy_ovf(name, host_name, ovf, service_instance)
    return {"deployed": True}


def deploy_ova(name, host_name, ova_path, service_instance=None):
    """
    Deploy a virtual machine from an OVA

    name
        The name of the virtual machine to be created.

    host_name
        The name of the esxi host to create the vitual machine on.

    ova_path
        The path to the Open Virtualization Appliance that contains a compressed configuration of a virtual machine.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.
    """
    ovf = utils_vm.read_ovf_from_ova(ova_path)
    _deploy_ovf(name, host_name, ovf, service_instance)
    return {"deployed": True}


def deploy_template(name, template_name, host_name, service_instance=None):
    """
    Deploy a virtual machine from a template virtual machine.

    name
        The name of the virtual machine to be created.

    template_name
        The name of the template to clone from.

    host_name
        The name of the esxi host to create the vitual machine on.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.
    """
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)

    vms = list_(service_instance)
    if name in vms:
        raise salt.exceptions.CommandExecutionError("Duplicate virtual machine name.")

    template_vms = list_templates(service_instance)
    if template_name not in template_vms:
        raise salt.exceptions.CommandExecutionError("Template does not exist.")

    template = utils_common.get_mor_by_property(service_instance, vim.VirtualMachine, template_name)
    resources = _deployment_resources(host_name, service_instance)

    relospec = vim.vm.RelocateSpec()
    relospec.pool = resources["resource_pool"]

    clonespec = vim.vm.CloneSpec()
    clonespec.location = relospec

    utils_vm.clone_vm(name, resources["datacenter"].vmFolder, template, clonespec)
    return {"deployed": True}


def info(name=None, service_instance=None):
    """
    Return basic info about a vSphere VM guest

    name
        (optional) The name of the virtual machine to get info on.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.
    """
    vms = []
    info = {}
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)

    if name:
        vms.append(
            utils_common.get_mor_by_property(
                service_instance,
                vim.VirtualMachine,
                name,
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


def power_state(name, state, datacenter_name=None, service_instance=None):
    """
    Manages the power state of a virtual machine.

    name
        The name of the virtual machine.

    state
        The state you want the specified virtual machine in (powered-on,powered-off,suspend,reset).

    datacenter_name
        (optional) The name of the datacenter containing the virtual machine you want to manage.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.
    """
    log.trace(f"Managing power state of virtual machine {name} to {state}")
    if service_instance is None:
        service_instance = connect.get_service_instance(opts=__opts__, pillar=__pillar__)

    if datacenter_name:
        dc_ref = utils_common.get_mor_by_property(service_instance, vim.Datacenter, datacenter_name)
        vm_ref = utils_common.get_mor_by_property(
            service_instance, vim.VirtualMachine, name, "name", dc_ref
        )
    else:
        vm_ref = utils_common.get_mor_by_property(service_instance, vim.VirtualMachine, name)
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
