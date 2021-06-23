"""
VMC Security Rule state module

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
import logging

from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_state

log = logging.getLogger(__name__)
SECURITY_RULE_NOT_FOUND_ERROR = "could not be found"

try:
    from saltext.vmware.modules import vmc_security_rules

    HAS_SECURITY_RULES = True
except ImportError:
    HAS_SECURITY_RULES = False


def __virtual__():
    if not HAS_SECURITY_RULES:
        return False, "'vmc_security_rules' binary not found on system"
    return "vmc_security_rules"


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
    disabled=None,
    notes=None,
    sequence_number=None,
    tags=vmc_constants.VMC_NONE,
    display_name=None,
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

    disabled
        (Optional) Flag to disable the rule. Default is enabled.

    notes
        (Optional) Text for additional notes on changes.

    sequence_number
        (Optional) Sequence number of the Rule.
        This field is used to resolve conflicts between multiple Rules under Security or Gateway Policy for a Domain.
        If no sequence number is specified by the user, a value of 0 is assigned by default.
        If there are multiple rules with the same sequence number then their order is not deterministic.
        If a specific order of rules is desired, then one has to specify unique sequence numbers.

    tags
        (Optional) Opaque identifiers meaningful to the user.

        .. code::

            tags='[
                {
                    "tag": "<tag-key-1>"
                    "scope": "<tag-value-1>"
                },
                {
                    "tag": "<tag-key-2>"
                    "scope": "<tag-value-2>"
                }
            ]'

    display_name
        Identifier to use when displaying entity in logs or GUI. This is applicable for only update scenario.
        For create scenario, display_name would be same as rule_id.

    Example values:

        .. code::

            {
                "display_name": "vCenter Inbound Rule"
                "sequence_number": 0,
                "source_groups": [
                    "ANY"
                ],
                "services": ["/infra/services/HTTPS"],
                "logged": false,
                "disabled": false,
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
        "disabled": disabled,
        "notes": notes,
        "sequence_number": sequence_number,
        "tags": tags,
        "display_name": display_name,
    }

    input_dict = {k: v for k, v in input_dict.items() if v != vmc_constants.VMC_NONE}

    get_security_rule = __salt__["vmc_security_rules.get_by_id"](
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        rule_id=rule_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    existing_security_rule = None

    if "error" not in get_security_rule:
        log.info("Security rule found with Id %s", rule_id)
        existing_security_rule = get_security_rule
    elif SECURITY_RULE_NOT_FOUND_ERROR not in get_security_rule["error"]:
        return vmc_state._create_state_response(
            name=name, comment=get_security_rule["error"], result=False
        )

    if __opts__.get("test"):
        log.info("present is called with test option")
        if existing_security_rule:
            return vmc_state._create_state_response(
                name=name, comment="State present will update Security rule {}".format(rule_id)
            )
        else:
            return vmc_state._create_state_response(
                name=name, comment="State present will create Security rule {}".format(rule_id)
            )

    if existing_security_rule:
        updatable_keys = input_dict.keys()
        is_update_required = vmc_state._check_for_updates(
            existing_security_rule, input_dict, updatable_keys, ["tags"]
        )

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
                disabled=disabled,
                notes=notes,
                sequence_number=sequence_number,
                tags=tags,
                display_name=display_name,
            )

            if "error" in updated_security_rule:
                return vmc_state._create_state_response(
                    name=name, comment=updated_security_rule["error"], result=False
                )

            get_security_rule_after_update = __salt__["vmc_security_rules.get_by_id"](
                hostname=hostname,
                refresh_key=refresh_key,
                authorization_host=authorization_host,
                org_id=org_id,
                sddc_id=sddc_id,
                domain_id=domain_id,
                rule_id=rule_id,
                verify_ssl=verify_ssl,
                cert=cert,
            )

            if "error" in get_security_rule_after_update:
                return vmc_state._create_state_response(
                    name=name, comment=get_security_rule_after_update["error"], result=False
                )

            return vmc_state._create_state_response(
                name=name,
                comment="Updated Security rule {}".format(rule_id),
                old_state=existing_security_rule,
                new_state=get_security_rule_after_update,
                result=True,
            )
        else:
            log.info("All fields are same as existing Security rule %s", rule_id)
            return vmc_state._create_state_response(
                name=name, comment="Security rule exists already, no action to perform", result=True
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
            disabled=disabled,
            notes=notes,
            sequence_number=sequence_number,
            tags=tags,
        )

        if "error" in created_security_rule:
            return vmc_state._create_state_response(
                name=name, comment=created_security_rule["error"], result=False
            )

        return vmc_state._create_state_response(
            name=name,
            comment="Created Security rule {}".format(rule_id),
            new_state=created_security_rule,
            result=True,
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
    cert=None,
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
        cert=cert,
    )

    existing_security_rule = None

    if "error" not in get_security_rule:
        log.info("Security rule found with Id %s", rule_id)
        existing_security_rule = get_security_rule
    elif SECURITY_RULE_NOT_FOUND_ERROR not in get_security_rule["error"]:
        return vmc_state._create_state_response(
            name=name, comment=get_security_rule["error"], result=False
        )

    if __opts__.get("test"):
        log.info("absent is called with test option")
        if existing_security_rule:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will delete Security rule with Id {}".format(rule_id),
            )
        else:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will do nothing as no Security rule found with Id {}".format(
                    rule_id
                ),
            )

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
            cert=cert,
        )

        if "error" in deleted_security_rule:
            return vmc_state._create_state_response(
                name=name, comment=deleted_security_rule["error"], result=False
            )

        return vmc_state._create_state_response(
            name=name,
            comment="Deleted Security rule {}".format(rule_id),
            old_state=existing_security_rule,
            result=True,
        )
    else:
        log.info("No Security rule found with Id %s", rule_id)
        return vmc_state._create_state_response(
            name=name, comment="No Security rule found with Id {}".format(rule_id), result=True
        )
