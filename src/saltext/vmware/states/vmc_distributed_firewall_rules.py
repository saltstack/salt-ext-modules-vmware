"""
VMC Distributed Firewall Rule state module

Add new distributed firewall rule, update existing distributed firewall rule and
     delete existing distributed firewall rule from an SDDC.

Example usage :

.. code-block:: yaml

    Distributed_Firewall_Rule_1:
      vmc_distributed_firewall_rules.present:
        - hostname: sample-nsx.vmwarevmc.com
        - refresh_key: 7jPSGSZpCa8e5Ouks4UY5cZyOtynAhF
        - authorization_host: console-stg.cloud.vmware.com
        - org_id: 10e1092f-51d0-473a-80f8-137652c39fd0
        - sddc_id: b43da080-2626-f64c-88e8-7f31d9d2c306
        - domain_id: default
        - security_policy_id: default-layer3-section
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


def present(
    name,
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    domain_id,
    security_policy_id,
    verify_ssl=True,
    cert=None,
    source_groups=None,
    destination_groups=None,
    services=None,
    scope=None,
    action=None,
    sequence_number=None,
    display_name=None,
    disabled=None,
    logged=None,
    description=None,
    direction=None,
    notes=None,
    tag=None,
    tags=vmc_constants.VMC_NONE,
):
    """
    Ensure a given distributed firewall rule exists for given SDDC

    name
        Indicates the distributed firewall rule id, any unique string identifying the  distributed firewall rule.
        Also same as the display_name by default.

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the distributed firewall rules should be added

    domain_id
        The domain_id for which the Distributed firewall rule belongs to. Possible values: default, cgw

    security_policy_id
        The  security_policy_id for which the distributed firewall rules should belongs to

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
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
        Possible Values for are: ALLOW, DROP, REJECT

    display_name
        Identifier to use when displaying entity in logs or GUI
            Defaults to ID if not set

    sequence_number
        (Optional) Sequence number of the Rule.
        This field is used to resolve conflicts between multiple Rules under Security or Gateway Policy for a Domain.
        If no sequence number is specified by the user, a value of 0 is assigned by default.
        If there are multiple rules with the same sequence number then their order is not deterministic.
        If a specific order of rules is desired, then one has to specify unique sequence numbers.

    Disabled
        (Optional) Flag to disable the rule. Default is false.

    logged
        (Optional) Enable logging flag. Flag to enable packet logging. Default is disabled.

    description
        (Optional) Description of this resource

    direction
        (Optional) Define direction of traffic
        Possible Values for are: IN, OUT, IN_OUT
        Default: "IN_OUT"

    notes
        (Optional) Text for additional notes on changes.

    tag
        (Optional) Tag applied on the rule. User level field which will be printed in CLI and packet logs.

    tags
        (Optional) Opaque identifiers meaningful to the user.

        .. code-block::

            {
                "tag": <tag>,
                "scope": <scope>
            }

    Example values:

        .. code-block::

           {
              "description": "comm entry",
              "display_name": "",
              "sequence_number": 1,
              "source_groups": [
                "ANY"
              ],
              "logged": false,
              "destination_groups": [
                "ANY"
              ],
              "scope": [
                "ANY"
              ],
              "action": "DROP",
              "services": [
                "ANY"
              ],
              "direction": "IN_OUT",
              "tag": "",
              "notes": ""
            }

    """

    rule_id = name
    input_dict = {
        "source_groups": source_groups,
        "destination_groups": destination_groups,
        "services": services,
        "scope": scope,
        "action": action,
        "display_name": display_name,
        "sequence_number": sequence_number,
        "disabled": disabled,
        "logged": logged,
        "description": description,
        "direction": direction,
        "notes": notes,
        "tag": tag,
        "tags": tags,
    }

    input_dict = {k: v for k, v in input_dict.items() if v != vmc_constants.VMC_NONE}

    distributed_firewall_rule = __salt__["vmc_distributed_firewall_rules.get_by_id"](
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_policy_id=security_policy_id,
        rule_id=rule_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in distributed_firewall_rule:
        if "could not be found" in distributed_firewall_rule["error"]:
            distributed_firewall_rule = None
        else:
            return vmc_state._create_state_response(
                name=name, comment=distributed_firewall_rule["error"], result=False
            )

    if __opts__.get("test"):
        log.info("present is called with test option")
        return vmc_state._create_state_response(
            name=name,
            comment="Distributed firewall rule {} would have been {}".format(
                rule_id, "updated" if distributed_firewall_rule else "created"
            ),
        )

    if distributed_firewall_rule:
        updatable_keys = input_dict.keys()
        is_update_required = vmc_state._check_for_updates(
            distributed_firewall_rule, input_dict, updatable_keys, ["tags"]
        )

        if is_update_required:
            updated_distributed_firewall_rule = __salt__["vmc_distributed_firewall_rules.update"](
                hostname=hostname,
                refresh_key=refresh_key,
                authorization_host=authorization_host,
                org_id=org_id,
                sddc_id=sddc_id,
                domain_id=domain_id,
                security_policy_id=security_policy_id,
                rule_id=rule_id,
                verify_ssl=verify_ssl,
                cert=cert,
                source_groups=source_groups,
                destination_groups=destination_groups,
                services=services,
                scope=scope,
                action=action,
                display_name=display_name,
                sequence_number=sequence_number,
                disabled=disabled,
                logged=logged,
                description=description,
                direction=direction,
                notes=notes,
                tag=tag,
                tags=tags,
            )

            if "error" in updated_distributed_firewall_rule:
                return vmc_state._create_state_response(
                    name=name, comment=updated_distributed_firewall_rule["error"], result=False
                )

            updated_distributed_firewall_rule = __salt__[
                "vmc_distributed_firewall_rules.get_by_id"
            ](
                hostname=hostname,
                refresh_key=refresh_key,
                authorization_host=authorization_host,
                org_id=org_id,
                sddc_id=sddc_id,
                domain_id=domain_id,
                security_policy_id=security_policy_id,
                rule_id=rule_id,
                verify_ssl=verify_ssl,
                cert=cert,
            )

            if "error" in updated_distributed_firewall_rule:
                return vmc_state._create_state_response(
                    name=name,
                    comment=updated_distributed_firewall_rule["error"],
                    result=False,
                )

            return vmc_state._create_state_response(
                name=name,
                comment="Updated distributed firewall rule {}".format(rule_id),
                old_state=distributed_firewall_rule,
                new_state=updated_distributed_firewall_rule,
                result=True,
            )
        else:
            log.info("All fields are same as existing distributed firewall rule %s", rule_id)
            return vmc_state._create_state_response(
                name=name,
                comment="Distributed firewall rule exists already, no action to perform",
                result=True,
            )
    else:
        log.info("No distributed firewall rule found with ID %s", rule_id)
        created_distributed_firewall_rule = __salt__["vmc_distributed_firewall_rules.create"](
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            domain_id=domain_id,
            security_policy_id=security_policy_id,
            rule_id=rule_id,
            verify_ssl=verify_ssl,
            cert=cert,
            source_groups=source_groups,
            destination_groups=destination_groups,
            services=services,
            scope=scope,
            action=action,
            sequence_number=sequence_number,
            disabled=disabled,
            logged=logged,
            description=description,
            direction=direction,
            notes=notes,
            tag=tag,
            tags=tags,
        )

        if "error" in created_distributed_firewall_rule:
            return vmc_state._create_state_response(
                name=name, comment=created_distributed_firewall_rule["error"], result=False
            )

        return vmc_state._create_state_response(
            name=name,
            comment="Created distributed firewall rule {}".format(rule_id),
            new_state=created_distributed_firewall_rule,
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
    security_policy_id,
    verify_ssl=True,
    cert=None,
):
    """
    Ensure a given distributed firewall rule does not exist on given SDDC

    name
        Indicates the distributed firewall rule id, any unique string identifying the distributed firewall rule.

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC from which the distributed firewall rule should be deleted

    domain_id
        The domain_id for which the Distributed firewall rule belongs to. Possible values: default, cgw

    security_policy_id
        The  security_policy_id for which the distributed firewall rules belongs to

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    rule_id = name
    log.info("Checking if distributed firewall rule with ID %s is present", rule_id)
    distributed_firewall_rule = __salt__["vmc_distributed_firewall_rules.get_by_id"](
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        security_policy_id=security_policy_id,
        domain_id=domain_id,
        rule_id=rule_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in distributed_firewall_rule:
        if "could not be found" in distributed_firewall_rule["error"]:
            distributed_firewall_rule = None
        else:
            return vmc_state._create_state_response(
                name=name, comment=distributed_firewall_rule["error"], result=False
            )

    if __opts__.get("test"):
        log.info("absent is called with test option")
        if distributed_firewall_rule:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will delete distributed firewall rule with ID {}".format(
                    rule_id
                ),
            )
        else:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will do nothing as no distributed firewall rule found with ID {}".format(
                    rule_id
                ),
            )

    if distributed_firewall_rule:
        log.info("Distributed firewall rule found with ID %s", rule_id)
        deleted_distributed_firewall_rule = __salt__["vmc_distributed_firewall_rules.delete"](
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            domain_id=domain_id,
            security_policy_id=security_policy_id,
            rule_id=rule_id,
            verify_ssl=verify_ssl,
            cert=cert,
        )

        if "error" in deleted_distributed_firewall_rule:
            return vmc_state._create_state_response(
                name=name, comment=deleted_distributed_firewall_rule["error"], result=False
            )

        return vmc_state._create_state_response(
            name=name,
            comment="Deleted distributed firewall rule {}".format(rule_id),
            old_state=distributed_firewall_rule,
            result=True,
        )
    else:
        log.info("No distributed firewall rule found with ID %s", rule_id)
        return vmc_state._create_state_response(
            name=name,
            comment="No distributed firewall rule found with ID {}".format(rule_id),
            result=True,
        )
