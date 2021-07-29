"""
State module for NSX-T tier0 gateway
"""
import logging

log = logging.getLogger(__name__)
try:
    from saltext.vmware.modules import nsxt_policy_tier0

    HAS_POLICY_TIER0 = True
except ImportError:
    HAS_POLICY_TIER0 = False


def __virtual__():
    if not HAS_POLICY_TIER0:
        return False, "'nsxt_policy_tier0' binary not found on system"
    return "nsxt_policy_tier0"


def present(
    name,
    hostname,
    username,
    password,
    display_name,
    arp_limit=None,
    bfd_peers=None,
    cert=None,
    cert_common_name=None,
    description=None,
    default_rule_logging=None,
    dhcp_config_id=None,
    disable_firewall=None,
    failover_mode=None,
    force_whitelisting=None,
    ha_mode=None,
    id=None,
    internal_transit_subnets=None,
    intersite_config=None,
    ipv6_ndra_profile_id=None,
    ipv6_dad_profile_id=None,
    locale_services=None,
    rd_admin_field=None,
    state=None,
    static_routes=None,
    tags=None,
    transit_subnets=None,
    verify_ssl=True,
    vrf_config=None,
):

    ret = {"name": name, "result": True, "comment": "", "changes": {}}
    if state and str(state).lower() == "absent":
        ret["result"] = False
        ret["comment"] = (
            "Use absent method to delete tier0 resource. "
            "Only tier0 sub-resources are allowed to be deleted here."
        )
        return ret
    tier_0_result = __salt__["nsxt_policy_tier0.get_by_display_name"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        display_name=display_name,
    )
    if "error" in tier_0_result:
        ret["result"] = False
        ret["comment"] = "Failed to get tier-0 gateways from NSX-T Manager : {}".format(
            tier_0_result["error"]
        )
        return ret

    result_count = len(tier_0_result.get("results"))
    if result_count > 1:
        ret["result"] = False
        ret["comment"] = (
            "Found multiple results(result_count={count}) for Tier-0 gateway with "
            "display_name {display_name}".format(count=result_count, display_name=display_name)
        )
        return ret

    if __opts__["test"]:
        if result_count == 0:
            ret["result"] = None
            ret["comment"] = "Tier-0 gateway will be created in NSX-T Manager"
        else:
            ret["result"] = None
            ret["comment"] = "Tier-0 gateway would be updated in NSX-T Manager"
        return ret

    if result_count == 0:
        # create flow
        log.info(
            "Creating new tier0 gateway as no results were found in NSX-T with display_name %s",
            display_name,
        )
        create_execution_logs = __salt__["nsxt_policy_tier0.create_or_update"](
            hostname=hostname,
            username=username,
            password=password,
            id=id,
            arp_limit=arp_limit,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            display_name=display_name,
            tags=tags,
            description=description,
            default_rule_logging=default_rule_logging,
            ha_mode=ha_mode,
            disable_firewall=disable_firewall,
            failover_mode=failover_mode,
            force_whitelisting=force_whitelisting,
            internal_transit_subnets=internal_transit_subnets,
            intersite_config=intersite_config,
            ipv6_ndra_profile_id=ipv6_ndra_profile_id,
            ipv6_dad_profile_id=ipv6_dad_profile_id,
            rd_admin_field=rd_admin_field,
            transit_subnets=transit_subnets,
            dhcp_config_id=dhcp_config_id,
            vrf_config=vrf_config,
            static_routes=static_routes,
            bfd_peers=bfd_peers,
            locale_services=locale_services,
        )

        log.info("Execution logs for creating tier 0 : {}".format(create_execution_logs))
        if "error" in create_execution_logs[len(create_execution_logs) - 1]:
            ret["result"] = False
            ret[
                "comment"
            ] = "Failed while creating tier0 gateway and sub-resources: {}\n Execution logs: {}".format(
                create_execution_logs[len(create_execution_logs) - 1]["error"],
                create_execution_logs,
            )
            return ret
        tier0_execution_log = next(
            (
                execution_log
                for execution_log in create_execution_logs
                if execution_log.get("resourceType") == "tier0"
            ),
            None,
        )
        tier_0_id = tier0_execution_log.get("results").get("id")
        tier0_hierarchy = __salt__["nsxt_policy_tier0.get_hierarchy"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            tier0_id=tier_0_id,
        )
        if "error" in tier0_hierarchy:
            ret["result"] = False
            ret["comment"] = "Failed while querying tier0 gateway and its sub-resources: {}".format(
                tier0_hierarchy["error"]
            )
            return ret
        ret["comment"] = "Created Tier-0 gateway {display_name} successfully".format(
            display_name=display_name
        )
        ret["changes"]["new"] = tier0_hierarchy
        return ret

    else:
        log.info("Updating existing tier0 gateway with display_name %s", display_name)
        tier_0_id = tier_0_result["results"][0]["id"]
        tier0_hierarchy_before_update = __salt__["nsxt_policy_tier0.get_hierarchy"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            tier0_id=tier_0_id,
        )
        if "error" in tier0_hierarchy_before_update:
            ret["result"] = False
            ret[
                "comment"
            ] = "Failed while querying tier0 gateway and its sub-resources.: {}".format(
                tier0_hierarchy_before_update["error"]
            )
            return ret

        update_execution_logs = __salt__["nsxt_policy_tier0.create_or_update"](
            hostname=hostname,
            username=username,
            password=password,
            id=id,
            arp_limit=arp_limit,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            display_name=display_name,
            tags=tags,
            description=description,
            default_rule_logging=default_rule_logging,
            ha_mode=ha_mode,
            disable_firewall=disable_firewall,
            failover_mode=failover_mode,
            force_whitelisting=force_whitelisting,
            internal_transit_subnets=internal_transit_subnets,
            intersite_config=intersite_config,
            ipv6_ndra_profile_id=ipv6_ndra_profile_id,
            ipv6_dad_profile_id=ipv6_dad_profile_id,
            rd_admin_field=rd_admin_field,
            transit_subnets=transit_subnets,
            dhcp_config_id=dhcp_config_id,
            vrf_config=vrf_config,
            static_routes=static_routes,
            bfd_peers=bfd_peers,
            locale_services=locale_services,
        )

        log.info("Execution logs for updating tier 0 : {}".format(update_execution_logs))

        # update execution logs can come empty if there is nothing to update
        if (
            update_execution_logs
            and "error" in update_execution_logs[len(update_execution_logs) - 1]
        ):
            ret["result"] = False
            ret[
                "comment"
            ] = "Failed while creating tier0 gateway and sub-resources: {}\n Execution logs: {}".format(
                update_execution_logs[len(update_execution_logs) - 1]["error"],
                update_execution_logs,
            )
            return ret

        tier0_hierarchy_after_update = __salt__["nsxt_policy_tier0.get_hierarchy"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            tier0_id=tier_0_id,
        )
        if "error" in tier0_hierarchy_after_update:
            ret["result"] = False
            ret[
                "comment"
            ] = "Failure while querying tier0 gateway and its sub-resources: {}".format(
                tier0_hierarchy_after_update["error"]
            )
            return ret

        ret["comment"] = "Updated Tier-0 gateway {display_name} successfully".format(
            display_name=display_name
        )
        ret["changes"]["new"] = tier0_hierarchy_after_update
        ret["changes"]["old"] = tier0_hierarchy_before_update
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
    Deletes tier0 gateway with the given display_name and all its sub-resources

    CLI Example:

        .. code-block:: bash

            salt vm_minion nsxt_policy_tier0.absent hostname=nsxt-manager.local username=admin ...

        delete_tier0:
          nsxt_policy_tier0.absent:
            - name: <Name of the operation>
              hostname: <hostname>
              username: <username>
              password: <password>
              display_name: <display name of tier0 gateway>
              cert: <certificate>
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
            Display name of the tier0 gateway to delete

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
    tier_0_result = __salt__["nsxt_policy_tier0.get_by_display_name"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        display_name=display_name,
    )
    if "error" in tier_0_result:
        ret["result"] = False
        ret["comment"] = "Failed to get tier0 gateways from NSX-T Manager : {}".format(
            tier_0_result["error"]
        )
        return ret

    result_count = len(tier_0_result.get("results"))
    if result_count > 1:
        ret["result"] = False
        ret["comment"] = (
            "Found multiple results(result_count={count}) for tier0 gateway with "
            "display_name {display_name}".format(count=result_count, display_name=display_name)
        )
        return ret

    if __opts__["test"]:
        if result_count == 0:
            ret["result"] = None
            ret["comment"] = "No tier0 gateway with display_name: {} found in NSX-T Manager".format(
                display_name
            )
        else:
            ret["result"] = None
            ret["comment"] = "Tier0 gateway with display_name: {} will be deleted".format(
                display_name
            )
        return ret

    if result_count == 0:
        ret["comment"] = "No Tier0 gateway with display_name: {} found in NSX-T Manager".format(
            display_name
        )
        return ret
    else:
        tier0_to_delete = tier_0_result.get("results")[0]
        tier0_hierarchy = __salt__["nsxt_policy_tier0.get_hierarchy"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            tier0_id=tier0_to_delete["id"],
        )
        if "error" in tier0_hierarchy:
            ret["result"] = False
            ret[
                "comment"
            ] = "Failure while querying tier0 gateway and its sub-resources: {}".format(
                tier0_hierarchy["error"]
            )
            return ret

        delete_execution_logs = __salt__["nsxt_policy_tier0.delete"](
            hostname=hostname,
            username=username,
            password=password,
            tier0_id=tier0_to_delete["id"],
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
        )
        log.info("Execution logs for deleting tier 0 : {}".format(delete_execution_logs))
        if "error" in delete_execution_logs[len(delete_execution_logs) - 1]:
            ret["result"] = False
            ret["comment"] = "Failed to delete tier0 gateway : {}\n Execution logs: {}".format(
                delete_execution_logs[len(delete_execution_logs) - 1]["error"],
                delete_execution_logs,
            )
            return ret
        else:
            ret[
                "comment"
            ] = "Tier0 gateway with display_name: {} and its sub-resources deleted successfully".format(
                display_name
            )
            ret["changes"]["old"] = tier0_hierarchy
            ret["changes"]["new"] = {}
            return ret
