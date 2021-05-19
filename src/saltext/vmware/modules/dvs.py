# SPDX-License-Identifier: Apache-2.0
def list_dvs(host, username, password, protocol=None, port=None, verify_ssl=True):
    """
    Returns a list of distributed virtual switches for the specified host.

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

    CLI Example:

    .. code-block:: bash

        salt '*' vsphere.list_dvs 1.2.3.4 root bad-password
    """
    service_instance = salt.utils.vmware.get_service_instance(
        host=host,
        username=username,
        password=password,
        protocol=protocol,
        port=port,
        verify_ssl=verify_ssl,
    )
    return salt.utils.vmware.list_dvs(service_instance)


def _get_dvs_config_dict(dvs_name, dvs_config):
    """
    Returns the dict representation of the DVS config

    dvs_name
        The name of the DVS

    dvs_config
        The DVS config
    """
    log.trace("Building the dict of the DVS '{}' config".format(dvs_name))
    conf_dict = {
        "name": dvs_name,
        "contact_email": dvs_config.contact.contact,
        "contact_name": dvs_config.contact.name,
        "description": dvs_config.description,
        "lacp_api_version": dvs_config.lacpApiVersion,
        "network_resource_control_version": dvs_config.networkResourceControlVersion,
        "network_resource_management_enabled": dvs_config.networkResourceManagementEnabled,
        "max_mtu": dvs_config.maxMtu,
    }
    if isinstance(dvs_config.uplinkPortPolicy, vim.DVSNameArrayUplinkPortPolicy):
        conf_dict.update({"uplink_names": dvs_config.uplinkPortPolicy.uplinkPortName})
    return conf_dict


def _get_dvs_link_discovery_protocol(dvs_name, dvs_link_disc_protocol):
    """
    Returns the dict representation of the DVS link discovery protocol

    dvs_name
        The name of the DVS

    dvs_link_disc_protocl
        The DVS link discovery protocol
    """
    log.trace("Building the dict of the DVS '{}' link discovery " "protocol".format(dvs_name))
    return {
        "operation": dvs_link_disc_protocol.operation,
        "protocol": dvs_link_disc_protocol.protocol,
    }


def _get_dvs_product_info(dvs_name, dvs_product_info):
    """
    Returns the dict representation of the DVS product_info

    dvs_name
        The name of the DVS

    dvs_product_info
        The DVS product info
    """
    log.trace("Building the dict of the DVS '{}' product " "info".format(dvs_name))
    return {
        "name": dvs_product_info.name,
        "vendor": dvs_product_info.vendor,
        "version": dvs_product_info.version,
    }


def _get_dvs_capability(dvs_name, dvs_capability):
    """
    Returns the dict representation of the DVS product_info

    dvs_name
        The name of the DVS

    dvs_capability
        The DVS capability
    """
    log.trace("Building the dict of the DVS '{}' capability" "".format(dvs_name))
    return {
        "operation_supported": dvs_capability.dvsOperationSupported,
        "portgroup_operation_supported": dvs_capability.dvPortGroupOperationSupported,
        "port_operation_supported": dvs_capability.dvPortOperationSupported,
    }


def _get_dvs_infrastructure_traffic_resources(dvs_name, dvs_infra_traffic_ress):
    """
    Returns a list of dict representations of the DVS infrastructure traffic
    resource

    dvs_name
        The name of the DVS

    dvs_infra_traffic_ress
        The DVS infrastructure traffic resources
    """
    log.trace(
        "Building the dicts of the DVS '{}' infrastructure traffic " "resources".format(dvs_name)
    )
    res_dicts = []
    for res in dvs_infra_traffic_ress:
        res_dict = {
            "key": res.key,
            "limit": res.allocationInfo.limit,
            "reservation": res.allocationInfo.reservation,
        }
        if res.allocationInfo.shares:
            res_dict.update(
                {
                    "num_shares": res.allocationInfo.shares.shares,
                    "share_level": res.allocationInfo.shares.level,
                }
            )
        res_dicts.append(res_dict)
    return res_dicts


def list_dvss(datacenter=None, dvs_names=None, service_instance=None):
    """
    Returns a list of distributed virtual switches (DVSs).
    The list can be filtered by the datacenter or DVS names.

    datacenter
        The datacenter to look for DVSs in.
        Default value is None.

    dvs_names
        List of DVS names to look for. If None, all DVSs are returned.
        Default value is None.

    .. code-block:: bash

        salt '*' vsphere.list_dvss

        salt '*' vsphere.list_dvss dvs_names=[dvs1,dvs2]
    """
    ret_list = []
    proxy_type = get_proxy_type()
    if proxy_type == "esxdatacenter":
        datacenter = __salt__["esxdatacenter.get_details"]()["datacenter"]
        dc_ref = _get_proxy_target(service_instance)
    elif proxy_type == "esxcluster":
        datacenter = __salt__["esxcluster.get_details"]()["datacenter"]
        dc_ref = salt.utils.vmware.get_datacenter(service_instance, datacenter)

    for dvs in salt.utils.vmware.get_dvss(dc_ref, dvs_names, (not dvs_names)):
        dvs_dict = {}
        # XXX: Because of how VMware did DVS object inheritance we can\'t
        # be more restrictive when retrieving the dvs config, we have to
        # retrieve the entire object
        props = salt.utils.vmware.get_properties_of_managed_object(
            dvs, ["name", "config", "capability", "networkResourcePool"]
        )
        dvs_dict = _get_dvs_config_dict(props["name"], props["config"])
        # Product info
        dvs_dict.update(
            {"product_info": _get_dvs_product_info(props["name"], props["config"].productInfo)}
        )
        # Link Discovery Protocol
        if props["config"].linkDiscoveryProtocolConfig:
            dvs_dict.update(
                {
                    "link_discovery_protocol": _get_dvs_link_discovery_protocol(
                        props["name"], props["config"].linkDiscoveryProtocolConfig
                    )
                }
            )
        # Capability
        dvs_dict.update({"capability": _get_dvs_capability(props["name"], props["capability"])})
        # InfrastructureTrafficResourceConfig - available with vSphere 6.0
        if hasattr(props["config"], "infrastructureTrafficResourceConfig"):
            dvs_dict.update(
                {
                    "infrastructure_traffic_resource_pools": _get_dvs_infrastructure_traffic_resources(
                        props["name"],
                        props["config"].infrastructureTrafficResourceConfig,
                    )
                }
            )
        ret_list.append(dvs_dict)
    return ret_list


def _apply_dvs_config(config_spec, config_dict):
    """
    Applies the values of the config dict dictionary to a config spec
    (vim.VMwareDVSConfigSpec)
    """
    if config_dict.get("name"):
        config_spec.name = config_dict["name"]
    if config_dict.get("contact_email") or config_dict.get("contact_name"):
        if not config_spec.contact:
            config_spec.contact = vim.DVSContactInfo()
        config_spec.contact.contact = config_dict.get("contact_email")
        config_spec.contact.name = config_dict.get("contact_name")
    if config_dict.get("description"):
        config_spec.description = config_dict.get("description")
    if config_dict.get("max_mtu"):
        config_spec.maxMtu = config_dict.get("max_mtu")
    if config_dict.get("lacp_api_version"):
        config_spec.lacpApiVersion = config_dict.get("lacp_api_version")
    if config_dict.get("network_resource_control_version"):
        config_spec.networkResourceControlVersion = config_dict.get(
            "network_resource_control_version"
        )
    if config_dict.get("uplink_names"):
        if not config_spec.uplinkPortPolicy or not isinstance(
            config_spec.uplinkPortPolicy, vim.DVSNameArrayUplinkPortPolicy
        ):

            config_spec.uplinkPortPolicy = vim.DVSNameArrayUplinkPortPolicy()
        config_spec.uplinkPortPolicy.uplinkPortName = config_dict["uplink_names"]


def _apply_dvs_link_discovery_protocol(disc_prot_config, disc_prot_dict):
    """
    Applies the values of the disc_prot_dict dictionary to a link discovery
    protocol config object (vim.LinkDiscoveryProtocolConfig)
    """
    disc_prot_config.operation = disc_prot_dict["operation"]
    disc_prot_config.protocol = disc_prot_dict["protocol"]


def _apply_dvs_product_info(product_info_spec, product_info_dict):
    """
    Applies the values of the product_info_dict dictionary to a product info
    spec (vim.DistributedVirtualSwitchProductSpec)
    """
    if product_info_dict.get("name"):
        product_info_spec.name = product_info_dict["name"]
    if product_info_dict.get("vendor"):
        product_info_spec.vendor = product_info_dict["vendor"]
    if product_info_dict.get("version"):
        product_info_spec.version = product_info_dict["version"]


def _apply_dvs_capability(capability_spec, capability_dict):
    """
    Applies the values of the capability_dict dictionary to a DVS capability
    object (vim.vim.DVSCapability)
    """
    if "operation_supported" in capability_dict:
        capability_spec.dvsOperationSupported = capability_dict["operation_supported"]
    if "port_operation_supported" in capability_dict:
        capability_spec.dvPortOperationSupported = capability_dict["port_operation_supported"]
    if "portgroup_operation_supported" in capability_dict:
        capability_spec.dvPortGroupOperationSupported = capability_dict[
            "portgroup_operation_supported"
        ]


def _apply_dvs_infrastructure_traffic_resources(infra_traffic_resources, resource_dicts):
    """
    Applies the values of the resource dictionaries to infra traffic resources,
    creating the infra traffic resource if required
    (vim.DistributedVirtualSwitchProductSpec)
    """
    for res_dict in resource_dicts:
        filtered_traffic_resources = [
            r for r in infra_traffic_resources if r.key == res_dict["key"]
        ]
        if filtered_traffic_resources:
            traffic_res = filtered_traffic_resources[0]
        else:
            traffic_res = vim.DvsHostInfrastructureTrafficResource()
            traffic_res.key = res_dict["key"]
            traffic_res.allocationInfo = vim.DvsHostInfrastructureTrafficResourceAllocation()
            infra_traffic_resources.append(traffic_res)
        if res_dict.get("limit"):
            traffic_res.allocationInfo.limit = res_dict["limit"]
        if res_dict.get("reservation"):
            traffic_res.allocationInfo.reservation = res_dict["reservation"]
        if res_dict.get("num_shares") or res_dict.get("share_level"):
            if not traffic_res.allocationInfo.shares:
                traffic_res.allocationInfo.shares = vim.SharesInfo()
        if res_dict.get("share_level"):
            traffic_res.allocationInfo.shares.level = vim.SharesLevel(res_dict["share_level"])
        if res_dict.get("num_shares"):
            # XXX Even though we always set the number of shares if provided,
            # the vCenter will ignore it unless the share level is 'custom'.
            traffic_res.allocationInfo.shares.shares = res_dict["num_shares"]


def _apply_dvs_network_resource_pools(network_resource_pools, resource_dicts):
    """
    Applies the values of the resource dictionaries to network resource pools,
    creating the resource pools if required
    (vim.DVSNetworkResourcePoolConfigSpec)
    """
    for res_dict in resource_dicts:
        ress = [r for r in network_resource_pools if r.key == res_dict["key"]]
        if ress:
            res = ress[0]
        else:
            res = vim.DVSNetworkResourcePoolConfigSpec()
            res.key = res_dict["key"]
            res.allocationInfo = vim.DVSNetworkResourcePoolAllocationInfo()
            network_resource_pools.append(res)
        if res_dict.get("limit"):
            res.allocationInfo.limit = res_dict["limit"]
        if res_dict.get("num_shares") and res_dict.get("share_level"):
            if not res.allocationInfo.shares:
                res.allocationInfo.shares = vim.SharesInfo()
            res.allocationInfo.shares.shares = res_dict["num_shares"]
            res.allocationInfo.shares.level = vim.SharesLevel(res_dict["share_level"])


def create_dvs(dvs_dict, dvs_name, service_instance=None):
    """
    Creates a distributed virtual switch (DVS).

    Note: The ``dvs_name`` param will override any name set in ``dvs_dict``.

    dvs_dict
        Dict representation of the new DVS (example in salt.states.dvs)

    dvs_name
        Name of the DVS to be created.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.create_dvs dvs dict=$dvs_dict dvs_name=dvs_name
    """
    log.trace("Creating dvs '{}' with dict = {}".format(dvs_name, dvs_dict))
    proxy_type = get_proxy_type()
    if proxy_type == "esxdatacenter":
        datacenter = __salt__["esxdatacenter.get_details"]()["datacenter"]
        dc_ref = _get_proxy_target(service_instance)
    elif proxy_type == "esxcluster":
        datacenter = __salt__["esxcluster.get_details"]()["datacenter"]
        dc_ref = salt.utils.vmware.get_datacenter(service_instance, datacenter)
    # Make the name of the DVS consistent with the call
    dvs_dict["name"] = dvs_name
    # Build the config spec from the input
    dvs_create_spec = vim.DVSCreateSpec()
    dvs_create_spec.configSpec = vim.VMwareDVSConfigSpec()
    _apply_dvs_config(dvs_create_spec.configSpec, dvs_dict)
    if dvs_dict.get("product_info"):
        dvs_create_spec.productInfo = vim.DistributedVirtualSwitchProductSpec()
        _apply_dvs_product_info(dvs_create_spec.productInfo, dvs_dict["product_info"])
    if dvs_dict.get("capability"):
        dvs_create_spec.capability = vim.DVSCapability()
        _apply_dvs_capability(dvs_create_spec.capability, dvs_dict["capability"])
    if dvs_dict.get("link_discovery_protocol"):
        dvs_create_spec.configSpec.linkDiscoveryProtocolConfig = vim.LinkDiscoveryProtocolConfig()
        _apply_dvs_link_discovery_protocol(
            dvs_create_spec.configSpec.linkDiscoveryProtocolConfig,
            dvs_dict["link_discovery_protocol"],
        )
    if dvs_dict.get("infrastructure_traffic_resource_pools"):
        dvs_create_spec.configSpec.infrastructureTrafficResourceConfig = []
        _apply_dvs_infrastructure_traffic_resources(
            dvs_create_spec.configSpec.infrastructureTrafficResourceConfig,
            dvs_dict["infrastructure_traffic_resource_pools"],
        )
    log.trace("dvs_create_spec = {}".format(dvs_create_spec))
    salt.utils.vmware.create_dvs(dc_ref, dvs_name, dvs_create_spec)
    if "network_resource_management_enabled" in dvs_dict:
        dvs_refs = salt.utils.vmware.get_dvss(dc_ref, dvs_names=[dvs_name])
        if not dvs_refs:
            raise VMwareObjectRetrievalError(
                "DVS '{}' wasn't found in datacenter '{}'" "".format(dvs_name, datacenter)
            )
        dvs_ref = dvs_refs[0]
        salt.utils.vmware.set_dvs_network_resource_management_enabled(
            dvs_ref, dvs_dict["network_resource_management_enabled"]
        )
    return True


def update_dvs(dvs_dict, dvs, service_instance=None):
    """
    Updates a distributed virtual switch (DVS).

    Note: Updating the product info, capability, uplinks of a DVS is not
          supported so the corresponding entries in ``dvs_dict`` will be
          ignored.

    dvs_dict
        Dictionary with the values the DVS should be update with
        (example in salt.states.dvs)

    dvs
        Name of the DVS to be updated.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.update_dvs dvs_dict=$dvs_dict dvs=dvs1
    """
    # Remove ignored properties
    log.trace("Updating dvs '{}' with dict = {}".format(dvs, dvs_dict))
    for prop in ["product_info", "capability", "uplink_names", "name"]:
        if prop in dvs_dict:
            del dvs_dict[prop]
    proxy_type = get_proxy_type()
    if proxy_type == "esxdatacenter":
        datacenter = __salt__["esxdatacenter.get_details"]()["datacenter"]
        dc_ref = _get_proxy_target(service_instance)
    elif proxy_type == "esxcluster":
        datacenter = __salt__["esxcluster.get_details"]()["datacenter"]
        dc_ref = salt.utils.vmware.get_datacenter(service_instance, datacenter)
    dvs_refs = salt.utils.vmware.get_dvss(dc_ref, dvs_names=[dvs])
    if not dvs_refs:
        raise VMwareObjectRetrievalError(
            "DVS '{}' wasn't found in " "datacenter '{}'" "".format(dvs, datacenter)
        )
    dvs_ref = dvs_refs[0]
    # Build the config spec from the input
    dvs_props = salt.utils.vmware.get_properties_of_managed_object(
        dvs_ref, ["config", "capability"]
    )
    dvs_config = vim.VMwareDVSConfigSpec()
    # Copy all of the properties in the config of the of the DVS to a
    # DvsConfigSpec
    skipped_properties = ["host"]
    for prop in dvs_config.__dict__.keys():
        if prop in skipped_properties:
            continue
        if hasattr(dvs_props["config"], prop):
            setattr(dvs_config, prop, getattr(dvs_props["config"], prop))
    _apply_dvs_config(dvs_config, dvs_dict)
    if dvs_dict.get("link_discovery_protocol"):
        if not dvs_config.linkDiscoveryProtocolConfig:
            dvs_config.linkDiscoveryProtocolConfig = vim.LinkDiscoveryProtocolConfig()
        _apply_dvs_link_discovery_protocol(
            dvs_config.linkDiscoveryProtocolConfig, dvs_dict["link_discovery_protocol"]
        )
    if dvs_dict.get("infrastructure_traffic_resource_pools"):
        if not dvs_config.infrastructureTrafficResourceConfig:
            dvs_config.infrastructureTrafficResourceConfig = []
        _apply_dvs_infrastructure_traffic_resources(
            dvs_config.infrastructureTrafficResourceConfig,
            dvs_dict["infrastructure_traffic_resource_pools"],
        )
    log.trace("dvs_config= {}".format(dvs_config))
    salt.utils.vmware.update_dvs(dvs_ref, dvs_config_spec=dvs_config)
    if "network_resource_management_enabled" in dvs_dict:
        salt.utils.vmware.set_dvs_network_resource_management_enabled(
            dvs_ref, dvs_dict["network_resource_management_enabled"]
        )
    return True


def _get_dvportgroup_out_shaping(pg_name, pg_default_port_config):
    """
    Returns the out shaping policy of a distributed virtual portgroup

    pg_name
        The name of the portgroup

    pg_default_port_config
        The dafault port config of the portgroup
    """
    log.trace("Retrieving portgroup's '{}' out shaping " "config".format(pg_name))
    out_shaping_policy = pg_default_port_config.outShapingPolicy
    if not out_shaping_policy:
        return {}
    return {
        "average_bandwidth": out_shaping_policy.averageBandwidth.value,
        "burst_size": out_shaping_policy.burstSize.value,
        "enabled": out_shaping_policy.enabled.value,
        "peak_bandwidth": out_shaping_policy.peakBandwidth.value,
    }


def _get_dvportgroup_security_policy(pg_name, pg_default_port_config):
    """
    Returns the security policy of a distributed virtual portgroup

    pg_name
        The name of the portgroup

    pg_default_port_config
        The dafault port config of the portgroup
    """
    log.trace("Retrieving portgroup's '{}' security policy " "config".format(pg_name))
    sec_policy = pg_default_port_config.securityPolicy
    if not sec_policy:
        return {}
    return {
        "allow_promiscuous": sec_policy.allowPromiscuous.value,
        "forged_transmits": sec_policy.forgedTransmits.value,
        "mac_changes": sec_policy.macChanges.value,
    }


def _get_dvportgroup_teaming(pg_name, pg_default_port_config):
    """
    Returns the teaming of a distributed virtual portgroup

    pg_name
        The name of the portgroup

    pg_default_port_config
        The dafault port config of the portgroup
    """
    log.trace("Retrieving portgroup's '{}' teaming" "config".format(pg_name))
    teaming_policy = pg_default_port_config.uplinkTeamingPolicy
    if not teaming_policy:
        return {}
    ret_dict = {
        "notify_switches": teaming_policy.notifySwitches.value,
        "policy": teaming_policy.policy.value,
        "reverse_policy": teaming_policy.reversePolicy.value,
        "rolling_order": teaming_policy.rollingOrder.value,
    }
    if teaming_policy.failureCriteria:
        failure_criteria = teaming_policy.failureCriteria
        ret_dict.update(
            {
                "failure_criteria": {
                    "check_beacon": failure_criteria.checkBeacon.value,
                    "check_duplex": failure_criteria.checkDuplex.value,
                    "check_error_percent": failure_criteria.checkErrorPercent.value,
                    "check_speed": failure_criteria.checkSpeed.value,
                    "full_duplex": failure_criteria.fullDuplex.value,
                    "percentage": failure_criteria.percentage.value,
                    "speed": failure_criteria.speed.value,
                }
            }
        )
    if teaming_policy.uplinkPortOrder:
        uplink_order = teaming_policy.uplinkPortOrder
        ret_dict.update(
            {
                "port_order": {
                    "active": uplink_order.activeUplinkPort,
                    "standby": uplink_order.standbyUplinkPort,
                }
            }
        )
    return ret_dict


def _get_dvportgroup_dict(pg_ref):
    """
    Returns a dictionary with a distributed virtual portgroup data


    pg_ref
        Portgroup reference
    """
    props = salt.utils.vmware.get_properties_of_managed_object(
        pg_ref,
        [
            "name",
            "config.description",
            "config.numPorts",
            "config.type",
            "config.defaultPortConfig",
        ],
    )
    pg_dict = {
        "name": props["name"],
        "description": props.get("config.description"),
        "num_ports": props["config.numPorts"],
        "type": props["config.type"],
    }
    if props["config.defaultPortConfig"]:
        dpg = props["config.defaultPortConfig"]
        if dpg.vlan and isinstance(dpg.vlan, vim.VmwareDistributedVirtualSwitchVlanIdSpec):

            pg_dict.update({"vlan_id": dpg.vlan.vlanId})
        pg_dict.update(
            {
                "out_shaping": _get_dvportgroup_out_shaping(
                    props["name"], props["config.defaultPortConfig"]
                )
            }
        )
        pg_dict.update(
            {
                "security_policy": _get_dvportgroup_security_policy(
                    props["name"], props["config.defaultPortConfig"]
                )
            }
        )
        pg_dict.update(
            {"teaming": _get_dvportgroup_teaming(props["name"], props["config.defaultPortConfig"])}
        )
    return pg_dict


def list_dvportgroups(dvs=None, portgroup_names=None, service_instance=None):
    """
    Returns a list of distributed virtual switch portgroups.
    The list can be filtered by the portgroup names or by the DVS.

    dvs
        Name of the DVS containing the portgroups.
        Default value is None.

    portgroup_names
        List of portgroup names to look for. If None, all portgroups are
        returned.
        Default value is None

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.list_dvporgroups

        salt '*' vsphere.list_dvportgroups dvs=dvs1

        salt '*' vsphere.list_dvportgroups portgroup_names=[pg1]

        salt '*' vsphere.list_dvportgroups dvs=dvs1 portgroup_names=[pg1]
    """
    ret_dict = []
    proxy_type = get_proxy_type()
    if proxy_type == "esxdatacenter":
        datacenter = __salt__["esxdatacenter.get_details"]()["datacenter"]
        dc_ref = _get_proxy_target(service_instance)
    elif proxy_type == "esxcluster":
        datacenter = __salt__["esxcluster.get_details"]()["datacenter"]
        dc_ref = salt.utils.vmware.get_datacenter(service_instance, datacenter)
    if dvs:
        dvs_refs = salt.utils.vmware.get_dvss(dc_ref, dvs_names=[dvs])
        if not dvs_refs:
            raise VMwareObjectRetrievalError("DVS '{}' was not " "retrieved".format(dvs))
        dvs_ref = dvs_refs[0]
    get_all_portgroups = True if not portgroup_names else False
    for pg_ref in salt.utils.vmware.get_dvportgroups(
        parent_ref=dvs_ref if dvs else dc_ref,
        portgroup_names=portgroup_names,
        get_all_portgroups=get_all_portgroups,
    ):

        ret_dict.append(_get_dvportgroup_dict(pg_ref))
    return ret_dict


def list_uplink_dvportgroup(dvs, service_instance=None):
    """
    Returns the uplink portgroup of a distributed virtual switch.

    dvs
        Name of the DVS containing the portgroup.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.list_uplink_dvportgroup dvs=dvs_name
    """
    proxy_type = get_proxy_type()
    if proxy_type == "esxdatacenter":
        datacenter = __salt__["esxdatacenter.get_details"]()["datacenter"]
        dc_ref = _get_proxy_target(service_instance)
    elif proxy_type == "esxcluster":
        datacenter = __salt__["esxcluster.get_details"]()["datacenter"]
        dc_ref = salt.utils.vmware.get_datacenter(service_instance, datacenter)
    dvs_refs = salt.utils.vmware.get_dvss(dc_ref, dvs_names=[dvs])
    if not dvs_refs:
        raise VMwareObjectRetrievalError("DVS '{}' was not " "retrieved".format(dvs))
    uplink_pg_ref = salt.utils.vmware.get_uplink_dvportgroup(dvs_refs[0])
    return _get_dvportgroup_dict(uplink_pg_ref)


def _apply_dvportgroup_out_shaping(pg_name, out_shaping, out_shaping_conf):
    """
    Applies the values in out_shaping_conf to an out_shaping object

    pg_name
        The name of the portgroup

    out_shaping
        The vim.DVSTrafficShapingPolicy to apply the config to

    out_shaping_conf
        The out shaping config
    """
    log.trace("Building portgroup's '{}' out shaping " "policy".format(pg_name))
    if out_shaping_conf.get("average_bandwidth"):
        out_shaping.averageBandwidth = vim.LongPolicy()
        out_shaping.averageBandwidth.value = out_shaping_conf["average_bandwidth"]
    if out_shaping_conf.get("burst_size"):
        out_shaping.burstSize = vim.LongPolicy()
        out_shaping.burstSize.value = out_shaping_conf["burst_size"]
    if "enabled" in out_shaping_conf:
        out_shaping.enabled = vim.BoolPolicy()
        out_shaping.enabled.value = out_shaping_conf["enabled"]
    if out_shaping_conf.get("peak_bandwidth"):
        out_shaping.peakBandwidth = vim.LongPolicy()
        out_shaping.peakBandwidth.value = out_shaping_conf["peak_bandwidth"]


def _apply_dvportgroup_security_policy(pg_name, sec_policy, sec_policy_conf):
    """
    Applies the values in sec_policy_conf to a security policy object

    pg_name
        The name of the portgroup

    sec_policy
        The vim.DVSTrafficShapingPolicy to apply the config to

    sec_policy_conf
        The out shaping config
    """
    log.trace("Building portgroup's '{}' security policy ".format(pg_name))
    if "allow_promiscuous" in sec_policy_conf:
        sec_policy.allowPromiscuous = vim.BoolPolicy()
        sec_policy.allowPromiscuous.value = sec_policy_conf["allow_promiscuous"]
    if "forged_transmits" in sec_policy_conf:
        sec_policy.forgedTransmits = vim.BoolPolicy()
        sec_policy.forgedTransmits.value = sec_policy_conf["forged_transmits"]
    if "mac_changes" in sec_policy_conf:
        sec_policy.macChanges = vim.BoolPolicy()
        sec_policy.macChanges.value = sec_policy_conf["mac_changes"]


def _apply_dvportgroup_teaming(pg_name, teaming, teaming_conf):
    """
    Applies the values in teaming_conf to a teaming policy object

    pg_name
        The name of the portgroup

    teaming
        The vim.VmwareUplinkPortTeamingPolicy to apply the config to

    teaming_conf
        The teaming config
    """
    log.trace("Building portgroup's '{}' teaming".format(pg_name))
    if "notify_switches" in teaming_conf:
        teaming.notifySwitches = vim.BoolPolicy()
        teaming.notifySwitches.value = teaming_conf["notify_switches"]
    if "policy" in teaming_conf:
        teaming.policy = vim.StringPolicy()
        teaming.policy.value = teaming_conf["policy"]
    if "reverse_policy" in teaming_conf:
        teaming.reversePolicy = vim.BoolPolicy()
        teaming.reversePolicy.value = teaming_conf["reverse_policy"]
    if "rolling_order" in teaming_conf:
        teaming.rollingOrder = vim.BoolPolicy()
        teaming.rollingOrder.value = teaming_conf["rolling_order"]
    if "failure_criteria" in teaming_conf:
        if not teaming.failureCriteria:
            teaming.failureCriteria = vim.DVSFailureCriteria()
        failure_criteria_conf = teaming_conf["failure_criteria"]
        if "check_beacon" in failure_criteria_conf:
            teaming.failureCriteria.checkBeacon = vim.BoolPolicy()
            teaming.failureCriteria.checkBeacon.value = failure_criteria_conf["check_beacon"]
        if "check_duplex" in failure_criteria_conf:
            teaming.failureCriteria.checkDuplex = vim.BoolPolicy()
            teaming.failureCriteria.checkDuplex.value = failure_criteria_conf["check_duplex"]
        if "check_error_percent" in failure_criteria_conf:
            teaming.failureCriteria.checkErrorPercent = vim.BoolPolicy()
            teaming.failureCriteria.checkErrorPercent.value = failure_criteria_conf[
                "check_error_percent"
            ]
        if "check_speed" in failure_criteria_conf:
            teaming.failureCriteria.checkSpeed = vim.StringPolicy()
            teaming.failureCriteria.checkSpeed.value = failure_criteria_conf["check_speed"]
        if "full_duplex" in failure_criteria_conf:
            teaming.failureCriteria.fullDuplex = vim.BoolPolicy()
            teaming.failureCriteria.fullDuplex.value = failure_criteria_conf["full_duplex"]
        if "percentage" in failure_criteria_conf:
            teaming.failureCriteria.percentage = vim.IntPolicy()
            teaming.failureCriteria.percentage.value = failure_criteria_conf["percentage"]
        if "speed" in failure_criteria_conf:
            teaming.failureCriteria.speed = vim.IntPolicy()
            teaming.failureCriteria.speed.value = failure_criteria_conf["speed"]
    if "port_order" in teaming_conf:
        if not teaming.uplinkPortOrder:
            teaming.uplinkPortOrder = vim.VMwareUplinkPortOrderPolicy()
        if "active" in teaming_conf["port_order"]:
            teaming.uplinkPortOrder.activeUplinkPort = teaming_conf["port_order"]["active"]
        if "standby" in teaming_conf["port_order"]:
            teaming.uplinkPortOrder.standbyUplinkPort = teaming_conf["port_order"]["standby"]


def _apply_dvportgroup_config(pg_name, pg_spec, pg_conf):
    """
    Applies the values in conf to a distributed portgroup spec

    pg_name
        The name of the portgroup

    pg_spec
        The vim.DVPortgroupConfigSpec to apply the config to

    pg_conf
        The portgroup config
    """
    log.trace("Building portgroup's '{}' spec".format(pg_name))
    if "name" in pg_conf:
        pg_spec.name = pg_conf["name"]
    if "description" in pg_conf:
        pg_spec.description = pg_conf["description"]
    if "num_ports" in pg_conf:
        pg_spec.numPorts = pg_conf["num_ports"]
    if "type" in pg_conf:
        pg_spec.type = pg_conf["type"]

    if not pg_spec.defaultPortConfig:
        for prop in ["vlan_id", "out_shaping", "security_policy", "teaming"]:
            if prop in pg_conf:
                pg_spec.defaultPortConfig = vim.VMwareDVSPortSetting()
    if "vlan_id" in pg_conf:
        pg_spec.defaultPortConfig.vlan = vim.VmwareDistributedVirtualSwitchVlanIdSpec()
        pg_spec.defaultPortConfig.vlan.vlanId = pg_conf["vlan_id"]
    if "out_shaping" in pg_conf:
        if not pg_spec.defaultPortConfig.outShapingPolicy:
            pg_spec.defaultPortConfig.outShapingPolicy = vim.DVSTrafficShapingPolicy()
        _apply_dvportgroup_out_shaping(
            pg_name, pg_spec.defaultPortConfig.outShapingPolicy, pg_conf["out_shaping"]
        )
    if "security_policy" in pg_conf:
        if not pg_spec.defaultPortConfig.securityPolicy:
            pg_spec.defaultPortConfig.securityPolicy = vim.DVSSecurityPolicy()
        _apply_dvportgroup_security_policy(
            pg_name,
            pg_spec.defaultPortConfig.securityPolicy,
            pg_conf["security_policy"],
        )
    if "teaming" in pg_conf:
        if not pg_spec.defaultPortConfig.uplinkTeamingPolicy:
            pg_spec.defaultPortConfig.uplinkTeamingPolicy = vim.VmwareUplinkPortTeamingPolicy()
        _apply_dvportgroup_teaming(
            pg_name, pg_spec.defaultPortConfig.uplinkTeamingPolicy, pg_conf["teaming"]
        )


def create_dvportgroup(portgroup_dict, portgroup_name, dvs, service_instance=None):
    """
    Creates a distributed virtual portgroup.

    Note: The ``portgroup_name`` param will override any name already set
    in ``portgroup_dict``.

    portgroup_dict
        Dictionary with the config values the portgroup should be created with
        (example in salt.states.dvs).

    portgroup_name
        Name of the portgroup to be created.

    dvs
        Name of the DVS that will contain the portgroup.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.create_dvportgroup portgroup_dict=<dict>
            portgroup_name=pg1 dvs=dvs1
    """
    log.trace(
        "Creating portgroup'{}' in dvs '{}' "
        "with dict = {}".format(portgroup_name, dvs, portgroup_dict)
    )
    proxy_type = get_proxy_type()
    if proxy_type == "esxdatacenter":
        datacenter = __salt__["esxdatacenter.get_details"]()["datacenter"]
        dc_ref = _get_proxy_target(service_instance)
    elif proxy_type == "esxcluster":
        datacenter = __salt__["esxcluster.get_details"]()["datacenter"]
        dc_ref = salt.utils.vmware.get_datacenter(service_instance, datacenter)
    dvs_refs = salt.utils.vmware.get_dvss(dc_ref, dvs_names=[dvs])
    if not dvs_refs:
        raise VMwareObjectRetrievalError("DVS '{}' was not " "retrieved".format(dvs))
    # Make the name of the dvportgroup consistent with the parameter
    portgroup_dict["name"] = portgroup_name
    spec = vim.DVPortgroupConfigSpec()
    _apply_dvportgroup_config(portgroup_name, spec, portgroup_dict)
    salt.utils.vmware.create_dvportgroup(dvs_refs[0], spec)
    return True


def update_dvportgroup(portgroup_dict, portgroup, dvs, service_instance=True):
    """
    Updates a distributed virtual portgroup.

    portgroup_dict
        Dictionary with the values the portgroup should be update with
        (example in salt.states.dvs).

    portgroup
        Name of the portgroup to be updated.

    dvs
        Name of the DVS containing the portgroups.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.update_dvportgroup portgroup_dict=<dict>
            portgroup=pg1

        salt '*' vsphere.update_dvportgroup portgroup_dict=<dict>
            portgroup=pg1 dvs=dvs1
    """
    log.trace(
        "Updating portgroup'{}' in dvs '{}' "
        "with dict = {}".format(portgroup, dvs, portgroup_dict)
    )
    proxy_type = get_proxy_type()
    if proxy_type == "esxdatacenter":
        datacenter = __salt__["esxdatacenter.get_details"]()["datacenter"]
        dc_ref = _get_proxy_target(service_instance)
    elif proxy_type == "esxcluster":
        datacenter = __salt__["esxcluster.get_details"]()["datacenter"]
        dc_ref = salt.utils.vmware.get_datacenter(service_instance, datacenter)
    dvs_refs = salt.utils.vmware.get_dvss(dc_ref, dvs_names=[dvs])
    if not dvs_refs:
        raise VMwareObjectRetrievalError("DVS '{}' was not " "retrieved".format(dvs))
    pg_refs = salt.utils.vmware.get_dvportgroups(dvs_refs[0], portgroup_names=[portgroup])
    if not pg_refs:
        raise VMwareObjectRetrievalError("Portgroup '{}' was not " "retrieved".format(portgroup))
    pg_props = salt.utils.vmware.get_properties_of_managed_object(pg_refs[0], ["config"])
    spec = vim.DVPortgroupConfigSpec()
    # Copy existing properties in spec
    for prop in [
        "autoExpand",
        "configVersion",
        "defaultPortConfig",
        "description",
        "name",
        "numPorts",
        "policy",
        "portNameFormat",
        "scope",
        "type",
        "vendorSpecificConfig",
    ]:
        setattr(spec, prop, getattr(pg_props["config"], prop))
    _apply_dvportgroup_config(portgroup, spec, portgroup_dict)
    salt.utils.vmware.update_dvportgroup(pg_refs[0], spec)
    return True


def remove_dvportgroup(portgroup, dvs, service_instance=None):
    """
    Removes a distributed virtual portgroup.

    portgroup
        Name of the portgroup to be removed.

    dvs
        Name of the DVS containing the portgroups.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.remove_dvportgroup portgroup=pg1 dvs=dvs1
    """
    log.trace("Removing portgroup'{}' in dvs '{}' " "".format(portgroup, dvs))
    proxy_type = get_proxy_type()
    if proxy_type == "esxdatacenter":
        datacenter = __salt__["esxdatacenter.get_details"]()["datacenter"]
        dc_ref = _get_proxy_target(service_instance)
    elif proxy_type == "esxcluster":
        datacenter = __salt__["esxcluster.get_details"]()["datacenter"]
        dc_ref = salt.utils.vmware.get_datacenter(service_instance, datacenter)
    dvs_refs = salt.utils.vmware.get_dvss(dc_ref, dvs_names=[dvs])
    if not dvs_refs:
        raise VMwareObjectRetrievalError("DVS '{}' was not " "retrieved".format(dvs))
    pg_refs = salt.utils.vmware.get_dvportgroups(dvs_refs[0], portgroup_names=[portgroup])
    if not pg_refs:
        raise VMwareObjectRetrievalError("Portgroup '{}' was not " "retrieved".format(portgroup))
    salt.utils.vmware.remove_dvportgroup(pg_refs[0])
    return True


def add_host_to_dvs(
    host,
    username,
    password,
    vmknic_name,
    vmnic_name,
    dvs_name,
    target_portgroup_name,
    uplink_portgroup_name,
    protocol=None,
    port=None,
    host_names=None,
    verify_ssl=True,
):
    """
    Adds an ESXi host to a vSphere Distributed Virtual Switch and migrates
    the desired adapters to the DVS from the standard switch.

    host
        The location of the vCenter server.

    username
        The username used to login to the vCenter server.

    password
        The password used to login to the vCenter server.

    vmknic_name
        The name of the virtual NIC to migrate.

    vmnic_name
        The name of the physical NIC to migrate.

    dvs_name
        The name of the Distributed Virtual Switch.

    target_portgroup_name
        The name of the distributed portgroup in which to migrate the
        virtual NIC.

    uplink_portgroup_name
        The name of the uplink portgroup in which to migrate the
        physical NIC.

    protocol
        Optionally set to alternate protocol if the vCenter server or ESX/ESXi host is not
        using the default protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the vCenter server or ESX/ESXi host is not
        using the default port. Default port is ``443``.

    host_names:
        An array of VMware host names to migrate

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        salt some_host vsphere.add_host_to_dvs host='vsphere.corp.com'
            username='administrator@vsphere.corp.com' password='vsphere_password'
            vmknic_name='vmk0' vmnic_name='vnmic0' dvs_name='DSwitch'
            target_portgroup_name='DPortGroup' uplink_portgroup_name='DSwitch1-DVUplinks-181'
            protocol='https' port='443', host_names="['esxi1.corp.com','esxi2.corp.com','esxi3.corp.com']"

    Return Example:

    .. code-block:: yaml

        somehost:
            ----------
            esxi1.corp.com:
                ----------
                dvs:
                    DSwitch
                portgroup:
                    DPortGroup
                status:
                    True
                uplink:
                    DSwitch-DVUplinks-181
                vmknic:
                    vmk0
                vmnic:
                    vmnic0
            esxi2.corp.com:
                ----------
                dvs:
                    DSwitch
                portgroup:
                    DPortGroup
                status:
                    True
                uplink:
                    DSwitch-DVUplinks-181
                vmknic:
                    vmk0
                vmnic:
                    vmnic0
            esxi3.corp.com:
                ----------
                dvs:
                    DSwitch
                portgroup:
                    DPortGroup
                status:
                    True
                uplink:
                    DSwitch-DVUplinks-181
                vmknic:
                    vmk0
                vmnic:
                    vmnic0
            message:
            success:
                True

    This was very difficult to figure out.  VMware's PyVmomi documentation at

    https://github.com/vmware/pyvmomi/blob/35e9bc6db903aecc00c8ed7ce22698d3d3b845ad/docs/vim/DistributedVirtualSwitch.rst
    (which is a copy of the official documentation here:
    https://www.vmware.com/support/developer/converter-sdk/conv60_apireference/vim.DistributedVirtualSwitch.html)

    says to create the DVS, create distributed portgroups, and then add the
    host to the DVS specifying which physical NIC to use as the port backing.
    However, if the physical NIC is in use as the only link from the host
    to vSphere, this will fail with an unhelpful "busy" error.

    There is, however, a Powershell PowerCLI cmdlet called Add-VDSwitchPhysicalNetworkAdapter
    that does what we want.  I used Onyx (https://labs.vmware.com/flings/onyx)
    to sniff the SOAP stream from Powershell to our vSphere server and got
    this snippet out:

    .. code-block:: xml

        <UpdateNetworkConfig xmlns="urn:vim25">
          <_this type="HostNetworkSystem">networkSystem-187</_this>
          <config>
            <vswitch>
              <changeOperation>edit</changeOperation>
              <name>vSwitch0</name>
              <spec>
                <numPorts>7812</numPorts>
              </spec>
            </vswitch>
            <proxySwitch>
                <changeOperation>edit</changeOperation>
                <uuid>73 a4 05 50 b0 d2 7e b9-38 80 5d 24 65 8f da 70</uuid>
                <spec>
                <backing xsi:type="DistributedVirtualSwitchHostMemberPnicBacking">
                    <pnicSpec><pnicDevice>vmnic0</pnicDevice></pnicSpec>
                </backing>
                </spec>
            </proxySwitch>
            <portgroup>
              <changeOperation>remove</changeOperation>
              <spec>
                <name>Management Network</name><vlanId>-1</vlanId><vswitchName /><policy />
              </spec>
            </portgroup>
            <vnic>
              <changeOperation>edit</changeOperation>
              <device>vmk0</device>
              <portgroup />
              <spec>
                <distributedVirtualPort>
                  <switchUuid>73 a4 05 50 b0 d2 7e b9-38 80 5d 24 65 8f da 70</switchUuid>
                  <portgroupKey>dvportgroup-191</portgroupKey>
                </distributedVirtualPort>
              </spec>
            </vnic>
          </config>
          <changeMode>modify</changeMode>
        </UpdateNetworkConfig>

    The SOAP API maps closely to PyVmomi, so from there it was (relatively)
    easy to figure out what Python to write.
    """
    ret = {}
    ret["success"] = True
    ret["message"] = []
    service_instance = salt.utils.vmware.get_service_instance(
        host=host,
        username=username,
        password=password,
        protocol=protocol,
        port=port,
        verify_ssl=verify_ssl,
    )
    dvs = salt.utils.vmware._get_dvs(service_instance, dvs_name)
    if not dvs:
        ret["message"].append("No Distributed Virtual Switch found with name {}".format(dvs_name))
        ret["success"] = False

    target_portgroup = salt.utils.vmware._get_dvs_portgroup(dvs, target_portgroup_name)
    if not target_portgroup:
        ret["message"].append(
            "No target portgroup found with name {}".format(target_portgroup_name)
        )
        ret["success"] = False

    uplink_portgroup = salt.utils.vmware._get_dvs_uplink_portgroup(dvs, uplink_portgroup_name)
    if not uplink_portgroup:
        ret["message"].append(
            "No uplink portgroup found with name {}".format(uplink_portgroup_name)
        )
        ret["success"] = False

    if len(ret["message"]) > 0:
        return ret

    dvs_uuid = dvs.config.uuid
    try:
        host_names = _check_hosts(service_instance, host, host_names)
    except CommandExecutionError as e:
        ret["message"] = "Error retrieving hosts: {}".format(e.msg)
        return ret

    for host_name in host_names:
        ret[host_name] = {}

        ret[host_name].update(
            {
                "status": False,
                "uplink": uplink_portgroup_name,
                "portgroup": target_portgroup_name,
                "vmknic": vmknic_name,
                "vmnic": vmnic_name,
                "dvs": dvs_name,
            }
        )
        host_ref = _get_host_ref(service_instance, host, host_name)
        if not host_ref:
            ret[host_name].update({"message": "Host {1} not found".format(host_name)})
            ret["success"] = False
            continue

        dvs_hostmember_config = vim.dvs.HostMember.ConfigInfo(host=host_ref)
        dvs_hostmember = vim.dvs.HostMember(config=dvs_hostmember_config)
        p_nics = salt.utils.vmware._get_pnics(host_ref)
        p_nic = [x for x in p_nics if x.device == vmnic_name]
        if len(p_nic) == 0:
            ret[host_name].update({"message": "Physical nic {} not found".format(vmknic_name)})
            ret["success"] = False
            continue

        v_nics = salt.utils.vmware._get_vnics(host_ref)
        v_nic = [x for x in v_nics if x.device == vmknic_name]

        if len(v_nic) == 0:
            ret[host_name].update({"message": "Virtual nic {} not found".format(vmnic_name)})
            ret["success"] = False
            continue

        v_nic_mgr = salt.utils.vmware._get_vnic_manager(host_ref)
        if not v_nic_mgr:
            ret[host_name].update({"message": "Unable to get the host's virtual nic manager."})
            ret["success"] = False
            continue

        dvs_pnic_spec = vim.dvs.HostMember.PnicSpec(
            pnicDevice=vmnic_name, uplinkPortgroupKey=uplink_portgroup.key
        )
        pnic_backing = vim.dvs.HostMember.PnicBacking(pnicSpec=[dvs_pnic_spec])
        dvs_hostmember_config_spec = vim.dvs.HostMember.ConfigSpec(
            host=host_ref,
            operation="add",
        )
        dvs_config = vim.DVSConfigSpec(
            configVersion=dvs.config.configVersion, host=[dvs_hostmember_config_spec]
        )
        task = dvs.ReconfigureDvs_Task(spec=dvs_config)
        try:
            salt.utils.vmware.wait_for_task(
                task, host_name, "Adding host to the DVS", sleep_seconds=3
            )
        except Exception as e:  # pylint: disable=broad-except
            if hasattr(e, "message") and hasattr(e.message, "msg"):
                if not (host_name in e.message.msg and "already exists" in e.message.msg):
                    ret["success"] = False
                    ret[host_name].update({"message": e.message.msg})
                    continue
            else:
                raise

        network_system = host_ref.configManager.networkSystem

        source_portgroup = None
        for pg in host_ref.config.network.portgroup:
            if pg.spec.name == v_nic[0].portgroup:
                source_portgroup = pg
                break

        if not source_portgroup:
            ret[host_name].update({"message": "No matching portgroup on the vSwitch"})
            ret["success"] = False
            continue

        virtual_nic_config = vim.HostVirtualNicConfig(
            changeOperation="edit",
            device=v_nic[0].device,
            portgroup=source_portgroup.spec.name,
            spec=vim.HostVirtualNicSpec(
                distributedVirtualPort=vim.DistributedVirtualSwitchPortConnection(
                    portgroupKey=target_portgroup.key,
                    switchUuid=target_portgroup.config.distributedVirtualSwitch.uuid,
                )
            ),
        )
        current_vswitch_ports = host_ref.config.network.vswitch[0].numPorts
        vswitch_config = vim.HostVirtualSwitchConfig(
            changeOperation="edit",
            name="vSwitch0",
            spec=vim.HostVirtualSwitchSpec(numPorts=current_vswitch_ports),
        )
        proxyswitch_config = vim.HostProxySwitchConfig(
            changeOperation="edit",
            uuid=dvs_uuid,
            spec=vim.HostProxySwitchSpec(backing=pnic_backing),
        )
        host_network_config = vim.HostNetworkConfig(
            vswitch=[vswitch_config],
            proxySwitch=[proxyswitch_config],
            portgroup=[
                vim.HostPortGroupConfig(changeOperation="remove", spec=source_portgroup.spec)
            ],
            vnic=[virtual_nic_config],
        )

        try:
            network_system.UpdateNetworkConfig(changeMode="modify", config=host_network_config)
            ret[host_name].update({"status": True})
        except Exception as e:  # pylint: disable=broad-except
            if hasattr(e, "msg"):
                ret[host_name].update({"message": "Failed to migrate adapters ({})".format(e.msg)})
                continue
            else:
                raise

    return ret
