# SPDX-License-Identifier: Apache-2.0
import logging
import tarfile

import salt.exceptions
import saltext.vmware.utils.cluster as utils_cluster
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.datacenter as utils_datacenter
import saltext.vmware.utils.esxi as utils_esxi

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
    if action == "powered-on":
        try:
            task = virtual_machine.PowerOnVM_Task()
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
    elif action == "powered-off":
        try:
            task = virtual_machine.PowerOffVM_Task()
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
    elif action == "suspend":
        try:
            task = virtual_machine.SuspendVM_Task()
            task_name = "suspend"
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
    elif action == "reset":
        try:
            task = virtual_machine.ResetVM_Task()
            task_name = "reset"
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
        utils_common.wait_for_task(
            task, utils_common.get_managed_object_name(virtual_machine), task_name
        )
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
        Host object where the machine will be placed (optional)

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


def clone_vm(vm_name, folder_object, template, clone_config_spec):
    """
    Creates virtual machine from config spec

    Returns Virtual Machine managed object reference

    vm_name
        Virtual machine name to be created

    folder_object
        Virtual Machine Folder managed object reference

    template
        Vitual Machine template to clone from

    clone_config_spec
        Clone Config Spec object
    """
    try:
        task = template.CloneVM_Task(folder_object, vm_name, clone_config_spec)
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
    vm_object = utils_common.wait_for_task(task, vm_name, "CloneVM Task", 10, "info")
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
    items = []
    vms = utils_common.get_mors_with_properties(service_instance, vim.VirtualMachine)
    for vm in vms:
        if not vm["config"].template:
            items.append(vm["name"])
    return items


def list_vm_templates(service_instance):
    """
    Returns a list of template VMs associated with a given service instance.

    service_instance
        The Service Instance Object from which to obtain VMs.
    """
    items = []
    vms = utils_common.get_mors_with_properties(service_instance, vim.VirtualMachine)
    for vm in vms:
        if vm["config"].template:
            items.append(vm["name"])
    return items


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


def get_placement(service_instance, datacenter, placement=None):
    """
    To create a virtual machine a resource pool needs to be supplied, we would like to use the strictest as possible.

    datacenter
        Name of the datacenter

    placement
        Dictionary with the placement info, cluster, host resource pool name

    return
        Resource pool, cluster and host object if any applies
    """
    log.trace("Retrieving placement information")
    resourcepool_object, placement_object = None, None
    if "host" in placement:
        host_objects = utils_esxi.get_hosts(
            service_instance, datacenter_name=datacenter, host_names=[placement["host"]]
        )
        if not host_objects:
            raise salt.exceptions.VMwareObjectRetrievalError(
                " ".join(
                    [
                        "The specified host",
                        "{} cannot be found.".format(placement["host"]),
                    ]
                )
            )
        try:
            host_props = utils_common.get_properties_of_managed_object(
                host_objects[0], properties=["resourcePool"]
            )
            resourcepool_object = host_props["resourcePool"]
        except vmodl.query.InvalidProperty:
            traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(
                path="parent",
                skip=True,
                type=vim.HostSystem,
                selectSet=[
                    vmodl.query.PropertyCollector.TraversalSpec(
                        path="resourcePool", skip=False, type=vim.ClusterComputeResource
                    )
                ],
            )
            resourcepools = utils_common.get_mors_with_properties(
                service_instance,
                vim.ResourcePool,
                container_ref=host_objects[0],
                property_list=["name"],
                traversal_spec=traversal_spec,
            )
            if resourcepools:
                resourcepool_object = resourcepools[0]["object"]
            else:
                raise salt.exceptions.VMwareObjectRetrievalError(
                    "The resource pool of host {} cannot be found.".format(placement["host"])
                )
        placement_object = host_objects[0]
    elif "resourcepool" in placement:
        resourcepool_objects = utils_common.get_resource_pools(
            service_instance, [placement["resourcepool"]], datacenter_name=datacenter
        )
        if len(resourcepool_objects) > 1:
            raise salt.exceptions.VMwareMultipleObjectsError(
                " ".join(
                    [
                        "Multiple instances are available of the",
                        "specified host {}.".format(placement["host"]),
                    ]
                )
            )
        resourcepool_object = resourcepool_objects[0]
        res_props = utils_common.get_properties_of_managed_object(
            resourcepool_object, properties=["parent"]
        )
        if "parent" in res_props:
            placement_object = res_props["parent"]
        else:
            raise salt.exceptions.VMwareObjectRetrievalError(
                " ".join(["The resource pool's parent", "object is not defined"])
            )
    elif "cluster" in placement:
        datacenter_object = utils_datacenter.get_datacenter(service_instance, datacenter)
        cluster_object = utils_cluster.get_cluster(datacenter_object, placement["cluster"])
        clus_props = utils_common.get_properties_of_managed_object(
            cluster_object, properties=["resourcePool"]
        )
        if "resourcePool" in clus_props:
            resourcepool_object = clus_props["resourcePool"]
        else:
            raise salt.exceptions.VMwareObjectRetrievalError(
                " ".join(["The cluster's resource pool", "object is not defined"])
            )
        placement_object = cluster_object
    else:
        # We are checking the schema for this object, this exception should never be raised
        raise salt.exceptions.VMwareObjectRetrievalError(" ".join(["Placement is not defined."]))
    return (resourcepool_object, placement_object)


def get_folder(service_instance, datacenter, placement, base_vm_name=None):
    """
    Returns a Folder Object

    service_instance
        Service instance object

    datacenter
        Name of the datacenter

    placement
        Placement dictionary

    base_vm_name
        Existing virtual machine name (for cloning)
    """
    log.trace("Retrieving folder information")
    if base_vm_name:
        vm_object = get_vm_by_property(service_instance, base_vm_name, vm_properties=["name"])
        vm_props = utils_common.get_properties_of_managed_object(vm_object, properties=["parent"])
        if "parent" in vm_props:
            folder_object = vm_props["parent"]
        else:
            raise salt.exceptions.VMwareObjectRetrievalError(
                " ".join(["The virtual machine parent", "object is not defined"])
            )
    # elif "folder" in placement:
    #     folder_objects = get_folders(
    #         service_instance, [placement["folder"]], datacenter
    #     )
    #     if len(folder_objects) > 1:
    #         raise salt.exceptions.VMwareMultipleObjectsError(
    #             " ".join(
    #                 [
    #                     "Multiple instances are available of the",
    #                     "specified folder {}".format(placement["folder"]),
    #                 ]
    #             )
    #         )
    #     folder_object = folder_objects[0]
    elif datacenter:
        datacenter_object = utils_datacenter.get_datacenter(service_instance, datacenter)
        dc_props = utils_common.get_properties_of_managed_object(
            datacenter_object, properties=["vmFolder"]
        )
        if "vmFolder" in dc_props:
            folder_object = dc_props["vmFolder"]
        else:
            raise salt.exceptions.VMwareObjectRetrievalError(
                "The datacenter vm folder object is not defined"
            )
    return folder_object


def read_ovf_file(ovf_path):
    """
    Read in OVF file.

    ovf_path
        Path to ovf file
    """
    try:
        with open(ovf_path) as ovf_file:
            return ovf_file.read()
    except Exception:
        exit(f"Could not read file: {ovf_path}")


def read_ovf_from_ova(ova_path):
    """
    Read in OVF file from OVA.

    ova_path
        Path to ova file
    """
    try:
        with tarfile.open(ova_path) as tf:
            for entry in tf:
                if entry.name.endswith(".ovf"):
                    ovf = tf.extractfile(entry)
                    return ovf.read().decode()
    except Exception:
        exit(f"Could not read file: {ova_path}")


def get_network(vm):
    """
    Returns network from a virtual machine object.

    vm
        Virtual Machine Object from which to obtain mac address.
    """
    network = {}
    for device in vm.guest.net:
        network[device.macAddress] = {}
        network[device.macAddress]["ipv4"] = []
        network[device.macAddress]["ipv6"] = []
        for address in device.ipAddress:
            if "::" in address:
                network[device.macAddress]["ipv6"].append(address)
            else:
                network[device.macAddress]["ipv4"].append(address)
    return network


def get_mac_address(vm):
    """
    Returns mac addresses from a virtual machine object.

    vm
        Virtual Machine Object from which to obtain mac address.
    """
    mac_address = []
    for device in vm.config.hardware.device:
        if isinstance(device, vim.vm.device.VirtualEthernetCard):
            mac_address.append(device.macAddress)
    return mac_address


def options_order_list(vm, order):
    """
    Converts a text order into internal representation for setting the boot order.

    vm
        Reference to virtual machine to check options on.

    order
        (List of strings) Boot order of devices. Acceptable strings: cdrom, disk, ethernet, floppy
    """

    boot_order_list = []
    for device_name in order:
        if device_name == "cdrom":
            cdrom = [
                device
                for device in vm.config.hardware.device
                if isinstance(device, vim.vm.device.VirtualCdrom)
            ]
            if cdrom:
                boot_order_list.append(vim.vm.BootOptions.BootableCdromDevice())
        elif device_name == "disk":
            hdd = [
                device
                for device in vm.config.hardware.device
                if isinstance(device, vim.vm.device.VirtualDisk)
            ]
            if hdd:
                boot_order_list.append(vim.vm.BootOptions.BootableDiskDevice(deviceKey=hdd[0].key))
        elif device_name == "ethernet":
            ether = [
                device
                for device in vm.config.hardware.device
                if isinstance(device, vim.vm.device.VirtualEthernetCard)
            ]
            if ether:
                boot_order_list.append(
                    vim.vm.BootOptions.BootableEthernetDevice(deviceKey=ether[0].key)
                )
        elif device_name == "floppy":
            floppy = [
                device
                for device in vm.config.hardware.device
                if isinstance(device, vim.vm.device.VirtualFloppy)
            ]
            if floppy:
                boot_order_list.append(vim.vm.BootOptions.BootableFloppyDevice())
        else:
            raise salt.exceptions.VMwareRuntimeError("invalid order name")
    return boot_order_list


def compare_boot_order_list(new, current):
    """
    Compares current boot order list and input boot order list.

    new
        List of vim bootable device objects.

    current
        List of vim bootable device objects.
    """
    if len(new) == len(current):
        for provided, existing in zip(new, current):
            if provided.deviceKey != existing.deviceKey:
                return False
        return True
    else:
        return False


def compare_boot_options(input_opts, current):
    """
    Compares current boot options and input options.

    input_opts
        (dict) Dictionary of virtual machine boot options.

    current
        Pyvmomi virtual machine boot options object.
    """

    lists_same = compare_boot_order_list(input_opts["bootOrder"], current.bootOrder)
    if (
        lists_same
        and current.bootDelay == input_opts["bootDelay"]
        and current.enterBIOSSetup == input_opts["enterBIOSSetup"]
        and current.bootRetryEnabled == input_opts["bootRetryEnabled"]
        and current.bootRetryDelay == input_opts["bootRetryDelay"]
        and current.efiSecureBootEnabled == input_opts["efiSecureBootEnabled"]
    ):
        return True
    else:
        return False


def boot_options_dif(input_opts, current):
    """
    Returns the difference between two dictionaries of virtual machine boot options.

    input_opts
        (dict) Dictionary of virtual machine boot options.

    current
        Pyvmomi virtual machine boot options object.
    """
    ret = {}
    lists_same = compare_boot_order_list(input_opts["bootOrder"], current.bootOrder)
    if not lists_same:
        old = [i.deviceKey for i in current.bootOrder]
        new = [i.deviceKey for i in input_opts["bootOrder"]]
        ret["order"] = {"old": old, "new": new}
    if not current.bootDelay == input_opts["bootDelay"]:
        ret["delay"] = {"old": current.bootDelay, "new": input_opts["bootDelay"]}
    if not current.enterBIOSSetup == input_opts["enterBIOSSetup"]:
        ret["enter_bois_setup"] = {
            "old": current.enterBIOSSetup,
            "new": input_opts["enterBIOSSetup"],
        }
    if not current.bootRetryEnabled == input_opts["bootRetryEnabled"]:
        ret["retry_enabled"] = {
            "old": current.bootRetryEnabled,
            "new": input_opts["bootRetryEnabled"],
        }
    if not current.bootRetryDelay == input_opts["bootRetryDelay"]:
        ret["retry_delay"] = {
            "old": current.bootRetryDelay,
            "new": input_opts["bootRetryDelay"],
        }
    if not current.efiSecureBootEnabled == input_opts["efiSecureBootEnabled"]:
        ret["efi_secure_boot_enabled"] = {
            "old": current.efiSecureBootEnabled,
            "new": input_opts["efiSecureBootEnabled"],
        }
    return ret


def change_boot_options(vm, input_opts):
    """
    Changes boot options on given vm.

    vm
        reference to virtual machine to change options on.

    input_opts
        (dict) Dictionary of virtual machine boot options.
    """
    vm_conf = vim.vm.ConfigSpec()
    vm_conf.bootOptions = vim.vm.BootOptions(**input_opts)
    task = vm.ReconfigVM_Task(vm_conf)
    utils_common.wait_for_task(task, vm.name, "configure boot options")

    return {"status": "changed"}


def create_snapshot(vm_ref, snapshot_name, description, memory, quiesce):
    """
    Create virtual machine snapshot.

    vm_ref
        Reference to virtual machine.

    snapshot_name
        The name for the snapshot being created. Not unique

    description
        Description for the snapshot.

    memory
        (boolean) If TRUE, a dump of the internal state of the virtual machine (basically a memory dump) is included in the snapshot.

    quiesce
        (boolean) If TRUE and the virtual machine is powered on when the snapshot is taken, VMware Tools is used to quiesce the file system in the virtual machine.
    """
    task = vm_ref.CreateSnapshot_Task(snapshot_name, description, memory, quiesce)
    ret = utils_common.wait_for_task(task, vm_ref.name, "create snapshot")
    return ret


def snapshot_recursive(snapshot_tree_root, snaps):
    """
    Recursively appends all snapshots in a snapshot tree.

    snapshot_tree_root
        Root node of snapshot tree.

    snaps
        List of snapshot info.
    """
    for ss in snapshot_tree_root:
        current = {
            "creation_time": str(ss.createTime),
            "description": ss.description,
            "id": ss.id,
            "name": ss.name,
            "state": ss.state,
            "quiesced": ss.quiesced,
        }
        snaps.append(current)
        if ss.childSnapshotList:
            snaps = snapshot_recursive(ss.childSnapshotList, snaps)
    return snaps


def snapshot_recursive_search(snapshot_tree_root, snapshot_name, snapshot_id):
    """
    Recursively appends all snapshots in a snapshot tree.

    snapshot_tree_root
        Root node of snapshot tree.

    snapshot_name
        Name of snapshot to find.

    snapshot_id
        id of snapshot to find.
    """
    for ss in snapshot_tree_root:
        if snapshot_id is None:
            if snapshot_name == ss.name:
                return ss
            elif ss.childSnapshotList:
                snaps = snapshot_recursive_search(ss.childSnapshotList, snapshot_name, snapshot_id)
            else:
                return None
        else:
            if snapshot_id and snapshot_id == ss.id and snapshot_name == ss.name:
                return ss
            elif ss.childSnapshotList:
                snaps = snapshot_recursive_search(ss.childSnapshotList, snapshot_name, snapshot_id)
            else:
                return None
    return snaps


def get_snapshots(vm_ref):
    """
    Returns list of snapshot info for a given vm.

    vm_ref
        Reference to a virtual machine.
    """
    snaps = []
    tree = vm_ref.snapshot
    if hasattr(tree, "rootSnapshotList") and len(tree.rootSnapshotList) > 0:
        snaps = snapshot_recursive(tree.rootSnapshotList, snaps)
    else:
        snaps = {"msg": "no snapshots"}
    return snaps


def get_snapshot(vm_ref, snapshot_name, snapshot_id):
    """"""
    tree = vm_ref.snapshot
    if hasattr(tree, "rootSnapshotList") and tree.rootSnapshotList:
        snap = snapshot_recursive_search(tree.rootSnapshotList, snapshot_name, snapshot_id)
    else:
        snap = {"msg": "no snapshots"}
    return snap


def destroy_snapshot(snapshot, remove_children):
    """
    Destroy a given snapshot.

    snapshot
        Reference to a vim.vm.Snapshot object.

    remove_children
        Remove subtree of snapshots.
    """
    vm_name = snapshot.vm.name
    task = snapshot.RemoveSnapshot_Task(remove_children)
    ret = utils_common.wait_for_task(task, vm_name, "remove snapshot")
    return ret


def relocate(vm, host, datastore, pool):
    """
    Relocates a virtual machine to the location specified.

    vm
        Reference to virtual machine.

    host
        Reference to new host.

    datastore
        Reference to datastore

    Pool
        Reference to resource pool.
    """
    relocate_spec = vim.vm.RelocateSpec(host=host, datastore=datastore, pool=pool)
    task = vm.RelocateVM_Task(relocate_spec)
    utils_common.wait_for_task(task, vm.name, "move vm")
    return task.info.state
