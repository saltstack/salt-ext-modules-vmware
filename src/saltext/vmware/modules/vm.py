# pylint: disable=C0302
"""
Manage VMware vCenter servers and ESXi hosts.

.. versionadded:: 2015.8.4

:codeauthor: Alexandru Bleotu <alexandru.bleotu@morganstaley.com>

Dependencies
============

- pyVmomi Python Module
- ESXCLI

pyVmomi
-------

PyVmomi can be installed via pip:

.. code-block:: bash

    pip install pyVmomi

.. note::

    Version 6.0 of pyVmomi has some problems with SSL error handling on certain
    versions of Python. If using version 6.0 of pyVmomi, Python 2.7.9,
    or newer must be present. This is due to an upstream dependency
    in pyVmomi 6.0 that is not supported in Python versions 2.7 to 2.7.8. If the
    version of Python is not in the supported range, you will need to install an
    earlier version of pyVmomi. See `Issue #29537`_ for more information.

.. _Issue #29537: https://github.com/saltstack/salt/issues/29537

Based on the note above, to install an earlier version of pyVmomi than the
version currently listed in PyPi, run the following:

.. code-block:: bash

    pip install pyVmomi==5.5.0.2014.1.1

The 5.5.0.2014.1.1 is a known stable version that this original vSphere Execution
Module was developed against.

vSphere Automation SDK
----------------------

vSphere Automation SDK can be installed via pip:

.. code-block:: bash

    pip install --upgrade pip setuptools
    pip install --upgrade git+https://github.com/vmware/vsphere-automation-sdk-python.git

.. note::

    The SDK also requires OpenSSL 1.0.1+ if you want to connect to vSphere 6.5+ in order to support
    TLS1.1 & 1.2.

    In order to use the tagging functions in this module, vSphere Automation SDK is necessary to
    install.

The module is currently in version 1.0.3
(as of 8/26/2019)

ESXCLI
------

Currently, about a third of the functions used in the vSphere Execution Module require
the ESXCLI package be installed on the machine running the Proxy Minion process.

The ESXCLI package is also referred to as the VMware vSphere CLI, or vCLI. VMware
provides vCLI package installation instructions for `vSphere 5.5`_ and
`vSphere 6.0`_.

.. _vSphere 5.5: http://pubs.vmware.com/vsphere-55/index.jsp#com.vmware.vcli.getstart.doc/cli_install.4.2.html
.. _vSphere 6.0: http://pubs.vmware.com/vsphere-60/index.jsp#com.vmware.vcli.getstart.doc/cli_install.4.2.html

Once all of the required dependencies are in place and the vCLI package is
installed, you can check to see if you can connect to your ESXi host or vCenter
server by running the following command:

.. code-block:: bash

    esxcli -s <host-location> -u <username> -p <password> system syslog config get

If the connection was successful, ESXCLI was successfully installed on your system.
You should see output related to the ESXi host's syslog configuration.

.. note::

    Be aware that some functionality in this execution module may depend on the
    type of license attached to a vCenter Server or ESXi host(s).

    For example, certain services are only available to manipulate service state
    or policies with a VMware vSphere Enterprise or Enterprise Plus license, while
    others are available with a Standard license. The ``ntpd`` service is restricted
    to an Enterprise Plus license, while ``ssh`` is available via the Standard
    license.

    Please see the `vSphere Comparison`_ page for more information.

.. _vSphere Comparison: https://www.vmware.com/products/vsphere/compare


About
=====

This execution module was designed to be able to handle connections both to a
vCenter Server, as well as to an ESXi host. It utilizes the pyVmomi Python
library and the ESXCLI package to run remote execution functions against either
the defined vCenter server or the ESXi host.

Whether or not the function runs against a vCenter Server or an ESXi host depends
entirely upon the arguments passed into the function. Each function requires a
``host`` location, ``username``, and ``password``. If the credentials provided
apply to a vCenter Server, then the function will be run against the vCenter
Server. For example, when listing hosts using vCenter credentials, you'll get a
list of hosts associated with that vCenter Server:

.. code-block:: bash

    # salt my-minion vsphere.list_hosts <vcenter-ip> <vcenter-user> <vcenter-password>
    my-minion:
    - esxi-1.example.com
    - esxi-2.example.com

However, some functions should be used against ESXi hosts, not vCenter Servers.
Functionality such as getting a host's coredump network configuration should be
performed against a host and not a vCenter server. If the authentication
information you're using is against a vCenter server and not an ESXi host, you
can provide the host name that is associated with the vCenter server in the
command, as a list, using the ``host_names`` or ``esxi_host`` kwarg. For
example:

.. code-block:: bash

    # salt my-minion vsphere.get_coredump_network_config <vcenter-ip> <vcenter-user> \
        <vcenter-password> esxi_hosts='[esxi-1.example.com, esxi-2.example.com]'
    my-minion:
    ----------
        esxi-1.example.com:
            ----------
            Coredump Config:
                ----------
                enabled:
                    False
        esxi-2.example.com:
            ----------
            Coredump Config:
                ----------
                enabled:
                    True
                host_vnic:
                    vmk0
                ip:
                    coredump-location.example.com
                port:
                    6500

You can also use these functions against an ESXi host directly by establishing a
connection to an ESXi host using the host's location, username, and password. If ESXi
connection credentials are used instead of vCenter credentials, the ``host_names`` and
``esxi_hosts`` arguments are not needed.

.. code-block:: bash

    # salt my-minion vsphere.get_coredump_network_config esxi-1.example.com root <host-password>
    local:
    ----------
        10.4.28.150:
            ----------
            Coredump Config:
                ----------
                enabled:
                    True
                host_vnic:
                    vmk0
                ip:
                    coredump-location.example.com
                port:
                    6500
"""
import logging
import sys

import salt.utils.platform
import saltext.vmware.utils.vmware
from salt.exceptions import InvalidConfigError
from salt.utils.decorators import depends
from salt.utils.dictdiffer import recursive_diff
from salt.utils.listdiffer import list_diff
from saltext.vmware.config.schemas.esxvm import ESXVirtualMachineDeleteSchema
from saltext.vmware.config.schemas.esxvm import ESXVirtualMachineUnregisterSchema

log = logging.getLogger(__name__)

try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

try:
    # pylint: disable=no-name-in-module
    from pyVmomi import (
        vim,
        VmomiSupport,
    )

    # pylint: enable=no-name-in-module

    # We check the supported vim versions to infer the pyVmomi version
    if (
        "vim25/6.0" in VmomiSupport.versionMap
        and sys.version_info > (2, 7)
        and sys.version_info < (2, 7, 9)
    ):

        log.debug("pyVmomi not loaded: Incompatible versions " "of Python. See Issue #29537.")
        raise ImportError()
    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_vm"


def __virtual__():
    return __virtualname__


def _get_scsi_controller_key(bus_number, scsi_ctrls):
    """
    Returns key number of the SCSI controller keys

    bus_number
        Controller bus number from the adapter

    scsi_ctrls
        List of SCSI Controller objects (old+newly created)
    """
    # list of new/old VirtualSCSIController objects, both new and old objects
    # should contain a key attribute key should be a negative integer in case
    # of a new object
    keys = [ctrl.key for ctrl in scsi_ctrls if scsi_ctrls and ctrl.busNumber == bus_number]
    if not keys:
        raise salt.exceptions.VMwareVmCreationError(
            "SCSI controller number {} doesn't exist".format(bus_number)
        )
    return keys[0]


def _create_adapter_type(network_adapter, adapter_type, network_adapter_label=""):
    """
    Returns a vim.vm.device.VirtualEthernetCard object specifying a virtual
    ethernet card information

    network_adapter
        None or VirtualEthernet object

    adapter_type
        String, type of adapter

    network_adapter_label
        string, network adapter name
    """
    log.trace("Configuring virtual machine network " "adapter adapter_type=%s", adapter_type)
    if adapter_type in ["vmxnet", "vmxnet2", "vmxnet3", "e1000", "e1000e"]:
        edited_network_adapter = saltext.vmware.utils.vmware.get_network_adapter_type(adapter_type)
        if isinstance(network_adapter, type(edited_network_adapter)):
            edited_network_adapter = network_adapter
        else:
            if network_adapter:
                log.trace(
                    "Changing type of '%s' from" " '%s' to '%s'",
                    network_adapter.deviceInfo.label,
                    type(network_adapter).__name__.rsplit(".", 1)[1][7:].lower(),
                    adapter_type,
                )
    else:
        # If device is edited and type not specified or does not match,
        # don't change adapter type
        if network_adapter:
            if adapter_type:
                log.error(
                    "Cannot change type of '%s' to '%s'. " "Not changing type",
                    network_adapter.deviceInfo.label,
                    adapter_type,
                )
            edited_network_adapter = network_adapter
        else:
            if not adapter_type:
                log.trace(
                    "The type of '%s' has not been specified. "
                    "Creating of default type 'vmxnet3'",
                    network_adapter_label,
                )
            edited_network_adapter = vim.vm.device.VirtualVmxnet3()
    return edited_network_adapter


def _create_network_backing(network_name, switch_type, parent_ref):
    """
    Returns a vim.vm.device.VirtualDevice.BackingInfo object specifying a
    virtual ethernet card backing information

    network_name
        string, network name

    switch_type
        string, type of switch

    parent_ref
        Parent reference to search for network
    """
    log.trace(
        "Configuring virtual machine network backing network_name=%s " "switch_type=%s parent=%s",
        network_name,
        switch_type,
        saltext.vmware.utils.vmware.get_managed_object_name(parent_ref),
    )
    backing = {}
    if network_name:
        if switch_type == "standard":
            networks = saltext.vmware.utils.vmware.get_networks(parent_ref, network_names=[network_name])
            if not networks:
                raise salt.exceptions.VMwareObjectRetrievalError(
                    "The network '{}' could not be " "retrieved.".format(network_name)
                )
            network_ref = networks[0]
            backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
            backing.deviceName = network_name
            backing.network = network_ref
        elif switch_type == "distributed":
            networks = saltext.vmware.utils.vmware.get_dvportgroups(
                parent_ref, portgroup_names=[network_name]
            )
            if not networks:
                raise salt.exceptions.VMwareObjectRetrievalError(
                    "The port group '{}' could not be " "retrieved.".format(network_name)
                )
            network_ref = networks[0]
            dvs_port_connection = vim.dvs.PortConnection(
                portgroupKey=network_ref.key,
                switchUuid=network_ref.config.distributedVirtualSwitch.uuid,
            )
            backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
            backing.port = dvs_port_connection
    return backing


def _set_network_adapter_mapping(domain, gateway, ip_addr, subnet_mask, mac):
    """
    Returns a vim.vm.customization.AdapterMapping object containing the IP
    properties of a network adapter card

    domain
        Domain of the host

    gateway
        Gateway address

    ip_addr
        IP address

    subnet_mask
        Subnet mask

    mac
        MAC address of the guest
    """
    adapter_mapping = vim.vm.customization.AdapterMapping()
    adapter_mapping.macAddress = mac
    adapter_mapping.adapter = vim.vm.customization.IPSettings()
    if domain:
        adapter_mapping.adapter.dnsDomain = domain
    if gateway:
        adapter_mapping.adapter.gateway = gateway
    if ip_addr:
        adapter_mapping.adapter.ip = vim.vm.customization.FixedIp(ipAddress=ip_addr)
        adapter_mapping.adapter.subnetMask = subnet_mask
    else:
        adapter_mapping.adapter.ip = vim.vm.customization.DhcpIpGenerator()
    return adapter_mapping


def _get_device_by_key(devices, key):
    """
    Returns the device with the given key, raises error if the device is
    not found.

    devices
        list of vim.vm.device.VirtualDevice objects

    key
        Unique key of device
    """
    device_keys = [d for d in devices if d.key == key]
    if device_keys:
        return device_keys[0]
    else:
        raise salt.exceptions.VMwareObjectNotFoundError(
            "Virtual machine device with unique key " "{} does not exist".format(key)
        )


def _get_device_by_label(devices, label):
    """
    Returns the device with the given label, raises error if the device is
    not found.

    devices
        list of vim.vm.device.VirtualDevice objects

    key
        Unique key of device
    """
    device_labels = [d for d in devices if d.deviceInfo.label == label]
    if device_labels:
        return device_labels[0]
    else:
        raise salt.exceptions.VMwareObjectNotFoundError(
            "Virtual machine device with " "label {} does not exist".format(label)
        )


def _apply_advanced_config(config_spec, advanced_config, vm_extra_config=None):
    """
    Sets configuration parameters for the vm

    config_spec
        vm.ConfigSpec object

    advanced_config
        config key value pairs

    vm_extra_config
        Virtual machine vm_ref.config.extraConfig object
    """
    log.trace("Configuring advanced configuration " "parameters %s", advanced_config)
    if isinstance(advanced_config, str):
        raise salt.exceptions.ArgumentValueError(
            "The specified 'advanced_configs' configuration "
            "option cannot be parsed, please check the parameters"
        )
    for key, value in advanced_config.items():
        if vm_extra_config:
            for option in vm_extra_config:
                if option.key == key and option.value == str(value):
                    continue
        else:
            option = vim.option.OptionValue(key=key, value=value)
            config_spec.extraConfig.append(option)


def _apply_hardware_version(hardware_version, config_spec, operation="add"):
    """
    Specifies vm container version or schedules upgrade,
    returns True on change and False if nothing have been changed.

    hardware_version
        Hardware version string eg. vmx-08

    config_spec
        Configuration spec object

    operation
        Defines the operation which should be used,
        the possibles values: 'add' and 'edit', the default value is 'add'
    """
    log.trace("Configuring virtual machine hardware " "version version=%s", hardware_version)
    if operation == "edit":
        log.trace("Scheduling hardware version " "upgrade to %s", hardware_version)
        scheduled_hardware_upgrade = vim.vm.ScheduledHardwareUpgradeInfo()
        scheduled_hardware_upgrade.upgradePolicy = "always"
        scheduled_hardware_upgrade.versionKey = hardware_version
        config_spec.scheduledHardwareUpgradeInfo = scheduled_hardware_upgrade
    elif operation == "add":
        config_spec.version = str(hardware_version)


def _apply_cpu_config(config_spec, cpu_props):
    """
    Sets CPU core count to the given value

    config_spec
        vm.ConfigSpec object

    cpu_props
        CPU properties dict
    """
    log.trace("Configuring virtual machine CPU " "settings cpu_props=%s", cpu_props)
    if "count" in cpu_props:
        config_spec.numCPUs = int(cpu_props["count"])
    if "cores_per_socket" in cpu_props:
        config_spec.numCoresPerSocket = int(cpu_props["cores_per_socket"])
    if "nested" in cpu_props and cpu_props["nested"]:
        config_spec.nestedHVEnabled = cpu_props["nested"]  # True
    if "hotadd" in cpu_props and cpu_props["hotadd"]:
        config_spec.cpuHotAddEnabled = cpu_props["hotadd"]  # True
    if "hotremove" in cpu_props and cpu_props["hotremove"]:
        config_spec.cpuHotRemoveEnabled = cpu_props["hotremove"]  # True


def _apply_memory_config(config_spec, memory):
    """
    Sets memory size to the given value

    config_spec
        vm.ConfigSpec object

    memory
        Memory size and unit
    """
    log.trace("Configuring virtual machine memory " "settings memory=%s", memory)
    if "size" in memory and "unit" in memory:
        try:
            if memory["unit"].lower() == "kb":
                memory_mb = memory["size"] / 1024
            elif memory["unit"].lower() == "mb":
                memory_mb = memory["size"]
            elif memory["unit"].lower() == "gb":
                memory_mb = int(float(memory["size"]) * 1024)
        except (TypeError, ValueError):
            memory_mb = int(memory["size"])
        config_spec.memoryMB = memory_mb
    if "reservation_max" in memory:
        config_spec.memoryReservationLockedToMax = memory["reservation_max"]
    if "hotadd" in memory:
        config_spec.memoryHotAddEnabled = memory["hotadd"]


def _apply_network_adapter_config(
    key,
    network_name,
    adapter_type,
    switch_type,
    network_adapter_label=None,
    operation="add",
    connectable=None,
    mac=None,
    parent=None,
):
    """
    Returns a vim.vm.device.VirtualDeviceSpec object specifying to add/edit a
    network device

    network_adapter_label
        Network adapter label

    key
        Unique key for device creation

    network_name
        Network or port group name

    adapter_type
        Type of the adapter eg. vmxnet3

    switch_type
        Type of the switch: standard or distributed

    operation
        Type of operation: add or edit

    connectable
        Dictionary with the device connection properties

    mac
        MAC address of the network adapter

    parent
        Parent object reference
    """
    adapter_type.strip().lower()
    switch_type.strip().lower()
    log.trace(
        "Configuring virtual machine network adapter "
        "network_adapter_label=%s network_name=%s "
        "adapter_type=%s switch_type=%$ mac=%s",
        network_adapter_label,
        network_name,
        adapter_type,
        switch_type,
        mac,
    )
    network_spec = vim.vm.device.VirtualDeviceSpec()
    network_spec.device = _create_adapter_type(
        network_spec.device, adapter_type, network_adapter_label=network_adapter_label
    )
    network_spec.device.deviceInfo = vim.Description()
    if operation == "add":
        network_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    elif operation == "edit":
        network_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
    if switch_type and network_name:
        network_spec.device.backing = _create_network_backing(network_name, switch_type, parent)
        network_spec.device.deviceInfo.summary = network_name
    if key:
        # random negative integer for creations, concrete device key
        # for updates
        network_spec.device.key = key
    if network_adapter_label:
        network_spec.device.deviceInfo.label = network_adapter_label
    if mac:
        network_spec.device.macAddress = mac
        network_spec.device.addressType = "Manual"
    network_spec.device.wakeOnLanEnabled = True
    if connectable:
        network_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
        network_spec.device.connectable.startConnected = connectable["start_connected"]
        network_spec.device.connectable.allowGuestControl = connectable["allow_guest_control"]
    return network_spec


def _apply_scsi_controller(adapter, adapter_type, bus_sharing, key, bus_number, operation):
    """
    Returns a vim.vm.device.VirtualDeviceSpec object specifying to
    add/edit a SCSI controller

    adapter
        SCSI controller adapter name

    adapter_type
        SCSI controller adapter type eg. paravirtual

    bus_sharing
         SCSI controller bus sharing eg. virtual_sharing

    key
        SCSI controller unique key

    bus_number
        Device bus number property

    operation
        Describes the operation which should be done on the object,
        the possibles values: 'add' and 'edit', the default value is 'add'

    .. code-block:: bash

        scsi:
          adapter: 'SCSI controller 0'
          type: paravirtual or lsilogic or lsilogic_sas
          bus_sharing: 'no_sharing' or 'virtual_sharing' or 'physical_sharing'
    """
    log.trace(
        "Configuring scsi controller adapter=%s adapter_type=%s "
        "bus_sharing=%s key=%s bus_number=%s",
        adapter,
        adapter_type,
        bus_sharing,
        key,
        bus_number,
    )
    scsi_spec = vim.vm.device.VirtualDeviceSpec()
    if adapter_type == "lsilogic":
        summary = "LSI Logic"
        scsi_spec.device = vim.vm.device.VirtualLsiLogicController()
    elif adapter_type == "lsilogic_sas":
        summary = "LSI Logic Sas"
        scsi_spec.device = vim.vm.device.VirtualLsiLogicSASController()
    elif adapter_type == "paravirtual":
        summary = "VMware paravirtual SCSI"
        scsi_spec.device = vim.vm.device.ParaVirtualSCSIController()
    elif adapter_type == "buslogic":
        summary = "Bus Logic"
        scsi_spec.device = vim.vm.device.VirtualBusLogicController()
    if operation == "add":
        scsi_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    elif operation == "edit":
        scsi_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
    scsi_spec.device.key = key
    scsi_spec.device.busNumber = bus_number
    scsi_spec.device.deviceInfo = vim.Description()
    scsi_spec.device.deviceInfo.label = adapter
    scsi_spec.device.deviceInfo.summary = summary
    if bus_sharing == "virtual_sharing":
        # Virtual disks can be shared between virtual machines on
        # the same server
        scsi_spec.device.sharedBus = vim.vm.device.VirtualSCSIController.Sharing.virtualSharing
    elif bus_sharing == "physical_sharing":
        # Virtual disks can be shared between virtual machines on any server
        scsi_spec.device.sharedBus = vim.vm.device.VirtualSCSIController.Sharing.physicalSharing
    elif bus_sharing == "no_sharing":
        # Virtual disks cannot be shared between virtual machines
        scsi_spec.device.sharedBus = vim.vm.device.VirtualSCSIController.Sharing.noSharing
    return scsi_spec


def _create_ide_controllers(ide_controllers):
    """
    Returns a list of vim.vm.device.VirtualDeviceSpec objects representing
    IDE controllers

    ide_controllers
        IDE properties
    """
    ide_ctrls = []
    keys = range(-200, -250, -1)
    if ide_controllers:
        devs = [ide["adapter"] for ide in ide_controllers]
        log.trace("Creating IDE controllers %s", devs)
        for ide, key in zip(ide_controllers, keys):
            ide_ctrls.append(
                _apply_ide_controller_config(ide["adapter"], "add", key, abs(key + 200))
            )
    return ide_ctrls


def _apply_ide_controller_config(ide_controller_label, operation, key, bus_number=0):
    """
    Returns a vim.vm.device.VirtualDeviceSpec object specifying to add/edit an
    IDE controller

    ide_controller_label
        Controller label of the IDE adapter

    operation
        Type of operation: add or edit

    key
        Unique key of the device

    bus_number
        Device bus number property
    """
    log.trace("Configuring IDE controller " "ide_controller_label=%s", ide_controller_label)
    ide_spec = vim.vm.device.VirtualDeviceSpec()
    ide_spec.device = vim.vm.device.VirtualIDEController()
    if operation == "add":
        ide_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    if operation == "edit":
        ide_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
    ide_spec.device.key = key
    ide_spec.device.busNumber = bus_number
    if ide_controller_label:
        ide_spec.device.deviceInfo = vim.Description()
        ide_spec.device.deviceInfo.label = ide_controller_label
        ide_spec.device.deviceInfo.summary = ide_controller_label
    return ide_spec


def _create_sata_controllers(sata_controllers):
    """
    Returns a list of vim.vm.device.VirtualDeviceSpec objects representing
    SATA controllers

    sata_controllers
        SATA properties
    """
    sata_ctrls = []
    keys = range(-15000, -15050, -1)
    if sata_controllers:
        devs = [sata["adapter"] for sata in sata_controllers]
        log.trace("Creating SATA controllers %s", devs)
        for sata, key in zip(sata_controllers, keys):
            sata_ctrls.append(
                _apply_sata_controller_config(sata["adapter"], "add", key, sata["bus_number"])
            )
    return sata_ctrls


def _apply_sata_controller_config(sata_controller_label, operation, key, bus_number=0):
    """
    Returns a vim.vm.device.VirtualDeviceSpec object specifying to add/edit a
    SATA controller

    sata_controller_label
        Controller label of the SATA adapter

    operation
        Type of operation: add or edit

    key
        Unique key of the device

    bus_number
        Device bus number property
    """
    log.trace("Configuring SATA controller " "sata_controller_label=%s", sata_controller_label)
    sata_spec = vim.vm.device.VirtualDeviceSpec()
    sata_spec.device = vim.vm.device.VirtualAHCIController()
    if operation == "add":
        sata_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    elif operation == "edit":
        sata_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
    sata_spec.device.key = key
    sata_spec.device.controllerKey = 100
    sata_spec.device.busNumber = bus_number
    if sata_controller_label:
        sata_spec.device.deviceInfo = vim.Description()
        sata_spec.device.deviceInfo.label = sata_controller_label
        sata_spec.device.deviceInfo.summary = sata_controller_label
    return sata_spec


def _apply_cd_drive(
    drive_label,
    key,
    device_type,
    operation,
    client_device=None,
    datastore_iso_file=None,
    connectable=None,
    controller_key=200,
    parent_ref=None,
):
    """
    Returns a vim.vm.device.VirtualDeviceSpec object specifying to add/edit a
    CD/DVD drive

    drive_label
        Leble of the CD/DVD drive

    key
        Unique key of the device

    device_type
        Type of the device: client or iso

    operation
        Type of operation: add or edit

    client_device
        Client device properties

    datastore_iso_file
        ISO properties

    connectable
        Connection info for the device

    controller_key
        Controller unique identifier to which we will attach this device

    parent_ref
        Parent object

    .. code-block:: bash

        cd:
            adapter: "CD/DVD drive 1"
            device_type: datastore_iso_file or client_device
            client_device:
              mode: atapi or passthrough
            datastore_iso_file:
              path: "[share] iso/disk.iso"
            connectable:
              start_connected: True
              allow_guest_control:
    """
    log.trace(
        "Configuring CD/DVD drive drive_label=%s "
        "device_type=%s client_device=%s "
        "datastore_iso_file=%s",
        drive_label,
        device_type,
        client_device,
        datastore_iso_file,
    )
    drive_spec = vim.vm.device.VirtualDeviceSpec()
    drive_spec.device = vim.vm.device.VirtualCdrom()
    drive_spec.device.deviceInfo = vim.Description()
    if operation == "add":
        drive_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    elif operation == "edit":
        drive_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
    if device_type == "datastore_iso_file":
        drive_spec.device.backing = vim.vm.device.VirtualCdrom.IsoBackingInfo()
        drive_spec.device.backing.fileName = datastore_iso_file["path"]
        datastore = datastore_iso_file["path"].partition("[")[-1].rpartition("]")[0]
        datastore_object = saltext.vmware.utils.vmware.get_datastores(
            saltext.vmware.utils.vmware.get_service_instance_from_managed_object(parent_ref),
            parent_ref,
            datastore_names=[datastore],
        )[0]
        if datastore_object:
            drive_spec.device.backing.datastore = datastore_object
        drive_spec.device.deviceInfo.summary = "{}".format(datastore_iso_file["path"])
    elif device_type == "client_device":
        if client_device["mode"] == "passthrough":
            drive_spec.device.backing = vim.vm.device.VirtualCdrom.RemotePassthroughBackingInfo()
        elif client_device["mode"] == "atapi":
            drive_spec.device.backing = vim.vm.device.VirtualCdrom.RemoteAtapiBackingInfo()
    drive_spec.device.key = key
    drive_spec.device.deviceInfo.label = drive_label
    drive_spec.device.controllerKey = controller_key
    drive_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    if connectable:
        drive_spec.device.connectable.startConnected = connectable["start_connected"]
        drive_spec.device.connectable.allowGuestControl = connectable["allow_guest_control"]
    return drive_spec


def _apply_hard_disk(
    unit_number,
    key,
    operation,
    disk_label=None,
    size=None,
    unit="GB",
    controller_key=None,
    thin_provision=None,
    eagerly_scrub=None,
    datastore=None,
    filename=None,
):
    """
    Returns a vim.vm.device.VirtualDeviceSpec object specifying to add/edit
    a virtual disk device

    unit_number
        Add network adapter to this address

    key
        Device key number

    operation
        Action which should be done on the device add or edit

    disk_label
        Label of the new disk, can be overridden

    size
        Size of the disk

    unit
        Unit of the size, can be GB, MB, KB

    controller_key
        Unique umber of the controller key

    thin_provision
        Boolean for thin provision

    eagerly_scrub
        Boolean for eagerly scrubbing

    datastore
        Datastore name where the disk will be located

    filename
        Full file name of the vm disk
    """
    log.trace(
        "Configuring hard disk %s size={}, unit={}, "
        "controller_key=%s, thin_provision={}, "
        "eagerly_scrub=%s, datastore={}, "
        "filename=%s",
        disk_label,
        size,
        unit,
        controller_key,
        thin_provision,
        eagerly_scrub,
        datastore,
        filename,
    )
    disk_spec = vim.vm.device.VirtualDeviceSpec()
    disk_spec.device = vim.vm.device.VirtualDisk()
    disk_spec.device.key = key
    disk_spec.device.unitNumber = unit_number
    disk_spec.device.deviceInfo = vim.Description()
    if size:
        convert_size = saltext.vmware.utils.vmware.convert_to_kb(unit, size)
        disk_spec.device.capacityInKB = convert_size["size"]
    if disk_label:
        disk_spec.device.deviceInfo.label = disk_label
    if thin_provision is not None or eagerly_scrub is not None:
        disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
        disk_spec.device.backing.diskMode = "persistent"
    if thin_provision is not None:
        disk_spec.device.backing.thinProvisioned = thin_provision
    if eagerly_scrub is not None and eagerly_scrub != "None":
        disk_spec.device.backing.eagerlyScrub = eagerly_scrub
    if controller_key:
        disk_spec.device.controllerKey = controller_key
    if operation == "add":
        disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
        disk_spec.device.backing.fileName = "[{}] {}".format(
            saltext.vmware.utils.vmware.get_managed_object_name(datastore), filename
        )
        disk_spec.fileOperation = vim.vm.device.VirtualDeviceSpec.FileOperation.create
    elif operation == "edit":
        disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
    return disk_spec


def _create_disks(service_instance, disks, scsi_controllers=None, parent=None):
    """
    Returns a list of disk specs representing the disks to be created for a
    virtual machine

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.
        Default is None.

    disks
        List of disks with properties

    scsi_controllers
        List of SCSI controllers

    parent
        Parent object reference

    .. code-block:: bash

        disk:
          adapter: 'Hard disk 1'
          size: 16
          unit: GB
          address: '0:0'
          controller: 'SCSI controller 0'
          thin_provision: False
          eagerly_scrub: False
          datastore: 'myshare'
          filename: 'vm/mydisk.vmdk'
    """
    disk_specs = []
    keys = range(-2000, -2050, -1)
    if disks:
        devs = [disk["adapter"] for disk in disks]
        log.trace("Creating disks %s", devs)
    for disk, key in zip(disks, keys):
        # create the disk
        filename, datastore, datastore_ref = None, None, None
        size = float(disk["size"])
        # when creating both SCSI controller and Hard disk at the same time
        # we need the randomly assigned (temporary) key of the newly created
        # SCSI controller
        controller_key = 1000  # Default is the first SCSI controller
        if "address" in disk:  # 0:0
            controller_bus_number, unit_number = disk["address"].split(":")
            controller_bus_number = int(controller_bus_number)
            unit_number = int(unit_number)
            controller_key = _get_scsi_controller_key(
                controller_bus_number, scsi_ctrls=scsi_controllers
            )
        elif "controller" in disk:
            for contr in scsi_controllers:
                if contr["label"] == disk["controller"]:
                    controller_key = contr["key"]
                    break
            else:
                raise salt.exceptions.VMwareObjectNotFoundError(
                    "The given controller does not exist: " "{}".format(disk["controller"])
                )
        if "datastore" in disk:
            datastore_ref = saltext.vmware.utils.vmware.get_datastores(
                service_instance, parent, datastore_names=[disk["datastore"]]
            )[0]
            datastore = disk["datastore"]
        if "filename" in disk:
            filename = disk["filename"]
        # XOR filename, datastore
        if (not filename and datastore) or (filename and not datastore):
            raise salt.exceptions.ArgumentValueError(
                "You must specify both filename and datastore attributes"
                " to place your disk to a specific datastore "
                "{}, {}".format(datastore, filename)
            )
        disk_spec = _apply_hard_disk(
            unit_number,
            key,
            disk_label=disk["adapter"],
            size=size,
            unit=disk["unit"],
            controller_key=controller_key,
            operation="add",
            thin_provision=disk["thin_provision"],
            eagerly_scrub=disk["eagerly_scrub"] if "eagerly_scrub" in disk else None,
            datastore=datastore_ref,
            filename=filename,
        )
        disk_specs.append(disk_spec)
        unit_number += 1
    return disk_specs


def _create_scsi_devices(scsi_devices):
    """
    Returns a list of vim.vm.device.VirtualDeviceSpec objects representing
    SCSI controllers

    scsi_devices:
        List of SCSI device properties
    """
    keys = range(-1000, -1050, -1)
    scsi_specs = []
    if scsi_devices:
        devs = [scsi["adapter"] for scsi in scsi_devices]
        log.trace("Creating SCSI devices %s", devs)
        # unitNumber for disk attachment, 0:0 1st 0 is the controller busNumber,
        # 2nd is the unitNumber
        for (key, scsi_controller) in zip(keys, scsi_devices):
            # create the SCSI controller
            scsi_spec = _apply_scsi_controller(
                scsi_controller["adapter"],
                scsi_controller["type"],
                scsi_controller["bus_sharing"],
                key,
                scsi_controller["bus_number"],
                "add",
            )
            scsi_specs.append(scsi_spec)
    return scsi_specs


def _create_network_adapters(network_interfaces, parent=None):
    """
    Returns a list of vim.vm.device.VirtualDeviceSpec objects representing
    the interfaces to be created for a virtual machine

    network_interfaces
        List of network interfaces and properties

    parent
        Parent object reference

    .. code-block:: bash

        interfaces:
          adapter: 'Network adapter 1'
          name: vlan100
          switch_type: distributed or standard
          adapter_type: vmxnet3 or vmxnet, vmxnet2, vmxnet3, e1000, e1000e
          mac: '00:11:22:33:44:55'
    """
    network_specs = []
    nics_settings = []
    keys = range(-4000, -4050, -1)
    if network_interfaces:
        devs = [inter["adapter"] for inter in network_interfaces]
        log.trace("Creating network interfaces %s", devs)
        for interface, key in zip(network_interfaces, keys):
            network_spec = _apply_network_adapter_config(
                key,
                interface["name"],
                interface["adapter_type"],
                interface["switch_type"],
                network_adapter_label=interface["adapter"],
                operation="add",
                connectable=interface["connectable"] if "connectable" in interface else None,
                mac=interface["mac"],
                parent=parent,
            )
            network_specs.append(network_spec)
            if "mapping" in interface:
                adapter_mapping = _set_network_adapter_mapping(
                    interface["mapping"]["domain"],
                    interface["mapping"]["gateway"],
                    interface["mapping"]["ip_addr"],
                    interface["mapping"]["subnet_mask"],
                    interface["mac"],
                )
                nics_settings.append(adapter_mapping)
    return (network_specs, nics_settings)


def _apply_serial_port(serial_device_spec, key, operation="add"):
    """
    Returns a vim.vm.device.VirtualSerialPort representing a serial port
    component

    serial_device_spec
        Serial device properties

    key
        Unique key of the device

    operation
        Add or edit the given device

    .. code-block:: bash

        serial_ports:
            adapter: 'Serial port 1'
            backing:
              type: uri
              uri: 'telnet://something:port'
              direction: <client|server>
              filename: 'service_uri'
            connectable:
              allow_guest_control: True
              start_connected: True
            yield: False
    """
    log.trace(
        "Creating serial port adapter=%s type=%s connectable=%s " "yield=%s",
        serial_device_spec["adapter"],
        serial_device_spec["type"],
        serial_device_spec["connectable"],
        serial_device_spec["yield"],
    )
    device_spec = vim.vm.device.VirtualDeviceSpec()
    device_spec.device = vim.vm.device.VirtualSerialPort()
    if operation == "add":
        device_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    elif operation == "edit":
        device_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
    connect_info = vim.vm.device.VirtualDevice.ConnectInfo()
    type_backing = None

    if serial_device_spec["type"] == "network":
        type_backing = vim.vm.device.VirtualSerialPort.URIBackingInfo()
        if "uri" not in serial_device_spec["backing"].keys():
            raise ValueError("vSPC proxy URI not specified in config")
        if "uri" not in serial_device_spec["backing"].keys():
            raise ValueError("vSPC Direction not specified in config")
        if "filename" not in serial_device_spec["backing"].keys():
            raise ValueError("vSPC Filename not specified in config")
        type_backing.proxyURI = serial_device_spec["backing"]["uri"]
        type_backing.direction = serial_device_spec["backing"]["direction"]
        type_backing.serviceURI = serial_device_spec["backing"]["filename"]
    if serial_device_spec["type"] == "pipe":
        type_backing = vim.vm.device.VirtualSerialPort.PipeBackingInfo()
    if serial_device_spec["type"] == "file":
        type_backing = vim.vm.device.VirtualSerialPort.FileBackingInfo()
    if serial_device_spec["type"] == "device":
        type_backing = vim.vm.device.VirtualSerialPort.DeviceBackingInfo()
    connect_info.allowGuestControl = serial_device_spec["connectable"]["allow_guest_control"]
    connect_info.startConnected = serial_device_spec["connectable"]["start_connected"]
    device_spec.device.backing = type_backing
    device_spec.device.connectable = connect_info
    device_spec.device.unitNumber = 1
    device_spec.device.key = key
    device_spec.device.yieldOnPoll = serial_device_spec["yield"]

    return device_spec


def _create_serial_ports(serial_ports):
    """
    Returns a list of vim.vm.device.VirtualDeviceSpec objects representing the
    serial ports to be created for a virtual machine

    serial_ports
        Serial port properties
    """
    ports = []
    keys = range(-9000, -9050, -1)
    if serial_ports:
        devs = [serial["adapter"] for serial in serial_ports]
        log.trace("Creating serial ports %s", devs)
        for port, key in zip(serial_ports, keys):
            serial_port_device = _apply_serial_port(port, key, "add")
            ports.append(serial_port_device)
    return ports


def _create_cd_drives(cd_drives, controllers=None, parent_ref=None):
    """
    Returns a list of vim.vm.device.VirtualDeviceSpec objects representing the
    CD/DVD drives to be created for a virtual machine

    cd_drives
        CD/DVD drive properties

    controllers
        CD/DVD drive controllers (IDE, SATA)

    parent_ref
        Parent object reference
    """
    cd_drive_specs = []
    keys = range(-3000, -3050, -1)
    if cd_drives:
        devs = [dvd["adapter"] for dvd in cd_drives]
        log.trace("Creating cd/dvd drives %s", devs)
        for drive, key in zip(cd_drives, keys):
            # if a controller is not available/cannot be created we should use the
            #  one which is available by default, this is 'IDE 0'
            controller_key = 200
            if controllers:
                controller = _get_device_by_label(controllers, drive["controller"])
                controller_key = controller.key
            cd_drive_specs.append(
                _apply_cd_drive(
                    drive["adapter"],
                    key,
                    drive["device_type"],
                    "add",
                    client_device=drive["client_device"] if "client_device" in drive else None,
                    datastore_iso_file=drive["datastore_iso_file"]
                    if "datastore_iso_file" in drive
                    else None,
                    connectable=drive["connectable"] if "connectable" in drive else None,
                    controller_key=controller_key,
                    parent_ref=parent_ref,
                )
            )

    return cd_drive_specs


def _update_disks(disks_old_new):
    """
    Changes the disk size and returns the config spec objects in a list.
    The controller property cannot be updated, because controller address
    identifies the disk by the unit and bus number properties.

    disks_diffs
        List of old and new disk properties, the properties are dictionary
        objects
    """
    disk_changes = []
    if disks_old_new:
        devs = [disk["old"]["address"] for disk in disks_old_new]
        log.trace("Updating disks %s", devs)
        for item in disks_old_new:
            current_disk = item["old"]
            next_disk = item["new"]
            difference = recursive_diff(current_disk, next_disk)
            difference.ignore_unset_values = False
            if difference.changed():
                if next_disk["size"] < current_disk["size"]:
                    raise salt.exceptions.VMwareSaltError(
                        "Disk cannot be downsized size={} unit={} "
                        "controller_key={} "
                        "unit_number={}".format(
                            next_disk["size"],
                            next_disk["unit"],
                            current_disk["controller_key"],
                            current_disk["unit_number"],
                        )
                    )
                log.trace(
                    "Virtual machine disk will be updated "
                    "size=%s unit=%s controller_key=%s "
                    "unit_number=%s",
                    next_disk["size"],
                    next_disk["unit"],
                    current_disk["controller_key"],
                    current_disk["unit_number"],
                )
                device_config_spec = _apply_hard_disk(
                    current_disk["unit_number"],
                    current_disk["key"],
                    "edit",
                    size=next_disk["size"],
                    unit=next_disk["unit"],
                    controller_key=current_disk["controller_key"],
                )
                # The backing didn't change and we must supply one for
                # reconfigure
                device_config_spec.device.backing = current_disk["object"].backing
                disk_changes.append(device_config_spec)

    return disk_changes


def _update_scsi_devices(scsis_old_new, current_disks):
    """
    Returns a list of vim.vm.device.VirtualDeviceSpec specifying  the scsi
    properties as input the old and new configs are defined in a dictionary.

    scsi_diffs
        List of old and new scsi properties
    """
    device_config_specs = []
    if scsis_old_new:
        devs = [scsi["old"]["adapter"] for scsi in scsis_old_new]
        log.trace("Updating SCSI controllers %s", devs)
        for item in scsis_old_new:
            next_scsi = item["new"]
            current_scsi = item["old"]
            difference = recursive_diff(current_scsi, next_scsi)
            difference.ignore_unset_values = False
            if difference.changed():
                log.trace(
                    "Virtual machine scsi device will be updated "
                    "key=%s bus_number=%s type=%s "
                    "bus_sharing=%s",
                    current_scsi["key"],
                    current_scsi["bus_number"],
                    next_scsi["type"],
                    next_scsi["bus_sharing"],
                )
                # The sharedBus property is not optional
                # The type can only be updated if we delete the original
                # controller, create a new one with the properties and then
                # attach the disk object to the newly created controller, even
                # though the controller key stays the same the last step is
                # mandatory
                if next_scsi["type"] != current_scsi["type"]:
                    device_config_specs.append(_delete_device(current_scsi["object"]))
                    device_config_specs.append(
                        _apply_scsi_controller(
                            current_scsi["adapter"],
                            next_scsi["type"],
                            next_scsi["bus_sharing"],
                            current_scsi["key"],
                            current_scsi["bus_number"],
                            "add",
                        )
                    )
                    disks_to_update = []
                    for disk_key in current_scsi["device"]:
                        disk_objects = [disk["object"] for disk in current_disks]
                        disks_to_update.append(_get_device_by_key(disk_objects, disk_key))
                    for current_disk in disks_to_update:
                        disk_spec = vim.vm.device.VirtualDeviceSpec()
                        disk_spec.device = current_disk
                        disk_spec.operation = "edit"
                        device_config_specs.append(disk_spec)
                else:
                    device_config_specs.append(
                        _apply_scsi_controller(
                            current_scsi["adapter"],
                            current_scsi["type"],
                            next_scsi["bus_sharing"],
                            current_scsi["key"],
                            current_scsi["bus_number"],
                            "edit",
                        )
                    )
    return device_config_specs


def _update_network_adapters(interface_old_new, parent):
    """
    Returns a list of vim.vm.device.VirtualDeviceSpec specifying
    configuration(s) for changed network adapters, the adapter type cannot
    be changed, as input the old and new configs are defined in a dictionary.

    interface_old_new
        Dictionary with old and new keys which contains the current and the
        next config for a network device

    parent
        Parent managed object reference
    """
    network_changes = []
    if interface_old_new:
        devs = [inter["old"]["mac"] for inter in interface_old_new]
        log.trace("Updating network interfaces %s", devs)
        for item in interface_old_new:
            current_interface = item["old"]
            next_interface = item["new"]
            difference = recursive_diff(current_interface, next_interface)
            difference.ignore_unset_values = False
            if difference.changed():
                log.trace(
                    "Virtual machine network adapter will be updated "
                    "switch_type=%s name=%s adapter_type=%s "
                    "mac=%s",
                    next_interface["switch_type"],
                    next_interface["name"],
                    current_interface["adapter_type"],
                    current_interface["mac"],
                )
                device_config_spec = _apply_network_adapter_config(
                    current_interface["key"],
                    next_interface["name"],
                    current_interface["adapter_type"],
                    next_interface["switch_type"],
                    operation="edit",
                    mac=current_interface["mac"],
                    parent=parent,
                )
                network_changes.append(device_config_spec)
    return network_changes


def _update_serial_ports(serial_old_new):
    """
    Returns a list of vim.vm.device.VirtualDeviceSpec specifying to edit a
    deployed serial port configuration to the new given config

    serial_old_new
         Dictionary with old and new keys which contains the current and the
          next config for a serial port device
    """
    serial_changes = []
    if serial_old_new:
        devs = [serial["old"]["adapter"] for serial in serial_old_new]
        log.trace("Updating serial ports %s", devs)
        for item in serial_old_new:
            current_serial = item["old"]
            next_serial = item["new"]
            difference = recursive_diff(current_serial, next_serial)
            difference.ignore_unset_values = False
            if difference.changed():
                serial_changes.append(
                    _apply_serial_port(next_serial, current_serial["key"], "edit")
                )
        return serial_changes


def _update_cd_drives(drives_old_new, controllers=None, parent=None):
    """
    Returns a list of vim.vm.device.VirtualDeviceSpec specifying to edit a
    deployed cd drive configuration to the new given config

    drives_old_new
        Dictionary with old and new keys which contains the current and the
        next config for a cd drive

    controllers
        Controller device list

    parent
        Managed object reference of the parent object
    """
    cd_changes = []
    if drives_old_new:
        devs = [drive["old"]["adapter"] for drive in drives_old_new]
        log.trace("Updating cd/dvd drives %s", devs)
        for item in drives_old_new:
            current_drive = item["old"]
            new_drive = item["new"]
            difference = recursive_diff(current_drive, new_drive)
            difference.ignore_unset_values = False
            if difference.changed():
                if controllers:
                    controller = _get_device_by_label(controllers, new_drive["controller"])
                    controller_key = controller.key
                else:
                    controller_key = current_drive["controller_key"]
                cd_changes.append(
                    _apply_cd_drive(
                        current_drive["adapter"],
                        current_drive["key"],
                        new_drive["device_type"],
                        "edit",
                        client_device=new_drive["client_device"]
                        if "client_device" in new_drive
                        else None,
                        datastore_iso_file=new_drive["datastore_iso_file"]
                        if "datastore_iso_file" in new_drive
                        else None,
                        connectable=new_drive["connectable"],
                        controller_key=controller_key,
                        parent_ref=parent,
                    )
                )
    return cd_changes


def _delete_device(device):
    """
    Returns a vim.vm.device.VirtualDeviceSpec specifying to remove a virtual
    machine device

    device
        Device data type object
    """
    log.trace("Deleting device with type %s", type(device))
    device_spec = vim.vm.device.VirtualDeviceSpec()
    device_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.remove
    device_spec.device = device
    return device_spec


@depends(HAS_PYVMOMI)
def power_on_vm(
    name,
    datacenter=None,
    host=None,
    vcenter=None,
    username=None,
    password=None,
    protocol=None,
    port=None,
    verify_ssl=True,
):
    """
    Powers on a virtual machine specified by its name.

    name
        Name of the virtual machine

    datacenter
        Datacenter of the virtual machine

    host
        The location of the host if using ESXI.

    vcenter
        The location of the host if using VCenter.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    verify_ssl
        Verify the SSL certificate. Default: True

    .. code-block:: bash

        salt '*' vsphere.power_on_vm name=my_vm

    """
    if salt.utils.platform.is_proxy():
        details = __salt__["vmware_info.get_proxy_connection_details"]()
    else:
        details = __salt__["vmware_info.get_connection_details"](
            host=host,
            vcenter=vcenter,
            username=username,
            password=password,
            protocol=protocol,
            port=port,
            verify_ssl=verify_ssl,
        )
    service_instance = saltext.vmware.utils.vmware.get_service_instance(**details)

    log.trace("Powering on virtual machine %s", name)
    vm_properties = ["name", "summary.runtime.powerState"]
    virtual_machine = saltext.vmware.utils.vmware.get_vm_by_property(
        service_instance, name, datacenter=datacenter, vm_properties=vm_properties
    )
    if virtual_machine["summary.runtime.powerState"] == "poweredOn":
        result = {
            "comment": "Virtual machine is already powered on",
            "changes": {"power_on": True},
        }
        return result
    saltext.vmware.utils.vmware.power_cycle_vm(virtual_machine["object"], action="on")
    result = {
        "comment": "Virtual machine power on action succeeded",
        "changes": {"power_on": True},
    }
    return result


@depends(HAS_PYVMOMI)
def power_off_vm(
    name,
    datacenter=None,
    host=None,
    vcenter=None,
    username=None,
    password=None,
    protocol=None,
    port=None,
    verify_ssl=True,
):
    """
    Powers off a virtual machine specified by its name.

    name
        Name of the virtual machine

    datacenter
        Datacenter of the virtual machine

    host
        The location of the host if using ESXI.

    vcenter
        The location of the host if using VCenter.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    verify_ssl
        Verify the SSL certificate. Default: True

    .. code-block:: bash

        salt '*' vsphere.power_off_vm name=my_vm

    """
    if salt.utils.platform.is_proxy():
        details = __salt__["vmware_info.get_proxy_connection_details"]()
    else:
        details = __salt__["vmware_info.get_connection_details"](
            host=host,
            vcenter=vcenter,
            username=username,
            password=password,
            protocol=protocol,
            port=port,
            verify_ssl=verify_ssl,
        )
    service_instance = saltext.vmware.utils.vmware.get_service_instance(**details)

    log.trace("Powering off virtual machine %s", name)
    vm_properties = ["name", "summary.runtime.powerState"]
    virtual_machine = saltext.vmware.utils.vmware.get_vm_by_property(
        service_instance, name, datacenter=datacenter, vm_properties=vm_properties
    )
    if virtual_machine["summary.runtime.powerState"] == "poweredOff":
        result = {
            "comment": "Virtual machine is already powered off",
            "changes": {"power_off": True},
        }
        return result
    saltext.vmware.utils.vmware.power_cycle_vm(virtual_machine["object"], action="off")
    result = {
        "comment": "Virtual machine power off action succeeded",
        "changes": {"power_off": True},
    }
    return result


@depends(HAS_PYVMOMI)
def list_vms(
    host=None, vcenter=None, username=None, password=None, protocol=None, port=None, verify_ssl=True
):
    """
    Returns a list of VMs for the specified host.

    host
        The location of the host if using ESXI.

    vcenter
        The location of the host if using VCenter.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        salt '*' vsphere.list_vms host=1.2.3.4 username=root password=bad-password
    """
    if salt.utils.platform.is_proxy():
        details = __salt__["vmware_info.get_proxy_connection_details"]()
    else:
        details = __salt__["vmware_info.get_connection_details"](
            host=host,
            vcenter=vcenter,
            username=username,
            password=password,
            protocol=protocol,
            port=port,
            verify_ssl=verify_ssl,
        )
    service_instance = saltext.vmware.utils.vmware.get_service_instance(**details)

    return saltext.vmware.utils.vmware.list_vms(service_instance)


@depends(HAS_PYVMOMI)
def delete_vm(
    name,
    datacenter,
    placement=None,
    power_off=False,
    host=None,
    vcenter=None,
    username=None,
    password=None,
    protocol=None,
    port=None,
    verify_ssl=True,
):
    """
    Deletes a virtual machine defined by name and placement

    name
        Name of the virtual machine

    datacenter
        Datacenter of the virtual machine

    placement
        Placement information of the virtual machine

    host
        The location of the host.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    verify_ssl
        Verify the SSL certificate. Default: True

    .. code-block:: bash

        salt '*' vsphere.delete_vm name=my_vm datacenter=my_datacenter

    """
    if salt.utils.platform.is_proxy():
        details = __salt__["vmware_info.get_proxy_connection_details"]()
    else:
        details = __salt__["vmware_info.get_connection_details"](
            host=host,
            vcenter=vcenter,
            username=username,
            password=password,
            protocol=protocol,
            port=port,
            verify_ssl=verify_ssl,
        )
    service_instance = saltext.vmware.utils.vmware.get_service_instance(**details)

    results = {}
    schema = ESXVirtualMachineDeleteSchema.serialize()
    try:
        jsonschema.validate(
            {"name": name, "datacenter": datacenter, "placement": placement}, schema
        )
    except jsonschema.exceptions.ValidationError as exc:
        raise InvalidConfigError(exc) from exc
    (results, vm_ref) = _remove_vm(
        name,
        datacenter,
        service_instance=service_instance,
        placement=placement,
        power_off=power_off,
    )
    saltext.vmware.utils.vmware.delete_vm(vm_ref)
    results["deleted_vm"] = True
    return results


@depends(HAS_PYVMOMI)
def create_vm(
    vm_name,
    cpu,
    memory,
    image,
    version,
    datacenter,
    datastore,
    placement,
    interfaces,
    disks,
    scsi_devices,
    serial_ports=None,
    ide_controllers=None,
    sata_controllers=None,
    cd_drives=None,
    advanced_configs=None,
    host=None,
    vcenter=None,
    username=None,
    password=None,
    protocol=None,
    port=None,
    verify_ssl=True,
):
    """
    Creates a virtual machine container.

    CLI Example:

    .. code-block:: bash

        salt vm_minion vsphere.create_vm vm_name=vmname cpu='{count: 2, nested: True}' ...

    vm_name
        Name of the virtual machine

    cpu
        Properties of CPUs for freshly created machines

    memory
        Memory size for freshly created machines

    image
        Virtual machine guest OS version identifier
        VirtualMachineGuestOsIdentifier

    version
        Virtual machine container hardware version

    datacenter
        Datacenter where the virtual machine will be deployed (mandatory)

    datastore
        Datastore where the virtual machine files will be placed

    placement
        Resource pool or cluster or host or folder where the virtual machine
        will be deployed

    host
        The location of the host.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    verify_ssl
        Verify the SSL certificate. Default: True

    devices
        interfaces

        .. code-block:: bash

            interfaces:
              adapter: 'Network adapter 1'
              name: vlan100
              switch_type: distributed or standard
              adapter_type: vmxnet3 or vmxnet, vmxnet2, vmxnet3, e1000, e1000e
              mac: '00:11:22:33:44:55'
              connectable:
                allow_guest_control: True
                connected: True
                start_connected: True

        disks

        .. code-block:: bash

            disks:
              adapter: 'Hard disk 1'
              size: 16
              unit: GB
              address: '0:0'
              controller: 'SCSI controller 0'
              thin_provision: False
              eagerly_scrub: False
              datastore: 'myshare'
              filename: 'vm/mydisk.vmdk'

        scsi_devices

        .. code-block:: bash

            scsi_devices:
              controller: 'SCSI controller 0'
              type: paravirtual
              bus_sharing: no_sharing

        serial_ports

        .. code-block:: bash

            serial_ports:
              adapter: 'Serial port 1'
              type: network
              backing:
                uri: 'telnet://something:port'
                direction: <client|server>
                filename: 'service_uri'
              connectable:
                allow_guest_control: True
                connected: True
                start_connected: True
              yield: False

        cd_drives

        .. code-block:: bash

            cd_drives:
              adapter: 'CD/DVD drive 0'
              controller: 'IDE 0'
              device_type: datastore_iso_file
              datastore_iso_file:
                path: path_to_iso
              connectable:
                allow_guest_control: True
                connected: True
                start_connected: True

    advanced_config
        Advanced config parameters to be set for the virtual machine
    """
    if salt.utils.platform.is_proxy():
        details = __salt__["vmware_info.get_proxy_connection_details"]()
    else:
        details = __salt__["vmware_info.get_connection_details"](
            host=host,
            vcenter=vcenter,
            username=username,
            password=password,
            protocol=protocol,
            port=port,
            verify_ssl=verify_ssl,
        )
    service_instance = saltext.vmware.utils.vmware.get_service_instance(**details)

    # If datacenter is specified, set the container reference to start search
    # from it instead
    container_object = saltext.vmware.utils.vmware.get_datacenter(service_instance, datacenter)
    (resourcepool_object, placement_object) = saltext.vmware.utils.vmware.get_placement(
        service_instance, datacenter, placement=placement
    )
    folder_object = saltext.vmware.utils.vmware.get_folder(service_instance, datacenter, placement)
    # Create the config specs
    config_spec = vim.vm.ConfigSpec()
    config_spec.name = vm_name
    config_spec.guestId = image
    config_spec.files = vim.vm.FileInfo()

    # For VSAN disks we need to specify a different vm path name, the vm file
    # full path cannot be used
    datastore_object = saltext.vmware.utils.vmware.get_datastores(
        service_instance, placement_object, datastore_names=[datastore]
    )[0]
    if not datastore_object:
        raise salt.exceptions.ArgumentValueError(
            "Specified datastore: '{}' does not exist.".format(datastore)
        )
    try:
        ds_summary = saltext.vmware.utils.vmware.get_properties_of_managed_object(
            datastore_object, "summary.type"
        )
        if "summary.type" in ds_summary and ds_summary["summary.type"] == "vsan":
            log.trace(
                "The vmPathName should be the datastore " "name if the datastore type is vsan"
            )
            config_spec.files.vmPathName = "[{}]".format(datastore)
        else:
            config_spec.files.vmPathName = "[{0}] {1}/{1}.vmx".format(datastore, vm_name)
    except salt.exceptions.VMwareApiError:
        config_spec.files.vmPathName = "[{0}] {1}/{1}.vmx".format(datastore, vm_name)

    cd_controllers = []
    if version:
        _apply_hardware_version(version, config_spec, "add")
    if cpu:
        _apply_cpu_config(config_spec, cpu)
    if memory:
        _apply_memory_config(config_spec, memory)
    if scsi_devices:
        scsi_specs = _create_scsi_devices(scsi_devices)
        config_spec.deviceChange.extend(scsi_specs)
    if disks:
        scsi_controllers = [spec.device for spec in scsi_specs]
        disk_specs = _create_disks(
            service_instance,
            disks,
            scsi_controllers=scsi_controllers,
            parent=container_object,
        )
        config_spec.deviceChange.extend(disk_specs)
    if interfaces:
        (
            interface_specs,
            nic_settings,  # pylint: disable=unused-variable
        ) = _create_network_adapters(interfaces, parent=container_object)
        config_spec.deviceChange.extend(interface_specs)
    if serial_ports:
        serial_port_specs = _create_serial_ports(serial_ports)
        config_spec.deviceChange.extend(serial_port_specs)
    if ide_controllers:
        ide_specs = _create_ide_controllers(ide_controllers)
        config_spec.deviceChange.extend(ide_specs)
        cd_controllers.extend(ide_specs)
    if sata_controllers:
        sata_specs = _create_sata_controllers(sata_controllers)
        config_spec.deviceChange.extend(sata_specs)
        cd_controllers.extend(sata_specs)
    if cd_drives:
        cd_drive_specs = _create_cd_drives(
            cd_drives, controllers=cd_controllers, parent_ref=container_object
        )
        config_spec.deviceChange.extend(cd_drive_specs)
    if advanced_configs:
        _apply_advanced_config(config_spec, advanced_configs)
    saltext.vmware.utils.vmware.create_vm(
        vm_name, config_spec, folder_object, resourcepool_object, placement_object
    )

    return {"create_vm": True}


@depends(HAS_PYVMOMI)
def update_vm(
    vm_name,
    cpu=None,
    memory=None,
    image=None,
    version=None,
    interfaces=None,
    disks=None,
    scsi_devices=None,
    serial_ports=None,
    datacenter=None,
    datastore=None,
    cd_dvd_drives=None,
    sata_controllers=None,
    advanced_configs=None,
    host=None,
    vcenter=None,
    username=None,
    password=None,
    protocol=None,
    port=None,
    verify_ssl=True,
):
    """
    Updates the configuration of the virtual machine if the config differs

    vm_name
        Virtual Machine name to be updated

    cpu
        CPU configuration options

    memory
        Memory configuration options

    version
        Virtual machine container hardware version

    image
        Virtual machine guest OS version identifier
        VirtualMachineGuestOsIdentifier

    interfaces
        Network interfaces configuration options

    disks
        Disks configuration options

    scsi_devices
        SCSI devices configuration options

    serial_ports
        Serial ports configuration options

    datacenter
        Datacenter where the virtual machine is available

    datastore
        Datastore where the virtual machine config files are available

    cd_dvd_drives
        CD/DVD drives configuration options

    advanced_config
        Advanced config parameters to be set for the virtual machine

    host
        The location of the host.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    verify_ssl
        Verify the SSL certificate. Default: True
    """

    if salt.utils.platform.is_proxy():
        details = __salt__["vmware_info.get_proxy_connection_details"]()
    else:
        details = __salt__["vmware_info.get_connection_details"](
            host=host,
            vcenter=vcenter,
            username=username,
            password=password,
            protocol=protocol,
            port=port,
            verify_ssl=verify_ssl,
        )
    service_instance = saltext.vmware.utils.vmware.get_service_instance(**details)

    current_config = get_vm_config(vm_name, datacenter=datacenter, objects=True)
    diffs = compare_vm_configs(
        {
            "name": vm_name,
            "cpu": cpu,
            "memory": memory,
            "image": image,
            "version": version,
            "interfaces": interfaces,
            "disks": disks,
            "scsi_devices": scsi_devices,
            "serial_ports": serial_ports,
            "datacenter": datacenter,
            "datastore": datastore,
            "cd_drives": cd_dvd_drives,
            "sata_controllers": sata_controllers,
            "advanced_configs": advanced_configs,
        },
        current_config,
    )
    config_spec = vim.vm.ConfigSpec()
    datacenter_ref = saltext.vmware.utils.vmware.get_datacenter(service_instance, datacenter)
    vm_ref = saltext.vmware.utils.vmware.get_mor_by_property(
        service_instance,
        vim.VirtualMachine,
        vm_name,
        property_name="name",
        container_ref=datacenter_ref,
    )

    difference_keys = diffs.keys()
    if "cpu" in difference_keys:
        if diffs["cpu"].changed() != set():
            _apply_cpu_config(config_spec, diffs["cpu"].current_dict)
    if "memory" in difference_keys:
        if diffs["memory"].changed() != set():
            _apply_memory_config(config_spec, diffs["memory"].current_dict)
    if "advanced_configs" in difference_keys:
        _apply_advanced_config(
            config_spec, diffs["advanced_configs"].new_values, vm_ref.config.extraConfig
        )
    if "version" in difference_keys:
        _apply_hardware_version(version, config_spec, "edit")
    if "image" in difference_keys:
        config_spec.guestId = image
    new_scsi_devices = []
    if "scsi_devices" in difference_keys and "disks" in current_config:
        scsi_changes = []
        scsi_changes.extend(
            _update_scsi_devices(diffs["scsi_devices"].intersect, current_config["disks"])
        )
        for item in diffs["scsi_devices"].removed:
            scsi_changes.append(_delete_device(item["object"]))
        new_scsi_devices = _create_scsi_devices(diffs["scsi_devices"].added)
        scsi_changes.extend(new_scsi_devices)
        config_spec.deviceChange.extend(scsi_changes)
    if "disks" in difference_keys:
        disk_changes = []
        disk_changes.extend(_update_disks(diffs["disks"].intersect))
        for item in diffs["disks"].removed:
            disk_changes.append(_delete_device(item["object"]))
        # We will need the existing and new controllers as well
        scsi_controllers = [dev["object"] for dev in current_config["scsi_devices"]]
        scsi_controllers.extend([device_spec.device for device_spec in new_scsi_devices])
        disk_changes.extend(
            _create_disks(
                service_instance,
                diffs["disks"].added,
                scsi_controllers=scsi_controllers,
                parent=datacenter_ref,
            )
        )
        config_spec.deviceChange.extend(disk_changes)
    if "interfaces" in difference_keys:
        network_changes = []
        network_changes.extend(
            _update_network_adapters(diffs["interfaces"].intersect, datacenter_ref)
        )
        for item in diffs["interfaces"].removed:
            network_changes.append(_delete_device(item["object"]))
        (adapters, nics) = _create_network_adapters(  # pylint: disable=unused-variable
            diffs["interfaces"].added, datacenter_ref
        )  # pylint: disable=unused-variable
        network_changes.extend(adapters)
        config_spec.deviceChange.extend(network_changes)
    if "serial_ports" in difference_keys:
        serial_changes = []
        serial_changes.extend(_update_serial_ports(diffs["serial_ports"].intersect))
        for item in diffs["serial_ports"].removed:
            serial_changes.append(_delete_device(item["object"]))
        serial_changes.extend(_create_serial_ports(diffs["serial_ports"].added))
        config_spec.deviceChange.extend(serial_changes)
    new_controllers = []
    if "sata_controllers" in difference_keys:
        # SATA controllers don't have many properties, it does not make sense
        # to update them
        sata_specs = _create_sata_controllers(diffs["sata_controllers"].added)
        for item in diffs["sata_controllers"].removed:
            sata_specs.append(_delete_device(item["object"]))
        new_controllers.extend(sata_specs)
        config_spec.deviceChange.extend(sata_specs)
    if "cd_drives" in difference_keys:
        cd_changes = []
        controllers = [dev["object"] for dev in current_config["sata_controllers"]]
        controllers.extend([device_spec.device for device_spec in new_controllers])
        cd_changes.extend(
            _update_cd_drives(
                diffs["cd_drives"].intersect,
                controllers=controllers,
                parent=datacenter_ref,
            )
        )
        for item in diffs["cd_drives"].removed:
            cd_changes.append(_delete_device(item["object"]))
        cd_changes.extend(
            _create_cd_drives(
                diffs["cd_drives"].added,
                controllers=controllers,
                parent_ref=datacenter_ref,
            )
        )
        config_spec.deviceChange.extend(cd_changes)

    if difference_keys:
        saltext.vmware.utils.vmware.update_vm(vm_ref, config_spec)
    changes = {}
    for key, properties in diffs.items():
        # We can't display object, although we will need them for delete
        # and update actions, we will need to delete these before we summarize
        # the changes for the users
        if isinstance(properties, salt.utils.listdiffer.ListDictDiffer):
            properties.remove_diff(diff_key="object", diff_list="intersect")
            properties.remove_diff(diff_key="key", diff_list="intersect")
            properties.remove_diff(diff_key="object", diff_list="removed")
            properties.remove_diff(diff_key="key", diff_list="removed")
        changes[key] = properties.diffs

    return changes


@depends(HAS_PYVMOMI)
def register_vm(
    name,
    datacenter,
    placement,
    vmx_path,
    host=None,
    vcenter=None,
    username=None,
    password=None,
    protocol=None,
    port=None,
    verify_ssl=True,
):
    """
    Registers a virtual machine to the inventory with the given vmx file.
    Returns comments and change list

    name
        Name of the virtual machine

    datacenter
        Datacenter of the virtual machine

    placement
        Placement dictionary of the virtual machine, host or cluster

    vmx_path:
        Full path to the vmx file, datastore name should be included

    host
        The location of the host.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    verify_ssl
        Verify the SSL certificate. Default: True
    """
    if salt.utils.platform.is_proxy():
        details = __salt__["vmware_info.get_proxy_connection_details"]()
    else:
        details = __salt__["vmware_info.get_connection_details"](
            host=host,
            vcenter=vcenter,
            username=username,
            password=password,
            protocol=protocol,
            port=port,
            verify_ssl=verify_ssl,
        )
    service_instance = saltext.vmware.utils.vmware.get_service_instance(**details)

    log.trace(
        "Registering virtual machine with properties "
        "datacenter=%s, placement={}, "
        "vmx_path=%s",
        datacenter,
        placement,
        vmx_path,
    )
    datacenter_object = saltext.vmware.utils.vmware.get_datacenter(service_instance, datacenter)
    if "cluster" in placement:
        cluster_obj = saltext.vmware.utils.vmware.get_cluster(
            datacenter_object, placement["cluster"]
        )
        cluster_props = saltext.vmware.utils.vmware.get_properties_of_managed_object(
            cluster_obj, properties=["resourcePool"]
        )
        if "resourcePool" in cluster_props:
            resourcepool = cluster_props["resourcePool"]
        else:
            raise salt.exceptions.VMwareObjectRetrievalError(
                "The cluster's resource pool object could not be retrieved."
            )
        saltext.vmware.utils.vmware.register_vm(datacenter_object, name, vmx_path, resourcepool)
    elif "host" in placement:
        hosts = saltext.vmware.utils.vmware.get_hosts(
            service_instance, datacenter_name=datacenter, host_names=[placement["host"]]
        )
        if not hosts:
            raise salt.exceptions.VMwareObjectRetrievalError(
                "ESXi host named '{}' wasn't found.".format(placement["host"])
            )
        host_obj = hosts[0]
        host_props = saltext.vmware.utils.vmware.get_properties_of_managed_object(
            host_obj, properties=["parent"]
        )
        if "parent" in host_props:
            host_parent = host_props["parent"]
            parent = saltext.vmware.utils.vmware.get_properties_of_managed_object(
                host_parent, properties=["parent"]
            )
            if "parent" in parent:
                resourcepool = parent["parent"]
            else:
                raise salt.exceptions.VMwareObjectRetrievalError(
                    "The host parent's parent object could not be retrieved."
                )
        else:
            raise salt.exceptions.VMwareObjectRetrievalError(
                "The host's parent object could not be retrieved."
            )
        saltext.vmware.utils.vmware.register_vm(
            datacenter_object, name, vmx_path, resourcepool, host_object=host_obj
        )
    result = {
        "comment": "Virtual machine registration action succeeded",
        "changes": {"register_vm": True},
    }
    return result


def _remove_vm(name, datacenter, service_instance, placement=None, power_off=None):
    """
    Helper function to remove a virtual machine

    name
        Name of the virtual machine

    service_instance
        vCenter service instance for connection and configuration

    datacenter
        Datacenter of the virtual machine

    placement
        Placement information of the virtual machine
    """
    results = {}
    if placement:
        (
            resourcepool_object,  # pylint: disable=unused-variable
            placement_object,
        ) = saltext.vmware.utils.vmware.get_placement(service_instance, datacenter, placement)
    else:
        placement_object = saltext.vmware.utils.vmware.get_datacenter(service_instance, datacenter)
    if power_off:
        power_off_vm(name, datacenter, service_instance)
        results["powered_off"] = True
    vm_ref = saltext.vmware.utils.vmware.get_mor_by_property(
        service_instance,
        vim.VirtualMachine,
        name,
        property_name="name",
        container_ref=placement_object,
    )
    if not vm_ref:
        raise salt.exceptions.VMwareObjectRetrievalError(
            "The virtual machine object {} in datacenter "
            "{} was not found".format(name, datacenter)
        )
    return results, vm_ref


@depends(HAS_PYVMOMI)
def unregister_vm(
    name,
    datacenter,
    placement=None,
    power_off=False,
    host=None,
    vcenter=None,
    username=None,
    password=None,
    protocol=None,
    port=None,
    verify_ssl=True,
):
    """
    Unregisters a virtual machine defined by name and placement

    name
        Name of the virtual machine

    datacenter
        Datacenter of the virtual machine

    placement
        Placement information of the virtual machine

    host
        The location of the host.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    verify_ssl
        Verify the SSL certificate. Default: True

    .. code-block:: bash

        salt '*' vsphere.unregister_vm name=my_vm datacenter=my_datacenter

    """
    if salt.utils.platform.is_proxy():
        details = __salt__["vmware_info.get_proxy_connection_details"]()
    else:
        details = __salt__["vmware_info.get_connection_details"](
            host=host,
            vcenter=vcenter,
            username=username,
            password=password,
            protocol=protocol,
            port=port,
            verify_ssl=verify_ssl,
        )
    service_instance = saltext.vmware.utils.vmware.get_service_instance(**details)

    results = {}
    schema = ESXVirtualMachineUnregisterSchema.serialize()
    try:
        jsonschema.validate(
            {"name": name, "datacenter": datacenter, "placement": placement}, schema
        )
    except jsonschema.exceptions.ValidationError as exc:
        raise InvalidConfigError(exc) from exc
    (results, vm_ref) = _remove_vm(
        name,
        datacenter,
        service_instance=service_instance,
        placement=placement,
        power_off=power_off,
    )
    saltext.vmware.utils.vmware.unregister_vm(vm_ref)
    results["unregistered_vm"] = True
    return results


@depends(HAS_PYVMOMI)
def get_vm(
    name,
    datacenter=None,
    vm_properties=None,
    traversal_spec=None,
    parent_ref=None,
    host=None,
    vcenter=None,
    username=None,
    password=None,
    protocol=None,
    port=None,
    verify_ssl=True,
):
    """
    Returns vm object properties.

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

    host
        The location of the host.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    verify_ssl
        Verify the SSL certificate. Default: True
    """
    if salt.utils.platform.is_proxy():
        details = __salt__["vmware_info.get_proxy_connection_details"]()
    else:
        details = __salt__["vmware_info.get_connection_details"](
            host=host,
            vcenter=vcenter,
            username=username,
            password=password,
            protocol=protocol,
            port=port,
            verify_ssl=verify_ssl,
        )
    service_instance = saltext.vmware.utils.vmware.get_service_instance(**details)

    virtual_machine = saltext.vmware.utils.vmware.get_vm_by_property(
        service_instance,
        name,
        datacenter=datacenter,
        vm_properties=vm_properties,
        traversal_spec=traversal_spec,
        parent_ref=parent_ref,
    )
    return virtual_machine


@depends(HAS_PYVMOMI)
def get_vm_config_file(
    name,
    datacenter,
    placement,
    datastore,
    host=None,
    vcenter=None,
    username=None,
    password=None,
    protocol=None,
    port=None,
    verify_ssl=True,
):
    """
    Queries the virtual machine config file and returns
    vim.host.DatastoreBrowser.SearchResults object on success None on failure

    name
        Name of the virtual machine

    datacenter
        Datacenter name

    datastore
        Datastore where the virtual machine files are stored

    host
        The location of the host.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    verify_ssl
        Verify the SSL certificate. Default: True
    """

    if salt.utils.platform.is_proxy():
        details = __salt__["vmware_info.get_proxy_connection_details"]()
    else:
        details = __salt__["vmware_info.get_connection_details"](
            host=host,
            vcenter=vcenter,
            username=username,
            password=password,
            protocol=protocol,
            port=port,
            verify_ssl=verify_ssl,
        )
    service_instance = saltext.vmware.utils.vmware.get_service_instance(**details)

    browser_spec = vim.host.DatastoreBrowser.SearchSpec()
    directory = name
    browser_spec.query = [vim.host.DatastoreBrowser.VmConfigQuery()]
    datacenter_object = saltext.vmware.utils.vmware.get_datacenter(service_instance, datacenter)
    if "cluster" in placement:
        container_object = saltext.vmware.utils.vmware.get_cluster(
            datacenter_object, placement["cluster"]
        )
    else:
        container_objects = saltext.vmware.utils.vmware.get_hosts(
            service_instance, datacenter_name=datacenter, host_names=[placement["host"]]
        )
        if not container_objects:
            raise salt.exceptions.VMwareObjectRetrievalError(
                "ESXi host named '{}' wasn't " "found.".format(placement["host"])
            )
        container_object = container_objects[0]

    # list of vim.host.DatastoreBrowser.SearchResults objects
    files = saltext.vmware.utils.vmware.get_datastore_files(
        service_instance, directory, [datastore], container_object, browser_spec
    )
    if files and len(files[0].file) > 1:
        raise salt.exceptions.VMwareMultipleObjectsError(
            "Multiple configuration files found in " "the same virtual machine folder"
        )
    elif files and files[0].file:
        return files[0]
    else:
        return None


def get_vm_config(
    name,
    datacenter=None,
    objects=True,
    host=None,
    vcenter=None,
    username=None,
    password=None,
    protocol=None,
    port=None,
    verify_ssl=True,
):
    """
    Queries and converts the virtual machine properties to the available format
    from the schema. If the objects attribute is True the config objects will
    have extra properties, like 'object' which will include the
    vim.vm.device.VirtualDevice, this is necessary for deletion and update
    actions.

    name
        Name of the virtual machine

    datacenter
        Datacenter's name where the virtual machine is available

    objects
        Indicates whether to return the vmware object properties
        (eg. object, key) or just the properties which can be set

    host
        The location of the host.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    verify_ssl
        Verify the SSL certificate. Default: True
    """
    if salt.utils.platform.is_proxy():
        details = __salt__["vmware_info.get_proxy_connection_details"]()
    else:
        details = __salt__["vmware_info.get_connection_details"](
            host=host,
            vcenter=vcenter,
            username=username,
            password=password,
            protocol=protocol,
            port=port,
            verify_ssl=verify_ssl,
        )
    service_instance = saltext.vmware.utils.vmware.get_service_instance(**details)

    properties = [
        "config.hardware.device",
        "config.hardware.numCPU",
        "config.hardware.numCoresPerSocket",
        "config.nestedHVEnabled",
        "config.cpuHotAddEnabled",
        "config.cpuHotRemoveEnabled",
        "config.hardware.memoryMB",
        "config.memoryReservationLockedToMax",
        "config.memoryHotAddEnabled",
        "config.version",
        "config.guestId",
        "config.extraConfig",
        "name",
    ]
    virtual_machine = saltext.vmware.utils.vmware.get_vm_by_property(
        service_instance, name, vm_properties=properties, datacenter=datacenter
    )
    parent_ref = saltext.vmware.utils.vmware.get_datacenter(
        service_instance=service_instance, datacenter_name=datacenter
    )
    current_config = {"name": name}
    current_config["cpu"] = {
        "count": virtual_machine["config.hardware.numCPU"],
        "cores_per_socket": virtual_machine["config.hardware.numCoresPerSocket"],
        "nested": virtual_machine["config.nestedHVEnabled"],
        "hotadd": virtual_machine["config.cpuHotAddEnabled"],
        "hotremove": virtual_machine["config.cpuHotRemoveEnabled"],
    }

    current_config["memory"] = {
        "size": virtual_machine["config.hardware.memoryMB"],
        "unit": "MB",
        "reservation_max": virtual_machine["config.memoryReservationLockedToMax"],
        "hotadd": virtual_machine["config.memoryHotAddEnabled"],
    }
    current_config["image"] = virtual_machine["config.guestId"]
    current_config["version"] = virtual_machine["config.version"]
    current_config["advanced_configs"] = {}
    for extra_conf in virtual_machine["config.extraConfig"]:
        try:
            current_config["advanced_configs"][extra_conf.key] = int(extra_conf.value)
        except ValueError:
            current_config["advanced_configs"][extra_conf.key] = extra_conf.value

    current_config["disks"] = []
    current_config["scsi_devices"] = []
    current_config["interfaces"] = []
    current_config["serial_ports"] = []
    current_config["cd_drives"] = []
    current_config["sata_controllers"] = []

    for device in virtual_machine["config.hardware.device"]:
        if isinstance(device, vim.vm.device.VirtualSCSIController):
            controller = {}
            controller["adapter"] = device.deviceInfo.label
            controller["bus_number"] = device.busNumber
            bus_sharing = device.sharedBus
            if bus_sharing == "noSharing":
                controller["bus_sharing"] = "no_sharing"
            elif bus_sharing == "virtualSharing":
                controller["bus_sharing"] = "virtual_sharing"
            elif bus_sharing == "physicalSharing":
                controller["bus_sharing"] = "physical_sharing"
            if isinstance(device, vim.vm.device.ParaVirtualSCSIController):
                controller["type"] = "paravirtual"
            elif isinstance(device, vim.vm.device.VirtualBusLogicController):
                controller["type"] = "buslogic"
            elif isinstance(device, vim.vm.device.VirtualLsiLogicController):
                controller["type"] = "lsilogic"
            elif isinstance(device, vim.vm.device.VirtualLsiLogicSASController):
                controller["type"] = "lsilogic_sas"
            if objects:
                # int list, stores the keys of the disks which are attached
                # to this controller
                controller["device"] = device.device
                controller["key"] = device.key
                controller["object"] = device
            current_config["scsi_devices"].append(controller)
        if isinstance(device, vim.vm.device.VirtualDisk):
            disk = {}
            disk["adapter"] = device.deviceInfo.label
            disk["size"] = device.capacityInKB
            disk["unit"] = "KB"
            controller = _get_device_by_key(
                virtual_machine["config.hardware.device"], device.controllerKey
            )
            disk["controller"] = controller.deviceInfo.label
            disk["address"] = str(controller.busNumber) + ":" + str(device.unitNumber)
            disk["datastore"] = saltext.vmware.utils.vmware.get_managed_object_name(
                device.backing.datastore
            )
            disk["thin_provision"] = device.backing.thinProvisioned
            disk["eagerly_scrub"] = device.backing.eagerlyScrub
            if objects:
                disk["key"] = device.key
                disk["unit_number"] = device.unitNumber
                disk["bus_number"] = controller.busNumber
                disk["controller_key"] = device.controllerKey
                disk["object"] = device
            current_config["disks"].append(disk)
        if isinstance(device, vim.vm.device.VirtualEthernetCard):
            interface = {}
            interface["adapter"] = device.deviceInfo.label
            interface["adapter_type"] = saltext.vmware.utils.vmware.get_network_adapter_object_type(
                device
            )
            interface["connectable"] = {
                "allow_guest_control": device.connectable.allowGuestControl,
                "connected": device.connectable.connected,
                "start_connected": device.connectable.startConnected,
            }
            interface["mac"] = device.macAddress
            if isinstance(
                device.backing,
                vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo,
            ):
                interface["switch_type"] = "distributed"
                pg_key = device.backing.port.portgroupKey
                network_ref = saltext.vmware.utils.vmware.get_mor_by_property(
                    service_instance,
                    vim.DistributedVirtualPortgroup,
                    pg_key,
                    property_name="key",
                    container_ref=parent_ref,
                )
            elif isinstance(device.backing, vim.vm.device.VirtualEthernetCard.NetworkBackingInfo):
                interface["switch_type"] = "standard"
                network_ref = device.backing.network
            interface["name"] = saltext.vmware.utils.vmware.get_managed_object_name(network_ref)
            if objects:
                interface["key"] = device.key
                interface["object"] = device
            current_config["interfaces"].append(interface)
        if isinstance(device, vim.vm.device.VirtualCdrom):
            drive = {}
            drive["adapter"] = device.deviceInfo.label
            controller = _get_device_by_key(
                virtual_machine["config.hardware.device"], device.controllerKey
            )
            drive["controller"] = controller.deviceInfo.label
            if isinstance(device.backing, vim.vm.device.VirtualCdrom.RemotePassthroughBackingInfo):
                drive["device_type"] = "client_device"
                drive["client_device"] = {"mode": "passthrough"}
            if isinstance(device.backing, vim.vm.device.VirtualCdrom.RemoteAtapiBackingInfo):
                drive["device_type"] = "client_device"
                drive["client_device"] = {"mode": "atapi"}
            if isinstance(device.backing, vim.vm.device.VirtualCdrom.IsoBackingInfo):
                drive["device_type"] = "datastore_iso_file"
                drive["datastore_iso_file"] = {"path": device.backing.fileName}
            drive["connectable"] = {
                "allow_guest_control": device.connectable.allowGuestControl,
                "connected": device.connectable.connected,
                "start_connected": device.connectable.startConnected,
            }
            if objects:
                drive["key"] = device.key
                drive["controller_key"] = device.controllerKey
                drive["object"] = device
            current_config["cd_drives"].append(drive)
        if isinstance(device, vim.vm.device.VirtualSerialPort):
            port = {}
            port["adapter"] = device.deviceInfo.label
            if isinstance(device.backing, vim.vm.device.VirtualSerialPort.URIBackingInfo):
                port["type"] = "network"
                port["backing"] = {
                    "uri": device.backing.proxyURI,
                    "direction": device.backing.direction,
                    "filename": device.backing.serviceURI,
                }
            if isinstance(device.backing, vim.vm.device.VirtualSerialPort.PipeBackingInfo):
                port["type"] = "pipe"
            if isinstance(device.backing, vim.vm.device.VirtualSerialPort.FileBackingInfo):
                port["type"] = "file"
            if isinstance(device.backing, vim.vm.device.VirtualSerialPort.DeviceBackingInfo):
                port["type"] = "device"
            port["yield"] = device.yieldOnPoll
            port["connectable"] = {
                "allow_guest_control": device.connectable.allowGuestControl,
                "connected": device.connectable.connected,
                "start_connected": device.connectable.startConnected,
            }
            if objects:
                port["key"] = device.key
                port["object"] = device
            current_config["serial_ports"].append(port)
        if isinstance(device, vim.vm.device.VirtualSATAController):
            sata = {}
            sata["adapter"] = device.deviceInfo.label
            sata["bus_number"] = device.busNumber
            if objects:
                sata["device"] = device.device  # keys of the connected devices
                sata["key"] = device.key
                sata["object"] = device
            current_config["sata_controllers"].append(sata)

    return current_config


def _convert_units(devices):
    """
    Updates the size and unit dictionary values with the new unit values

    devices
        List of device data objects
    """
    if devices:
        for device in devices:
            if "unit" in device and "size" in device:
                device.update(saltext.vmware.utils.vmware.convert_to_kb(device["unit"], device["size"]))
    else:
        return False
    return True


def compare_vm_configs(new_config, current_config):
    """
    Compares virtual machine current and new configuration, the current is the
    one which is deployed now, and the new is the target config. Returns the
    differences between the objects in a dictionary, the keys are the
    configuration parameter keys and the values are differences objects: either
    list or recursive difference

    new_config:
        New config dictionary with every available parameter

    current_config
        Currently deployed configuration
    """
    diffs = {}
    keys = set(new_config.keys())

    # These values identify the virtual machine, comparison is unnecessary
    keys.discard("name")
    keys.discard("datacenter")
    keys.discard("datastore")
    for property_key in ("version", "image"):
        if property_key in keys:
            single_value_diff = recursive_diff(
                {property_key: current_config[property_key]},
                {property_key: new_config[property_key]},
            )
            if single_value_diff.diffs:
                diffs[property_key] = single_value_diff
            keys.discard(property_key)

    if "cpu" in keys:
        keys.remove("cpu")
        cpu_diff = recursive_diff(current_config["cpu"], new_config["cpu"])
        if cpu_diff.diffs:
            diffs["cpu"] = cpu_diff

    if "memory" in keys:
        keys.remove("memory")
        _convert_units([current_config["memory"]])
        _convert_units([new_config["memory"]])
        memory_diff = recursive_diff(current_config["memory"], new_config["memory"])
        if memory_diff.diffs:
            diffs["memory"] = memory_diff

    if "advanced_configs" in keys:
        keys.remove("advanced_configs")
        key = "advanced_configs"
        advanced_diff = recursive_diff(current_config[key], new_config[key])
        if advanced_diff.diffs:
            diffs[key] = advanced_diff

    if "disks" in keys:
        keys.remove("disks")
        _convert_units(current_config["disks"])
        _convert_units(new_config["disks"])
        disk_diffs = list_diff(current_config["disks"], new_config["disks"], "address")
        # REMOVE UNSUPPORTED DIFFERENCES/CHANGES
        # If the disk already exist, the backing properties like eagerly scrub
        # and thin provisioning
        # cannot be updated, and should not be identified as differences
        disk_diffs.remove_diff(diff_key="eagerly_scrub")
        # Filename updates are not supported yet, on VSAN datastores the
        # backing.fileName points to a uid + the vmdk name
        disk_diffs.remove_diff(diff_key="filename")
        # The adapter name shouldn't be changed
        disk_diffs.remove_diff(diff_key="adapter")
        if disk_diffs.diffs:
            diffs["disks"] = disk_diffs

    if "interfaces" in keys:
        keys.remove("interfaces")
        interface_diffs = list_diff(current_config["interfaces"], new_config["interfaces"], "mac")
        # The adapter name shouldn't be changed
        interface_diffs.remove_diff(diff_key="adapter")
        if interface_diffs.diffs:
            diffs["interfaces"] = interface_diffs

    # For general items where the identification can be done by adapter
    for key in keys:
        if key not in current_config or key not in new_config:
            raise ValueError(
                "A general device {} configuration was "
                "not supplied or it was not retrieved from "
                "remote configuration".format(key)
            )
        device_diffs = list_diff(current_config[key], new_config[key], "adapter")
        if device_diffs.diffs:
            diffs[key] = device_diffs

    return diffs


@depends(HAS_PYVMOMI)
def get_advanced_configs(vm_name, datacenter, service_instance=None):
    """
    Returns extra config parameters from a virtual machine advanced config list

    vm_name
        Virtual machine name

    datacenter
        Datacenter name where the virtual machine is available

    service_instance
        vCenter service instance for connection and configuration
    """
    current_config = get_vm_config(
        vm_name, datacenter=datacenter, objects=True, service_instance=service_instance
    )
    return current_config["advanced_configs"]


@depends(HAS_PYVMOMI)
def set_advanced_configs(vm_name, datacenter, advanced_configs, service_instance=None):
    """
    Appends extra config parameters to a virtual machine advanced config list

    vm_name
        Virtual machine name

    datacenter
        Datacenter name where the virtual machine is available

    advanced_configs
        Dictionary with advanced parameter key value pairs

    service_instance
        vCenter service instance for connection and configuration
    """
    current_config = get_vm_config(
        vm_name, datacenter=datacenter, objects=True, service_instance=service_instance
    )
    diffs = compare_vm_configs(
        {"name": vm_name, "advanced_configs": advanced_configs}, current_config
    )
    datacenter_ref = salt.utils.vmware.get_datacenter(service_instance, datacenter)
    vm_ref = salt.utils.vmware.get_mor_by_property(
        service_instance,
        vim.VirtualMachine,
        vm_name,
        property_name="name",
        container_ref=datacenter_ref,
    )
    config_spec = vim.vm.ConfigSpec()
    changes = diffs["advanced_configs"].diffs
    _apply_advanced_config(
        config_spec, diffs["advanced_configs"].new_values, vm_ref.config.extraConfig
    )
    if changes:
        salt.utils.vmware.update_vm(vm_ref, config_spec)
    return {"advanced_config_changes": changes}


def _delete_advanced_config(config_spec, advanced_config, vm_extra_config):
    """
    Removes configuration parameters for the vm

    config_spec
        vm.ConfigSpec object

    advanced_config
        List of advanced config keys to be deleted

    vm_extra_config
        Virtual machine vm_ref.config.extraConfig object
    """
    log.trace("Removing advanced configuration " "parameters {}".format(advanced_config))
    if isinstance(advanced_config, str):
        raise salt.exceptions.ArgumentValueError(
            "The specified 'advanced_configs' configuration "
            "option cannot be parsed, please check the parameters"
        )
    removed_configs = []
    for key in advanced_config:
        for option in vm_extra_config:
            if option.key == key:
                option = vim.option.OptionValue(key=key, value="")
                config_spec.extraConfig.append(option)
                removed_configs.append(key)
    return removed_configs


@depends(HAS_PYVMOMI)
def delete_advanced_configs(vm_name, datacenter, advanced_configs, service_instance=None):
    """
    Removes extra config parameters from a virtual machine

    vm_name
        Virtual machine name

    datacenter
        Datacenter name where the virtual machine is available

    advanced_configs
        List of advanced config values to be removed

    service_instance
        vCenter service instance for connection and configuration
    """
    datacenter_ref = salt.utils.vmware.get_datacenter(service_instance, datacenter)
    vm_ref = salt.utils.vmware.get_mor_by_property(
        service_instance,
        vim.VirtualMachine,
        vm_name,
        property_name="name",
        container_ref=datacenter_ref,
    )
    config_spec = vim.vm.ConfigSpec()
    removed_configs = _delete_advanced_config(
        config_spec, advanced_configs, vm_ref.config.extraConfig
    )
    if removed_configs:
        salt.utils.vmware.update_vm(vm_ref, config_spec)
    return {"removed_configs": removed_configs}
