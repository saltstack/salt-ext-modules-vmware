# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import salt.exceptions
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.datacenter as utils_datacenter
import saltext.vmware.utils.esxi as utils_esxi
import saltext.vmware.utils.vmware as utils_vmware
from saltext.vmware.utils.connect import get_service_instance

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim, vmodl

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False

__virtualname__ = "vmware_dvswitch"
__proxyenabled__ = ["vmware_dvswitch"]


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def _get_switch_config_spec(service_instance, datacenter_name, switch_name):
    dc_ref = switch_ref = config_spec = None
    dc_ref = utils_datacenter.get_datacenter(service_instance, datacenter_name)
    switch_refs = utils_vmware.get_dvss(dc_ref=dc_ref, dvs_names=[switch_name])
    if switch_refs:
        switch_ref = switch_refs[0]
        dvs_props = utils_common.get_properties_of_managed_object(
            switch_ref, ["config", "capability"]
        )
        config_spec = vim.dvs.VmwareDistributedVirtualSwitch.ConfigSpec()
        # Copy all of the properties in the config of the of the DVS to a
        # DvsConfigSpec
        skipped_properties = ["host"]
        for prop in config_spec.__dict__.keys():
            if prop in skipped_properties:
                continue
            if hasattr(dvs_props["config"], prop):
                setattr(config_spec, prop, getattr(dvs_props["config"], prop))
    return dc_ref, switch_ref, config_spec


def configure(
    datacenter_name,
    switch_name,
    uplink_count=None,
    uplink_prefix="Uplink ",
    switch_version=None,
    switch_description=None,
    mtu=None,
    discovery_protocol=None,
    discovery_operation=None,
    multicast_filtering_mode=None,
    contact_name=None,
    contact_description=None,
    network_forged_transmits=None,
    network_mac_changes=None,
    network_promiscuous=None,
    health_check_teaming_failover=None,
    health_teaming_failover_interval=None,
    health_vlan_mtu=None,
    health_vlan_mtu_interval=None,
    service_instance=None,
):
    """
    Creates a new distributed vSwitch or updates an existing vSwitch.

    switch_name
        Name of the distributed vSwitch to create or update.

    uplink_count
        Count of uplink per ESXi per host. Optional.

    uplink_prefix
        The prefix to be used for uplinks. Optional. Default: "Uplink ".

    switch_version
        The version of the distributed vSwitch to create or update. Optional.

    switch_description
        Description of the distributed vSwitch. Optional. Default: None.

    mtu
        Maximum transmission unit for the switch. Optional.

    discovery_protocol
        Link discovery protocol between Cisco and Link Layer discovery. Optional. Valid values: "cdp", "lldp", "disabled".

    discovery_operation
        Discovery operation for the switch. Optional. Valid values: "both", "advertise", "listen".

    multicast_filtering_mode
        Multicast filtering mode for the switch. Optional. Valid values: "basic", "snooping".

    contact_name
        Administrator contact name. Optional. Default: "".

    contact_description
        Administrator contact information. Optional. Default: "".

    network_forged_transmits
        Allow forged transmits. Type: Boolean. Optional. Valid values: "True", "False".

    network_mac_changes
        Allow mac changes. Type: Boolean. Optional. Valid values: "True", "False".

    network_promiscuous
        Allow promiscuous mode. Type: Boolean. Optional. Valid values: "True", "False".

    health_check_teaming_failover
        Enable teaming and failover health check. Type: Boolean. Optional. Valid values: "True", "False".

    health_teaming_failover_interval
        Teaming and failover health check interval in minutes. Optional.

    health_vlan_mtu
        Enable VLAN and MTU health check. Type: Boolean. Optional. Valid values: "True", "False".

    health_vlan_mtu_interval
        VLAN and MTU health check interval in minutes. Optional.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. Optional.

    .. code-block:: bash

        salt '*' vmware_dvswitch.configure dvs1
    """
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    try:
        health_spec = product_spec = spec = None
        dc_ref, switch_ref, config_spec = _get_switch_config_spec(
            service_instance=service_instance,
            datacenter_name=datacenter_name,
            switch_name=switch_name,
        )
        if not switch_ref:
            spec = vim.DistributedVirtualSwitch.CreateSpec()
            spec.configSpec = vim.dvs.VmwareDistributedVirtualSwitch.ConfigSpec()
            config_spec = spec.configSpec
            config_spec.name = switch_name

        if mtu:
            config_spec.maxMtu = mtu

        if uplink_count:
            config_spec.uplinkPortPolicy = vim.DistributedVirtualSwitch.NameArrayUplinkPortPolicy()
            for i in range(uplink_count):
                config_spec.uplinkPortPolicy.uplinkPortName.append(
                    "{}{}".format(uplink_prefix, i + 1)
                )

        if switch_version:
            product_spec = vim.dvs.ProductSpec()
            product_spec.version = switch_version
            if spec:
                spec.productInfo = product_spec

        if switch_description:
            config_spec.description = switch_description

        if contact_name or contact_description:
            contact_info_spec = vim.DistributedVirtualSwitch.ContactInfo()
            contact_info_spec.contact = contact_description
            contact_info_spec.name = contact_name
            if switch_ref:
                contact_info_spec.contact = contact_description or switch_ref.config.contact.contact
                contact_info_spec.name = contact_name or switch_ref.config.contact.name
            config_spec.contact = contact_info_spec

        if discovery_operation or discovery_protocol:
            ldp_config_spec = vim.host.LinkDiscoveryProtocolConfig()
            ldp_config_spec.operation = discovery_operation
            ldp_config_spec.protocol = discovery_protocol
            if switch_ref:
                ldp_config_spec.protocol = (
                    discovery_protocol or switch_ref.config.linkDiscoveryProtocolConfig.protocol
                )
                ldp_config_spec.operation = (
                    discovery_operation or switch_ref.config.linkDiscoveryProtocolConfig.operation
                )
            if discovery_protocol == "disabled":
                ldp_config_spec.protocol = "cdp"
                ldp_config_spec.operation = "none"
            config_spec.linkDiscoveryProtocolConfig = ldp_config_spec

        if multicast_filtering_mode:
            if multicast_filtering_mode == "basic":
                config_spec.multicastFilteringMode = "legacyFiltering"
            else:
                config_spec.multicastFilteringMode = multicast_filtering_mode

        if not switch_ref:
            utils_vmware.create_dvs(dc_ref=dc_ref, dvs_name=switch_name, dvs_create_spec=spec)

        if (
            network_promiscuous is not None
            or network_mac_changes is not None
            or network_forged_transmits is not None
        ):
            policy = vim.dvs.VmwareDistributedVirtualSwitch.SecurityPolicy()
            if not switch_ref:
                dc_ref, switch_ref, config_spec = _get_switch_config_spec(
                    service_instance=service_instance,
                    datacenter_name=datacenter_name,
                    switch_name=switch_name,
                )
            if network_promiscuous is None:
                network_promiscuous = (
                    switch_ref.config.defaultPortConfig.securityPolicy.allowPromiscuous.value
                )
            if network_mac_changes is None:
                network_mac_changes = (
                    switch_ref.config.defaultPortConfig.securityPolicy.macChanges.value
                )
            if network_forged_transmits is None:
                network_forged_transmits = (
                    switch_ref.config.defaultPortConfig.securityPolicy.forgedTransmits.value
                )
            if network_promiscuous is not None:
                policy.allowPromiscuous = vim.BoolPolicy(value=network_promiscuous)
            if network_mac_changes is not None:
                policy.macChanges = vim.BoolPolicy(value=network_mac_changes)
            if network_forged_transmits is not None:
                policy.forgedTransmits = vim.BoolPolicy(value=network_forged_transmits)
            config_spec.defaultPortConfig.securityPolicy = policy

        if (
            health_check_teaming_failover is not None
            or health_teaming_failover_interval is not None
            or health_vlan_mtu is not None
            or health_vlan_mtu_interval is not None
        ):
            if not switch_ref:
                dc_ref, switch_ref, config_spec = _get_switch_config_spec(
                    service_instance=service_instance,
                    datacenter_name=datacenter_name,
                    switch_name=switch_name,
                )
            health_spec = vim.DistributedVirtualSwitch.HealthCheckConfig.Array()
            for config in switch_ref.config.healthCheckConfig:
                if isinstance(
                    config, vim.dvs.VmwareDistributedVirtualSwitch.VlanMtuHealthCheckConfig
                ):
                    if health_vlan_mtu is not None:
                        config.enable = health_vlan_mtu
                    if health_vlan_mtu_interval is not None:
                        config.interval = health_vlan_mtu_interval
                    health_spec.append(config)
                if isinstance(
                    config, vim.dvs.VmwareDistributedVirtualSwitch.TeamingHealthCheckConfig
                ):
                    if health_check_teaming_failover is not None:
                        config.enable = health_check_teaming_failover
                    if health_teaming_failover_interval is not None:
                        config.interval = health_teaming_failover_interval
                    health_spec.append(config)

        if switch_ref:
            utils_vmware.update_dvs(dvs_ref=switch_ref, dvs_config_spec=config_spec)
            if product_spec:
                utils_vmware.update_dvs_version(dvs_ref=switch_ref, dvs_product_spec=product_spec)
            if health_spec:
                utils_vmware.update_dvs_health(dvs_ref=switch_ref, dvs_health_spec=health_spec)

        return True
    except (
        vim.fault.DvsFault,
        vmodl.fault.NotSupported,
        salt.exceptions.VMwareApiError,
        vmodl.RuntimeFault,
        vmodl.MethodFault,
    ) as exc:
        raise salt.exceptions.SaltException(str(exc))


def remove_hosts(
    switch_name,
    host_name=None,
    datacenter_name=None,
    cluster_name=None,
    service_instance=None,
):
    """
    Remove ESXi host(s) from a distributed vSwitch.

    switch_name
        Name of the distributed vSwitch.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_dvswitch.remove_hosts switch_name=dvs1 hostname=host1

    """
    log.debug("Running vmware_dvswitch.remove_hosts")
    ret = {}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )
    try:
        for h in hosts:
            ret[h.name] = False
            if hasattr(h.configManager.networkSystem.networkInfo, "vswitch"):
                h.configManager.networkSystem.RemoveVirtualSwitch(vswitchName=switch_name)
                ret[h.name] = True
        return ret
    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vim.fault.ResourceInUse,
        vmodl.fault.InvalidArgument,
        salt.exceptions.VMwareApiError,
    ) as exc:
        raise salt.exceptions.SaltException(str(exc))


def add_hosts(
    switch_name,
    host_name=None,
    datacenter_name=None,
    cluster_name=None,
    nics=None,
    service_instance=None,
):
    """
    Add ESXi host(s) to a distributed vSwitch.

    switch_name
        Name of the distributed vSwitch.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    nics
        List of vmnics to attach to vSwitch. (optional). Default "None".

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_dvswitch.add_hosts switch_name=dvs1 host_name=host1 num_ports=256 mtu=1800

    """
    log.debug("Running vmware_dvswitch.add_hosts")
    ret = {}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    _, switch_ref, _ = _get_switch_config_spec(
        service_instance=service_instance,
        datacenter_name=datacenter_name,
        switch_name=switch_name,
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )
    try:
        for h in hosts:
            ret[h.name] = False
            network_manager = h.configManager.networkSystem
            if not network_manager:
                continue
            if isinstance(nics, str):
                nics = [nics]
            vss_spec = vim.host.VirtualSwitch.Specification()
            vss_spec.mtu = switch_ref.config.maxMtu or 1500
            vss_spec.numPorts = switch_ref.config.numPorts or 128
            if nics:
                vss_spec.bridge = vim.host.VirtualSwitch.BondBridge(nicDevice=nics)
            network_manager.AddVirtualSwitch(vswitchName=switch_name, spec=vss_spec)
            ret[h.name] = True
        return ret
    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vim.fault.ResourceInUse,
        vmodl.fault.InvalidArgument,
        salt.exceptions.VMwareApiError,
    ) as exc:
        raise salt.exceptions.SaltException(str(exc))


def update_hosts(
    switch_name,
    host_name=None,
    datacenter_name=None,
    cluster_name=None,
    nics=None,
    num_ports=None,
    mtu=None,
    service_instance=None,
):
    """
    Update ESXi host(s) on a distributed vSwitch.

    switch_name
        Name of the distributed vSwitch.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    nics
        List of vmnics to attach to vSwitch. (optional). Default "None".

    num_ports
        Number of ports to configure on the vSwitch. (optional). Default 128.

    mtu
        MTU to configure on the vSwitch. (optional). Default 1600.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_dvswitch.update_hosts switch_name=dvs1 host_name=host1 num_ports=256 mtu=1800

    """
    log.debug("Running vmware_dvswitch.update_hosts")
    ret = {}
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    _, switch_ref, _ = _get_switch_config_spec(
        service_instance=service_instance,
        datacenter_name=datacenter_name,
        switch_name=switch_name,
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )
    try:
        for h in hosts:
            ret[h.name] = False
            network_manager = h.configManager.networkSystem
            if not network_manager:
                continue
            if isinstance(nics, str):
                nics = [nics]
            vss_spec = vim.host.VirtualSwitch.Specification()
            if hasattr(network_manager.networkInfo, "vswitch"):
                for switch in network_manager.networkInfo.vswitch:
                    if switch.name != switch_name:
                        continue
                    vss_spec.mtu = mtu or switch.mtu or switch_ref.config.maxMtu
                    vss_spec.numPorts = (
                        num_ports or switch.spec.numPorts or switch_ref.config.numPorts
                    )
                    if switch.pnic or nics:
                        vss_spec.bridge = vim.host.VirtualSwitch.BondBridge(
                            nicDevice=nics or list(map(lambda x: x.split("-", 3)[-1], switch.pnic))
                        )
                    network_manager.UpdateVirtualSwitch(vswitchName=switch_name, spec=vss_spec)
                    ret[h.name] = True
        return ret
    except (
        vim.fault.InvalidState,
        vim.fault.NotFound,
        vim.fault.HostConfigFault,
        vim.fault.ResourceInUse,
        vmodl.fault.InvalidArgument,
        salt.exceptions.VMwareApiError,
    ) as exc:
        raise salt.exceptions.SaltException(str(exc))
