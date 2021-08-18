"""
State module for NSX-T uplink profiles
"""
import logging

import salt.utils.dictdiffer

log = logging.getLogger(__name__)

try:
    from saltext.vmware.modules import nsxt_uplink_profiles

    HAS_NSXT_UPLINK_PROFILES = True
except ImportError:
    HAS_NSXT_UPLINK_PROFILES = False


def __virtual__():
    if not HAS_NSXT_UPLINK_PROFILES:
        return False, "'nsxt_uplink_profiles' binary not found on system"
    return "nsxt_uplink_profiles"


def _needs_update(existing_profile, new_teaming, **new_profile_params):
    non_complex_params = ("mtu", "overlay_encap", "required_capabilities", "transport_vlan", "tags")
    for param in non_complex_params:
        param_existing_value = existing_profile.get(param)
        param_new_value = new_profile_params.get(param)
        if not param_existing_value and param_new_value:
            return True
        if param_existing_value and param_new_value and param_existing_value != param_new_value:
            return True
    # checking for updates in lags
    existing_lags = existing_profile.get("lags")
    new_lags = new_profile_params.get("lags")
    if not existing_lags and new_lags:
        return True
    if existing_lags and new_lags:
        sorted_existing_lags = sorted(existing_lags, key=lambda i: i["name"])
        sorted_new_lags = sorted(new_lags, key=lambda i: i["name"])
        if len(sorted_existing_lags) != len(sorted_new_lags):
            return True
        # comparing lag objects one by one
        for i in range(len(sorted_existing_lags)):
            # removing uplinks and id from existing lag as it is nsxt generated and should not be compared with new lag
            existing_current_lag = sorted_existing_lags[i].copy()
            del existing_current_lag["uplinks"]
            del existing_current_lag["id"]
            is_update_required = _are_dictionaries_different(
                existing_current_lag, sorted_new_lags[i]
            )
            if is_update_required:
                return is_update_required

    # checking for updates in named_teamings
    existing_named_teamings = existing_profile.get("named_teamings")
    new_named_teamings = new_profile_params.get("named_teamings")
    if not existing_named_teamings and new_named_teamings:
        return True
    if existing_named_teamings and new_named_teamings:
        sorted_existing_named_teamings = sorted(existing_named_teamings, key=lambda i: i["name"])
        sorted_new_named_teamings = sorted(new_named_teamings, key=lambda i: i["name"])
        if len(sorted_existing_named_teamings) != len(sorted_new_named_teamings):
            return True
        # comparing named_teamings objects one by one
        for i in range(len(sorted_existing_named_teamings)):
            is_update_required = _are_dictionaries_different(
                sorted_existing_named_teamings[i], sorted_new_named_teamings[i]
            )
            if is_update_required:
                return is_update_required

    # checking for updates in teaming. Teaming is a mandatory param, so no need to validate existence
    return _are_dictionaries_different(existing_profile["teaming"], new_teaming)


def _are_dictionaries_different(obj1, obj2):
    # returns True if objects are different, else False
    changes_dict = salt.utils.dictdiffer.deep_diff(obj1, obj2)
    return True if changes_dict else False


def present(
    name,
    hostname,
    username,
    password,
    display_name,
    teaming,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
    lags=None,
    mtu=None,
    named_teamings=None,
    overlay_encap=None,
    required_capabilities=None,
    tags=None,
    transport_vlan=None,
    description=None,
    resource_type=None,
):
    """
    Creates or Updates(if present with same display_name) uplink profiles(resource_type:UplinkHostSwitchProfile).
    Fails if multiple uplink profiles are found with same display_name

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_uplink_profiles.create hostname=nsxt-manager.local username=admin ...

    .. code-block:: yaml

        create_uplink_profile:
          nsxt_uplink_profiles.present:
            - name: Create uplink profile
              hostname: {{ pillar['nsxt_manager_hostname'] }}
              username: {{ pillar['nsxt_manager_username'] }}
              password: {{ pillar['nsxt_manager_password'] }}
              cert: {{ pillar['nsxt_manager_certificate'] }}
              verify_ssl: <False/True>
              display_name: <uplink profile name>
              description: <uplink profile description>
              resource_type: UplinkHostSwitchProfile
              teaming:
                active_list:
                  -  uplink_name: <Name of the uplink>
                     uplink_type: <PNIC/LAG>
                  -  uplink_name: <Name of the uplink>
                     uplink_type: <PNIC/LAG>
                policy: <FAILOVER_ORDER/LOADBALANCE_SRCID/LOADBALANCE_SRC_MAC>
                standby_list:
                  -  uplink_name: <Name of the uplink>
                     uplink_type: <PNIC/LAG>
              tags:
                - tag: <tag-key-1>
                  scope: <tag-value-1>
                - tag: <tag-key-2>
                  scope: <tag-value-2>
              mtu: <mtu value>
              transport_vlan: <vlan_id>
              lags:
                -  load_balance_algorithm: <SRCMAC/DESTMAC/SRCDESTMAC/SRCDESTIPVLAN/SRCDESTMACIPPORT>
                   mode: <ACTIVE/PASSIVE>
                   name: <name of the lag>
                   number_of_uplinks: <Integer>
                   timeout_type: <SLOW/FAST>
                -  load_balance_algorithm: <SRCMAC/DESTMAC/SRCDESTMAC/SRCDESTIPVLAN/SRCDESTMACIPPORT>
                   mode: <ACTIVE/PASSIVE>
                   name: <name of the lag>
                   number_of_uplinks: <Integer>
                   timeout_type: <SLOW/FAST>
              named_teamings:
                -  name: <Name of the teaming>
                   active_list:
                     -  uplink_name: <Name of the uplink>
                        uplink_type: <PNIC/LAG>
                     -  uplink_name: <Name of the uplink>
                        uplink_type: <PNIC/LAG>
                   policy: <FAILOVER_ORDER/LOADBALANCE_SRCID/LOADBALANCE_SRC_MAC>
                   standby_list:
                     -  uplink_name: <Name of the uplink>
                        uplink_type: <PNIC/LAG>

    name
        Name of the operation

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    display_name
        The name of the uplink profile

    resource_type
        Must be set to the value UplinkHostSwitchProfile. Default is UplinkHostSwitchProfile in Salt Module

    teaming
        Default TeamingPolicy associated with this UplinkProfile. Object with following parameters:

        .. code::

            {'standby_list':[],'active_list':[{'uplink_name':'uplink3','uplink_type':'PNIC'}],'policy':'FAILOVER_ORDER'}

        active_list
            List of Uplinks used in active list. Array of Uplink objects.

            .. code::

                 active_list='[
                    {
                    "uplink_name": "uplink3",
                    "uplink_type": "PNIC"
                    }
                ]'

            Parameters as follows:

            uplink_name
                Name of this uplink

            uplink_type
                Type of the uplink. PNIC or LAG


        policy
            Teaming policy. Required field.
            Values could be one among FAILOVER_ORDER, LOADBALANCE_SRCID, LOADBALANCE_SRC_MAC

        standby_list
            List of Uplinks used in standby list. Array of Uplink objects.

            .. code::

                standby_list=[
                    {
                    "uplink_name": "uplink2",
                    "uplink_type": "PNIC"
                    }
                ]

           Parameters as follows:

            uplink_name
                Name of this uplink

            uplink_type
                Type of the uplink. PNIC or LAG

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
        verification. If the client certificate common name and hostname do not match (in case of self-signed
        certificates), specify the certificate common name as part of this parameter. This value is then used to
        compare against certificate common name

    lags
        (Optional) list of LACP group

    mtu
        (Optional) Maximum Transmission Unit used for uplinks

    named_teamings
        (Optional) List of named uplink teaming policies that can be used by logical switches.
         Array of NamedTeamingPolicy

    overlay_encap
        (Optional) The protocol used to encapsulate overlay traffic

    required_capabilities
        (Optional) List of string

    tags
        (Optional) Opaque identifier meaninful to API user. Array of Tag

    transport_vlan
        (Optional) VLAN used for tagging Overlay traffic of associated HostSwitch. Type: integer

    description
        (Optional) Description for the resource

    """
    ret = {"name": name, "result": True, "comment": "", "changes": {}}
    uplink_profiles_result = __salt__["nsxt_uplink_profiles.get_by_display_name"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        display_name=display_name,
    )
    if "error" in uplink_profiles_result:
        ret["result"] = False
        ret["comment"] = "Failed to get uplink profiles from NSX-T Manager : {}".format(
            uplink_profiles_result["error"]
        )
        return ret

    result_count = len(uplink_profiles_result.get("results"))
    if result_count > 1:
        ret["result"] = False
        ret["comment"] = (
            "Found multiple results(result_count={count}) for uplink profiles with "
            "display_name {display_name}".format(count=result_count, display_name=display_name)
        )
        return ret

    if __opts__["test"]:
        if result_count == 0:
            ret["result"] = None
            ret["comment"] = "Uplink profile will be created in NSX-T Manager"
        else:
            ret["result"] = None
            ret["comment"] = "Uplink profile would be updated in NSX-T Manager"
        return ret

    if result_count == 0:
        # create uplink profile
        log.info(
            "Creating new uplink profile as no results were found in NSX-T with display_name %s",
            display_name,
        )
        create_result = __salt__["nsxt_uplink_profiles.create"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            display_name=display_name,
            teaming=teaming,
            lags=lags,
            mtu=mtu,
            named_teamings=named_teamings,
            overlay_encap=overlay_encap,
            required_capabilities=required_capabilities,
            tags=tags,
            transport_vlan=transport_vlan,
            description=description,
        )

        if "error" in create_result:
            ret["result"] = False
            ret["comment"] = create_result["error"]
            return ret

        ret["comment"] = "Created uplink profile {display_name}".format(display_name=display_name)
        ret["changes"]["new"] = create_result
        return ret
    else:
        # update uplink profile
        existing_uplink_profile = uplink_profiles_result.get("results")[0]
        update_required = _needs_update(
            existing_profile=existing_uplink_profile,
            new_teaming=teaming,
            lags=lags,
            mtu=mtu,
            named_teamings=named_teamings,
            overlay_encap=overlay_encap,
            required_capabilities=required_capabilities,
            tags=tags,
            transport_vlan=transport_vlan,
            description=description,
        )
        if update_required:
            log.info("Updating uplink profile with display_name %s", display_name)
            # setting params from existing object back to current object, if missed
            optional_params_dict = {
                "lags": lags,
                "mtu": mtu,
                "named_teamings": named_teamings,
                "overlay_encap": overlay_encap,
                "required_capabilities": required_capabilities,
                "tags": tags,
                "transport_vlan": transport_vlan,
                "description": description,
            }

            for key in optional_params_dict.keys():
                existing_value = existing_uplink_profile.get(key)
                if not optional_params_dict.get(key) and existing_value:
                    optional_params_dict[key] = existing_uplink_profile[key]

            update_result = __salt__["nsxt_uplink_profiles.update"](
                hostname=hostname,
                username=username,
                password=password,
                verify_ssl=verify_ssl,
                cert=cert,
                cert_common_name=cert_common_name,
                display_name=display_name,
                teaming=teaming,
                uplink_profile_id=existing_uplink_profile["id"],
                revision=existing_uplink_profile["_revision"],
                **optional_params_dict
            )

            if "error" in update_result:
                ret["result"] = False
                ret["comment"] = update_result["error"]
                return ret

            ret["comment"] = "Updated uplink profile {display_name} successfully".format(
                display_name=display_name
            )
            ret["changes"]["old"] = existing_uplink_profile
            ret["changes"]["new"] = update_result
            return ret
        else:
            log.info("Update is not required. Uplink profile with same params already exists")
            ret[
                "comment"
            ] = "Uplink profile already exists with similar params. No action to perform"
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

    Deletes uplink profile with provided display_name in NSX-T Manager, if present.
    Fails if multiple uplink profiles are found with same display_name

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_uplink_profiles.absent hostname=nsxt-manager.local username=admin ...

    .. code-block:: yaml

        delete_uplink_profile:
          nsxt_uplink_profiles.absent:
            - name: <Name of the operation>
              hostname: {{ pillar['nsxt_manager_hostname'] }}
              username: {{ pillar['nsxt_manager_username'] }}
              password: {{ pillar['nsxt_manager_password'] }}
              cert: {{ pillar['nsxt_manager_certificate'] }}
              display_name: <display_name of the uplink profile>
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
        Display name of the uplink profile to delete

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
         verification. If the client certificate common name and hostname do not match (in case of self-signed
         certificates), specify the certificate common name as part of this parameter. This value is then used to
         compare against certificate common name.

    """
    ret = {"name": name, "result": True, "comment": "", "changes": {}}
    uplink_profiles_result = __salt__["nsxt_uplink_profiles.get_by_display_name"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        display_name=display_name,
    )
    if "error" in uplink_profiles_result:
        ret["result"] = False
        ret["comment"] = "Failed to get uplink profiles from NSX-T Manager : {}".format(
            uplink_profiles_result["error"]
        )
        return ret

    result_count = len(uplink_profiles_result.get("results"))
    if result_count > 1:
        ret["result"] = False
        ret["comment"] = (
            "Found multiple results(result_count={count}) for uplink profiles with "
            "display_name {display_name}".format(count=result_count, display_name=display_name)
        )
        return ret

    if __opts__["test"]:
        if result_count == 0:
            ret["result"] = None
            ret[
                "comment"
            ] = "No uplink profile with display_name: {} found in NSX-T Manager".format(
                display_name
            )
        else:
            ret["result"] = None
            ret["comment"] = "Uplink profile with display_name: {} will be deleted".format(
                display_name
            )
        return ret

    if result_count == 0:
        ret["comment"] = "No uplink profile with display_name: {} found in NSX-T Manager".format(
            display_name
        )
        return ret
    else:
        uplink_profile_to_delete = uplink_profiles_result.get("results")[0]
        delete_result = __salt__["nsxt_uplink_profiles.delete"](
            hostname=hostname,
            username=username,
            password=password,
            uplink_profile_id=uplink_profile_to_delete["id"],
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
        )
        if "error" in delete_result:
            ret["result"] = False
            ret["comment"] = "Failed to delete uplink profile : {}".format(delete_result["error"])
            return ret
        else:
            ret["comment"] = "Uplink profile with display_name: {} successfully deleted".format(
                display_name
            )
            ret["changes"]["old"] = uplink_profile_to_delete
            ret["changes"]["new"] = {}
            return ret
