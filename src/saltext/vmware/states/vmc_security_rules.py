"""
VMC Security Rule state module
================================================

:maintainer: <VMware>
:maturity: new

Add new security rule, update existing security rule and delete existing security rule from an SDDC.

Example usage :

.. code-block:: yaml
    ensure_security_rule:
      vmc_security_rules.present:
        - hostname: sample-nsx.vmwarevmc.com
        - refresh_key: 7jPSGSZpCa8e5Ouks4UY5cZyOtynAhF
        - authorization_host: console-stg.cloud.vmware.com
        - org_id: 10e1092f-51d0-473a-80f8-137652c39fd0
        - sddc_id: b43da080-2626-f64c-88e8-7f31d9d2c306
        - domain_id: mgw
        - rule_id: vCenter_Inbound_Rule_2
        - verify_ssl: False
        - cert: /path/to/client/certificate

.. warning::

    It is recommended to pass the VMC authentication details using Pillars rather than specifying as plain text in SLS
    files.


"""

# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals
from saltext.vmware.utils import vmc_state, vmc_constants
import logging

log = logging.getLogger(__name__)
SECURITY_RULE_NOT_FOUND_ERROR = "could not be found"


def __virtual__():
    """
    Only load if the vmc_security_rules module is available in __salt__
    """
    return (
        "vmc_security_rules" if "vmc_security_rules.get" in __salt__ else False,
        "'vmc_security_rules' binary not found on system",
    )


def present(
    name,
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    domain_id,
    rule_id,
    verify_ssl=True,
    cert=None,
    source_groups=None,
    destination_groups=None,
    services=None,
    scope=None,
    action=None,
    tag=None,
    logged=None,
    notes=None,
    sequence_number=None,
    tags=vmc_constants.VMC_NONE,
    display_name=None
):
    """
        Ensure a given security rule exists for given SDDC

        hostname
            The host name of NSX-T manager

        refresh_key
            API Token of the user which is used to get the Access Token required for VMC operations

        authorization_host
            Hostname of the VMC cloud console

        org_id
            The Id of organization to which the SDDC belongs to

        sddc_id
            The Id of SDDC for which the security rules should be added

        domain_id
            The domain_id for which the security rule should belong to. Possible values: mgw, cgw

        rule_id
            Id of the security_rule to be added to SDDC

        verify_ssl
            (Optional) Option to enable/disable SSL verification. Enabled by default.
            If set to False, the certificate validation is skipped.

        cert
            (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
            The certificate can be retrieved from browser.

        source_groups
            (Optional) List of Source group paths.
            We need paths as duplicate names may exist for groups under different domains.
            Along with paths we support IP Address of type IPv4 and IPv6.
            IP Address can be in one of the format(CIDR, IP Address, Range of IP Address).
            In order to specify all groups, use the constant "ANY". This is case insensitive.
            If "ANY" is used, it should be the ONLY element in the group array.
            Error will be thrown if ANY is used in conjunction with other values.
            If this value is not passed, then ["ANY"] will be used by default.

        destination_groups
            (Optional) List of Destination group paths.
            We need paths as duplicate names may exist for groups under different domains.
            Along with paths we support IP Address of type IPv4 and IPv6.
            IP Address can be in one of the format(CIDR, IP Address, Range of IP Address).
            In order to specify all groups, use the constant "ANY". This is case insensitive.
            If "ANY" is used, it should be the ONLY element in the group array.
            Error will be thrown if ANY is used in conjunction with other values.
            If this value is not passed, then ["ANY"] will be used by default.

        Note: Both source_groups and destination_groups can not be ["ANY"] when domain_id=mgw

        services
            (Optional) Names of services. In order to specify all services, use the constant "ANY".
            This is case insensitive. If "ANY" is used, it should be the ONLY element in the services array.
            Error will be thrown if ANY is used in conjunction with other values.
            If this value is not passed, then ["ANY"] will be used by default.

        scope
            (Optional) The list of policy paths where the rule is applied LR/Edge/T0/T1/LRP etc.
            Note that a given rule can be applied on multiple LRs/LRPs.

        action
            (Optional) The action to be applied to all the services.
            Possible Values for domain_id=cgw are: ALLOW, DROP, REJECT
            Possible Values for domain_id=mgw are: ALLOW

        tag
            (Optional) Tag applied on the rule. User level field which will be printed in CLI and packet logs.

        logged
            (Optional) Enable logging flag. Flag to enable packet logging. Default is disabled.

        notes
            (Optional) Text for additional notes on changes.

        sequence_number
            (Optional) Sequence number of the Rule.
            This field is used to resolve conflicts between multiple Rules under Security or Gateway Policy for a Domain
            If no sequence number is specified by the user, a value of 0 is assigned by default.
            If there are multiple rules with the same sequence number then their order is not deterministic.
            If a specific order of rules is desired, then one has to specify unique sequence numbers.

        tags
            (Optional) Opaque identifiers meaningful to the user.
            Array of tag where tag is of the format:
            {
                "tag": <tag>,
                "scope": <scope>
            }

        display_name
            Identifier to use when displaying entity in logs or GUI. This is applicable for only update scenario.
            For create scenario, display_name would be same as rule_id.

        Example values:
            {
                "display_name": "vCenter Inbound Rule"
                "sequence_number": 0,
                "source_groups": [
                    "ANY"
                ],
                "services": ["/infra/services/HTTPS"],
                "logged": false,
                "destination_groups": [
                    "/infra/domains/mgw/groups/VCENTER"
                ],
                "scope": [
                    "/infra/tier-1s/mgw"
                ],
                "action": "ALLOW",
                "tag": "",
                "notes": "",
                "tags": null
            }

    """

    input_dict = {
        "source_groups": source_groups,
        "destination_groups": destination_groups,
        "services": services,
        "scope": scope,
        "action": action,
        "tag": tag,
        "logged": logged,
        "notes": notes,
        "sequence_number": sequence_number,
        "tags": tags,
        "display_name": display_name
    }

    get_security_rule = __salt__["vmc_security_rules.get_by_id"](
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        rule_id=rule_id,
        verify_ssl=verify_ssl,
        cert=cert
    )

    existing_security_rule = None

    if "error" in get_security_rule and SECURITY_RULE_NOT_FOUND_ERROR not in get_security_rule["error"]:
        return vmc_state._create_state_response(name, None, None, False, get_security_rule["error"])
    elif "error" not in get_security_rule:
        log.info("Security rule found with Id %s", rule_id)
        existing_security_rule = get_security_rule

    if __opts__.get("test"):
        log.info("present is called with test option")
        if existing_security_rule:
            return vmc_state._create_state_response(name, None, None, None,
                                                    "State present will update Security rule {}".format(rule_id))
        else:
            return vmc_state._create_state_response(name, None, None, None,
                                                    "State present will create Security rule {}".format(rule_id))

    if existing_security_rule:
        updatable_keys = input_dict.keys()
        is_update_required = vmc_state._check_for_updates(existing_security_rule, input_dict, updatable_keys, ["tags"])

        if is_update_required:
            updated_security_rule = __salt__["vmc_security_rules.update"](
                hostname=hostname,
                refresh_key=refresh_key,
                authorization_host=authorization_host,
                org_id=org_id,
                sddc_id=sddc_id,
                domain_id=domain_id,
                rule_id=rule_id,
                verify_ssl=verify_ssl,
                cert=cert,
                source_groups=source_groups,
                destination_groups=destination_groups,
                services=services,
                scope=scope,
                action=action,
                tag=tag,
                logged=logged,
                notes=notes,
                sequence_number=sequence_number,
                tags=tags,
                display_name=display_name
            )

            if "error" in updated_security_rule:
                return vmc_state._create_state_response(name, None, None, False, updated_security_rule["error"])

            get_security_rule_after_update = __salt__["vmc_security_rules.get_by_id"](
                hostname=hostname,
                refresh_key=refresh_key,
                authorization_host=authorization_host,
                org_id=org_id,
                sddc_id=sddc_id,
                domain_id=domain_id,
                rule_id=rule_id,
                verify_ssl=verify_ssl,
                cert=cert
            )

            if "error" in get_security_rule_after_update:
                return vmc_state._create_state_response(name, None, None, False,
                                                        get_security_rule_after_update["error"])

            return vmc_state._create_state_response(name, existing_security_rule, get_security_rule_after_update,
                                                    True, "Updated Security rule {}".format(rule_id))
        else:
            log.info("All fields are same as existing Security rule %s", rule_id)
            return vmc_state._create_state_response(
                name, None, None, True, "Security rule exists already, no action to perform"
            )
    else:
        log.info("No Security rule found with Id %s", rule_id)
        created_security_rule = __salt__["vmc_security_rules.create"](
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            domain_id=domain_id,
            rule_id=rule_id,
            verify_ssl=verify_ssl,
            cert=cert,
            source_groups=source_groups,
            destination_groups=destination_groups,
            services=services,
            scope=scope,
            action=action,
            tag=tag,
            logged=logged,
            notes=notes,
            sequence_number=sequence_number,
            tags=tags
        )

        if "error" in created_security_rule:
            return vmc_state._create_state_response(name, None, None, False, created_security_rule["error"])

        return vmc_state._create_state_response(
            name, None, created_security_rule, True, "Created Security rule {}".format(rule_id)
        )


def absent(
    name,
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    domain_id,
    rule_id,
    verify_ssl=True,
    cert=None
):
    """
        Ensure a given security rule does not exist on given SDDC

        hostname
            The host name of NSX-T manager

        refresh_key
            API Token of the user which is used to get the Access Token required for VMC operations

        authorization_host
            Hostname of the VMC cloud console

        org_id
            The Id of organization to which the SDDC belongs to

        sddc_id
            The Id of SDDC from which the security rule should be deleted

        domain_id
            The domain_id for which the security rule should belong to. Possible values: mgw, cgw

        rule_id
            Id of the security_rule to be deleted from SDDC

        verify_ssl
            (Optional) Option to enable/disable SSL verification. Enabled by default.
            If set to False, the certificate validation is skipped.

        cert
            (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
            The certificate can be retrieved from browser.

    """

    log.info("Checking if Security rule with Id %s is present", rule_id)
    get_security_rule = __salt__["vmc_security_rules.get_by_id"](
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        rule_id=rule_id,
        verify_ssl=verify_ssl,
        cert=cert
    )

    existing_security_rule = None

    if "error" in get_security_rule and SECURITY_RULE_NOT_FOUND_ERROR not in get_security_rule["error"]:
        return vmc_state._create_state_response(name, None, None, False, get_security_rule["error"])
    elif "error" not in get_security_rule:
        log.info("Security rule found with Id %s", rule_id)
        existing_security_rule = get_security_rule

    if __opts__.get("test"):
        log.info("absent is called with test option")
        if existing_security_rule:
            return vmc_state._create_state_response(name, None, None, None,
                                                    "State absent will delete Security rule with Id {}".format(rule_id))
        else:
            return vmc_state._create_state_response(name, None, None, None,
                                                    "State absent will do nothing as no Security rule found with Id {}"
                                                    .format(rule_id))

    if existing_security_rule:
        log.info("Security rule found with Id %s", rule_id)
        deleted_security_rule = __salt__["vmc_security_rules.delete"](
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            domain_id=domain_id,
            rule_id=rule_id,
            verify_ssl=verify_ssl,
            cert=cert
        )

        if "error" in deleted_security_rule:
            return vmc_state._create_state_response(name, None, None, False, deleted_security_rule["error"])

        return vmc_state._create_state_response(
            name, existing_security_rule, None, True, "Deleted Security rule {}".format(rule_id)
        )
    else:
        log.info("No Security rule found with Id %s", rule_id)
        return vmc_state._create_state_response(
            name, None, None, True, "No Security rule found with Id {}".format(rule_id)
        )
