# Copyright 2022 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import saltext.vmware.utils.esxi as utils_esxi
from saltext.vmware.utils.connect import get_service_instance

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim, vmodl

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False

__virtualname__ = "vmware_vswitch"
__proxyenabled__ = ["vmware_vswitch"]


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def _get(hostname, switch_name=None, service_instance=None):
    """
    Returns a list of vswitches found on a host; if switch_name is set, the
    list will contain just that vswitch.
    If no matching vswitches are found, the empty list is returned.

    hostname
        The host name to inspect.

    switch_name
        The vswitch name (optional).

    service_instance
        Use this vCenter service connection instance instead of creating a new one (optional).
    """
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)

    host = utils_esxi.get_host(hostname, service_instance)

    vswitches = host.configManager.networkSystem.networkInfo.vswitch

    if switch_name:
        for vswitch in vswitches:
            if vswitch.name == switch_name:
                return [vswitch]
        return []

    return vswitches


def get(hostname, switch_name=None, service_instance=None):
    """
    Get the properties of all vswitches on a host, optionally filtering to one name.
    Returns an empty list if no matching vswitch is found.

    hostname
        The host name to inspect.

    switch_name
        The vswitch name (optional).

    service_instance
        Use this vCenter service connection instance instead of creating a new one (optional).

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vswitch.get hostname=host1 switch_name=vSwitch1
    """
    ret = []
    for vswitch in _get(
        hostname=hostname, switch_name=switch_name, service_instance=service_instance
    ):
        spec = vswitch.spec
        info = {
            "num_ports": spec.numPorts,
            "mtu": spec.mtu or vswitch.mtu,
            "name": vswitch.name,
            # each nic looks something like "key-vim.host.PhysicalNic-vmnic0"
            "nics": [nic.split("-")[-1] for nic in vswitch.pnic],
            # TODO: unit test "key-vim.host.PortGroup-Management Network", only split twice in case '-' is in the name
            "portgroups": [pg.split("-", 2)[-1] for pg in vswitch.portgroup],
            # TODO: support bonded/bridged nics
            # TODO: support "policy", teaming, offload, security and shaping.
        }
        ret.append(info)

    return ret


def add(switch_name, hostname, mtu=1500, nics=[], num_ports=128, service_instance=None):
    """
    Adds a vswitch to the host.

    switch_name
        The name of the new vswitch.

    hostname
        The hostname where the switch will be added.

    mtu
        Maximum transmission unit size in bytes (optional).

    nics
        List of physical nics to attach to; if used might look like ["vmnic0"] (optional).

    num_ports
        Number of ports to allocate on the virtual switch.

    service_instance
        Use this vCenter service connection instance instead of creating a new one (optional).

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vswitch.add switch_name=vSwitch0 hostname=host1 mtu=1500, nics='["vmnic0", "vmnic1"]', num_ports=256
    """
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)

    host = utils_esxi.get_host(hostname, service_instance)

    spec = vim.host.VirtualSwitch.Specification()
    spec.numPorts = num_ports
    spec.mtu = mtu
    if nics:
        spec.bridge = vim.host.VirtualSwitch.BondBridge(nicDevice=nics)

    host.configManager.networkSystem.AddVirtualSwitch(vswitchName=switch_name, spec=spec)

    return {"added": switch_name}


def remove(switch_name, hostname, service_instance=None):
    """
    Removes a vswitch on the host.

    switch_name
        The name of the vswitch to be removed.

    hostname
        The hostname where the switch exists.

    service_instance
        Use this vCenter service connection instance instead of creating a new one (optional).

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_vswitch.remove switch_name=vSwitch0 host_name=host1
    """
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)

    host = utils_esxi.get_host(hostname, service_instance)
    host.configManager.networkSystem.RemoveVirtualSwitch(switch_name)
    return {"removed": switch_name}
