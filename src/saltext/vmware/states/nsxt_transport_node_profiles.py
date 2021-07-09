"""
State module for NSX-T transport node profiles
"""
import logging

import salt.utils.dictdiffer
from saltext.vmware.utils import common
from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)

try:
    from saltext.vmware.modules import nsxt_transport_node_profiles

    HAS_NSXT_TRANSPORT_NODE_PROFILES = True
except ImportError:
    HAS_NSXT_TRANSPORT_NODE_PROFILES = False


def __virtual__():
    if not HAS_NSXT_TRANSPORT_NODE_PROFILES:
        return False, "'nsxt_transport_node_profiles' binary not found on system"
    return "nsxt_transport_node_profiles"


def _needs_update(existing_profile, new_profile_params):
    existing_profile_host_switch_spec = existing_profile.get("host_switch_spec")
    update_inputs_host_switch_spec = new_profile_params.get("host_switch_spec")
    if not existing_profile_host_switch_spec and update_inputs_host_switch_spec:
        return True
    if (
        existing_profile_host_switch_spec
        and update_inputs_host_switch_spec
        and salt.utils.dictdiffer.deep_diff(
            existing_profile_host_switch_spec, update_inputs_host_switch_spec
        )
    ):
        return True

    optional_params = ("ignore_overridden_hosts", "description", "transport_zone_endpoints")
    for param in optional_params:
        existing_profile_param_value = existing_profile.get(param)
        update_inputs_param_value = new_profile_params.get(param)
        if not existing_profile_param_value and update_inputs_param_value:
            return True
        if (
            existing_profile_param_value
            and update_inputs_param_value
            and existing_profile_param_value != new_profile_params.get(param)
        ):
            return True
    return False


def _get_by_display_name_result_from_module(
    hostname, username, password, verify_ssl, cert, cert_common_name, module_name, display_name
):
    module_to_call = module_name + ".get_by_display_name"
    result = __salt__[module_to_call](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        display_name=display_name,
    )
    if "error" in result:
        return result
    if len(result["results"]) > 1:
        return {
            "error": "Multiple results for {} with display_name {}".format(
                module_name, display_name
            )
        }
    if not result["results"]:
        return {"error": "No results for {} with display_name {}".format(module_name, display_name)}
    return result["results"][0]


def _get_by_display_name(
    hostname, username, password, endpoint, object_type, display_name, **kwargs
):
    url = "https://{management_host}/api/v1/{endpoint}".format(
        management_host=hostname, endpoint=endpoint
    )

    object_list = common._read_paginated(
        func=_get,
        display_name=display_name,
        url=url,
        username=username,
        password=password,
        **kwargs
    )

    if "error" in object_list:
        return object_list

    if len(object_list) > 1:
        return {
            "error": "Multiple results for {} with display_name {}".format(
                object_type, display_name
            )
        }
    if not object_list:
        return {"error": "No results for {} with display_name {}".format(object_type, display_name)}

    return object_list[0]


def _get(url, username, password, cursor=None, cert_common_name=None, verify_ssl=True, cert=None):
    params = dict()
    if cursor:
        params["cursor"] = cursor

    return nsxt_request.call_api(
        method="get",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
        params=params,
    )


def _update_params_with_id(
    hostname, username, password, cert, cert_common_name, verify_ssl, transport_node_profile_params
):
    for host_switch in transport_node_profile_params["host_switch_spec"]["host_switches"]:
        host_switch_type = host_switch.get("host_switch_type")
        if host_switch_type == "VDS":
            host_switch_name = host_switch.get("host_switch_name")
            if host_switch_name:
                result = _get_by_display_name(
                    hostname,
                    username,
                    password,
                    endpoint="fabric/virtual-switches",
                    object_type=host_switch_type,
                    display_name=host_switch_name,
                    cert=cert,
                    verify_ssl=verify_ssl,
                    cert_common_name=cert_common_name,
                )
                if "error" in result:
                    return result
                host_switch["host_switch_id"] = result["id"]
        host_switch_profiles = host_switch.pop("host_switch_profiles", None)
        if host_switch_profiles is not None:
            host_switch_profile_ids = []
            for host_switch_profile in host_switch_profiles:
                profile_obj = {}
                result = _get_by_display_name(
                    hostname,
                    username,
                    password,
                    endpoint="host-switch-profiles?include_system_owned=true",
                    object_type="host-switch-profiles",
                    display_name=host_switch_profile["name"],
                    cert=cert,
                    verify_ssl=verify_ssl,
                    cert_common_name=cert_common_name,
                )
                if "error" in result:
                    return result
                profile_obj["key"] = host_switch_profile["type"]
                profile_obj["value"] = result["id"]
                host_switch_profile_ids.append(profile_obj)
            host_switch["host_switch_profile_ids"] = host_switch_profile_ids

        ip_assignment_spec = host_switch.get("ip_assignment_spec")
        if ip_assignment_spec:
            ip_pool_name = ip_assignment_spec.pop("ip_pool_name", None)
            if ip_pool_name:
                result = _get_by_display_name_result_from_module(
                    hostname=hostname,
                    username=username,
                    password=password,
                    verify_ssl=verify_ssl,
                    cert=cert,
                    cert_common_name=cert_common_name,
                    module_name="nsxt_ip_pools",
                    display_name=ip_pool_name,
                )
                if "error" in result:
                    return result
                host_switch["ip_assignment_spec"]["ip_pool_id"] = result["id"]

        transport_zone_endpoints = host_switch.get("transport_zone_endpoints")
        if transport_zone_endpoints:
            for transport_zone_endpoint in transport_zone_endpoints:
                transport_zone_name = transport_zone_endpoint.pop("transport_zone_name", None)
                if transport_zone_name:
                    result = _get_by_display_name(
                        hostname,
                        username,
                        password,
                        endpoint="transport-zones",
                        object_type="transport zone",
                        display_name=transport_zone_name,
                        cert=cert,
                        verify_ssl=verify_ssl,
                        cert_common_name=cert_common_name,
                    )
                    if "error" in result:
                        return result
                    transport_zone_endpoint["transport_zone_id"] = result["id"]

        vmk_install_migrations = host_switch.get("vmk_install_migration")
        if vmk_install_migrations:
            for vmk_install_migration in vmk_install_migrations:
                destination_network_name = vmk_install_migration.pop(
                    "destination_network_name", None
                )
                if destination_network_name:
                    result = _get_by_display_name(
                        hostname,
                        username,
                        password,
                        endpoint="logical-switches",
                        object_type="destination network/logical switches",
                        display_name=destination_network_name,
                        cert=cert,
                        verify_ssl=verify_ssl,
                        cert_common_name=cert_common_name,
                    )
                    if "error" in result:
                        return result
                    vmk_install_migration["destination_network"] = result["id"]

    transport_zone_endpoints = transport_node_profile_params.get("transport_zone_endpoints")
    if transport_zone_endpoints:
        for transport_zone_endpoint in transport_zone_endpoints:
            transport_zone_name = transport_zone_endpoint.pop("transport_zone_name", None)
            if transport_zone_name:
                result = _get_by_display_name(
                    hostname,
                    username,
                    password,
                    endpoint="transport-zones",
                    object_type="transport zone",
                    display_name=transport_zone_name,
                    cert=cert,
                    verify_ssl=verify_ssl,
                    cert_common_name=cert_common_name,
                )
                if "error" in result:
                    return result
                transport_zone_endpoint["transport_zone_id"] = result["id"]
    else:
        transport_node_profile_params["transport_zone_endpoints"] = []
    return transport_node_profile_params


def present(
    name,
    hostname,
    username,
    password,
    display_name,
    host_switch_spec,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
    transport_zone_endpoints=None,
    ignore_overridden_hosts=None,
    description=None,
):
    """

    Creates or Updates(if present with same display_name) transport node profiles
    Fails if multiple transport node profiles are found with same display_name

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_transport_node_profiles.create hostname=nsxt-manager.local username=admin ...

    .. code-block:: yaml

        create_transport_node_profile:
          nsxt_transport_node_profiles.present:
            - name: Create uplink profile
              hostname: {{ pillar['nsxt_manager_hostname'] }}
              username: {{ pillar['nsxt_manager_username'] }}
              password: {{ pillar['nsxt_manager_password'] }}
              cert: {{ pillar['nsxt_manager_certificate'] }}
              verify_ssl: <False/True>
              display_name: <uplink profile name>
              description: <uplink profile description>
              host_switch_spec:
                resource_type: "StandardHostSwitchSpec"
                host_switches:
                  - host_switch_name: "hostswitch1"
                    host_switch_mode: "<STANDARD/ENS/ENS_INTERRUPT>"
                    host_switch_type: "<NVDS/VDS>"
                    host_switch_profiles:
                      - name: "<host_switch_profile_name>"
                        type: "<UplinkHostSwitchProfile/LldpHostSwitchProfile/NiocProfile>"
                    pnics:
                      - device_name: "vmnic1"
                        uplink_name: "uplink-1"
                    ip_assignment_spec:
                      resource_type: "StaticIpPoolSpec"
                      ip_pool_name: "IPPool-IPV4-1"
                    transport_zone_endpoints:
                      - transport_zone_name: "TZ1"
                    vmk_install_migration:
                      - device_name: vmk0
                        destination_network_name: "ls_vmk_Mgmt"

    name
        Name of the operation

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    display_name
        The name of the transport node profile

    host_switch_spec
        Transport node host switch specification. The HostSwitchSpec is the base class for standard and preconfigured
        host switch specifications. Only standard host switches are supported in the transport node profile.

        resource_type
            Must be set to the value StandardHostSwitchSpec

        host_switches
            Array of transport Node host switches.

            host_switch_name
                Host switch name. This name will be used to reference a host switch. Default is "nsxDefaultHostSwitch"

            host_switch_mode
                Operational mode of a HostSwitch. STANDARD, ENS, ENS_INTERRUPT

            host_switch_id
                The host switch id. This ID will be used to reference a host switch.

            host_switch_profiles
                Array of host switch profiles. Each entry should have name of the profile and type of the profile

                .. code::

                    host_switch_profiles:
                      -  name: <name of the profile>
                         type: <type of the profile>

            ip_assignment_spec
                Specification for IPs to be used with host switch virtual tunnel endpoints

                resource_type
                    Resource type for IP assignment

                ip_pool_name
                    Name of the IP pool

            pnics
                Array of Physical NICs connected to the host switch

                device_name
                    device name or key

                uplink_name
                    Uplink name for this Pnic

            transport_zone_endpoints
                Array of transport zones

                transport_zone_name
                    Name of the transport zone

            vmk_install_migration
                Array of VmknicNetwork. The vmknic and logical switch mappings

                destination_network
                    The network id to which the ESX vmk interface will be migrated.

                device_name
                    ESX vmk interface name

    transport_zone_endpoints
        (Optional) This is deprecated. TransportZoneEndPoints should be specified per host switch at
        StandardHostSwitch through Transport Node or Transport Node Profile configuration. Array of transport zones.

    ignore_overridden_hosts
        (Optional) Boolean which determines if cluster-level configuration should be applied on overridden hosts. Default: False

    description
        (Optional) Description

    """
    ret = {"name": name, "result": True, "comment": "", "changes": {}}
    transport_node_profiles_result = __salt__["nsxt_transport_node_profiles.get_by_display_name"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        display_name=display_name,
    )
    if "error" in transport_node_profiles_result:
        ret["result"] = False
        ret["comment"] = "Failed to get transport node profiles from NSX-T Manager : {}".format(
            transport_node_profiles_result["error"]
        )
        return ret

    result_count = len(transport_node_profiles_result.get("results"))
    if result_count > 1:
        ret["result"] = False
        ret["comment"] = (
            "Found multiple results(result_count={count}) for transport node profiles with "
            "display_name {display_name}".format(count=result_count, display_name=display_name)
        )
        return ret

    if __opts__["test"]:
        if result_count == 0:
            ret["result"] = None
            ret["comment"] = "Transport node profile will be created in NSX-T Manager"
        else:
            ret["result"] = None
            ret["comment"] = "Transport node profile would be updated in NSX-T Manager"
        return ret

    existing_transport_node_profile = (
        None if result_count == 0 else transport_node_profiles_result.get("results")[0]
    )

    # transport_node_profile_params dict will be populated appropriately and passed to execution module for create/updates
    transport_node_profile_params = common._filter_kwargs(
        allowed_kwargs=("description", "transport_zone_endpoints", "ignore_overridden_hosts"),
        default_dict={"display_name": display_name, "host_switch_spec": host_switch_spec},
        description=description,
        transport_zone_endpoints=transport_zone_endpoints,
        ignore_overridden_hosts=ignore_overridden_hosts,
    )

    current_transport_node_profile = _update_params_with_id(
        hostname,
        username,
        password,
        cert,
        cert_common_name,
        verify_ssl,
        transport_node_profile_params,
    )
    if "error" in current_transport_node_profile:
        ret["result"] = False
        ret["comment"] = "Failed while creating payload for transport node profile: {}".format(
            current_transport_node_profile["error"]
        )
        return ret
    current_transport_node_profile["resource_type"] = "TransportNodeProfile"
    current_transport_node_profile["ignore_overridden_hosts"] = ignore_overridden_hosts or False

    if existing_transport_node_profile is None:
        # create transport node profile
        log.info(
            "Creating new transport node profile as no results were found in NSX-T with display_name %s",
            display_name,
        )
        create_result = __salt__["nsxt_transport_node_profiles.create"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            display_name=display_name,
            host_switch_spec=current_transport_node_profile["host_switch_spec"],
            transport_zone_endpoints=transport_zone_endpoints,
            ignore_overridden_hosts=ignore_overridden_hosts,
            description=description,
        )

        if create_result and "error" in create_result:
            ret["result"] = False
            ret["comment"] = "Failed to create transport node profile due to error: {}".format(
                create_result["error"]
            )
            return ret

        ret["comment"] = "Created transport node profile {display_name}".format(
            display_name=display_name
        )
        ret["changes"]["new"] = create_result
        return ret
    else:
        update_required = _needs_update(
            existing_transport_node_profile, current_transport_node_profile
        )
        if update_required:
            log.info("Updating transport node profile with display_name %s", display_name)
            update_result = __salt__["nsxt_transport_node_profiles.update"](
                hostname=hostname,
                username=username,
                password=password,
                verify_ssl=verify_ssl,
                cert=cert,
                cert_common_name=cert_common_name,
                display_name=display_name,
                host_switch_spec=current_transport_node_profile["host_switch_spec"],
                transport_node_profile_id=existing_transport_node_profile["id"],
                revision=existing_transport_node_profile["_revision"],
                transport_zone_endpoints=transport_zone_endpoints,
                ignore_overridden_hosts=ignore_overridden_hosts,
                description=description,
            )
            if update_result and "error" in update_result:
                ret["result"] = False
                ret["comment"] = "Failure while updating transport node profile: {}".format(
                    update_result["error"]
                )
                return ret
            ret["comment"] = "Updated transport node profile {display_name} successfully".format(
                display_name=display_name
            )
            ret["changes"]["old"] = existing_transport_node_profile
            ret["changes"]["new"] = update_result
            return ret
        else:
            log.info(
                "Update is not required. Transport node profile with same params already exists"
            )
            ret[
                "comment"
            ] = "Transport node profile already exists with similar params. No action to perform"
            return ret


def absent(
    name,
    hostname,
    username,
    password,
    display_name,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
):
    """

    Deletes transport node profile with provided display_name in NSX-T Manager, if present.
    Fails if multiple transport node profiles are found with same display_name

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_transport_node_profiles.absent hostname=nsxt-manager.local username=admin ...

    -- code-block :: yaml

        delete_transport_node_profile:
          nsxt_transport_node_profiles.absent:
            - name: <Name of the operation>
              hostname: {{ pillar['nsxt_manager_hostname'] }}
              username: {{ pillar['nsxt_manager_username'] }}
              password: {{ pillar['nsxt_manager_password'] }}
              cert: {{ pillar['nsxt_manager_certificate'] }}
              display_name: <display_name of the transport node profile>
              verify_ssl: <False/True>


    name
        Name of the operation to perform

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    display_name
        Display name of the transport node profile to delete

    cert
        Path to the SSL certificate file to connect to NSX-T manager

    verify_ssl
        Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
         verification. If the client certificate common name and hostname do not match (in case of self-signed
         certificates), specify the certificate common name as part of this parameter. This value is then used to
         compare against certificate common name.

    """
    ret = {"name": name, "result": True, "comment": "", "changes": {}}
    transport_node_profiles_result = __salt__["nsxt_transport_node_profiles.get_by_display_name"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        display_name=display_name,
    )
    if "error" in transport_node_profiles_result:
        ret["result"] = False
        ret["comment"] = "Failed to get transport node profiles from NSX-T Manager : {}".format(
            transport_node_profiles_result["error"]
        )
        return ret

    result_count = len(transport_node_profiles_result.get("results"))
    if result_count > 1:
        ret["result"] = False
        ret["comment"] = (
            "Found multiple results(result_count={count}) for transport node profiles with "
            "display_name {display_name}".format(count=result_count, display_name=display_name)
        )
        return ret

    if __opts__["test"]:
        if result_count == 0:
            ret["result"] = None
            ret[
                "comment"
            ] = "No transport node profile with display_name: {} found in NSX-T Manager".format(
                display_name
            )
        else:
            ret["result"] = None
            ret["comment"] = "Transport node profile with display_name: {} will be deleted".format(
                display_name
            )
        return ret

    if result_count == 0:
        ret[
            "comment"
        ] = "No transport node profile with display_name: {} found in NSX-T Manager".format(
            display_name
        )
        return ret
    else:
        transport_node_profile_to_delete = transport_node_profiles_result.get("results")[0]
        delete_result = __salt__["nsxt_transport_node_profiles.delete"](
            hostname=hostname,
            username=username,
            password=password,
            transport_node_profile_id=transport_node_profile_to_delete["id"],
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
        )
        if "error" in delete_result:
            ret["result"] = False
            ret["comment"] = "Failed to delete transport node profile : {}".format(
                delete_result["error"]
            )
            return ret
        else:
            ret[
                "comment"
            ] = "Transport node profile with display_name: {} successfully deleted".format(
                display_name
            )
            ret["changes"]["old"] = transport_node_profile_to_delete
            ret["changes"]["new"] = {}
            return ret
