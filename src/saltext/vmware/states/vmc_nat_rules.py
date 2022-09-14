"""
VMC nat rules state module

Add new nat rule, update existing nat rule and delete existing nat rule from an SDDC.

Example usage :

.. code-block:: yaml

    ensure_nat_rule:
      vmc_nat_rules.present:
        - hostname: sample-nsx.vmwarevmc.com
        - refresh_key: 7jPSGSZpCa8e5Ouks4UY5cZyOtynAhF
        - authorization_host: console-stg.cloud.vmware.com
        - org_id: 10e1092f-51d0-473a-80f8-137652c39fd0
        - sddc_id: b43da080-2626-f64c-88e8-7f31d9d2c306
        - domain_id: mgw
        - nat_rule: vCenter_Inbound_Rule_2
        - verify_ssl: False
        - cert: /path/to/client/certificate
        - source_network: "203.0.113.73"
        - translated_network: "198.51.100.1"


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
    tier1,
    nat,
    nat_rule,
    verify_ssl=True,
    cert=None,
    action=None,
    destination_network=None,
    source_network=None,
    translated_network=None,
    translated_ports=vmc_constants.VMC_NONE,
    scope=None,
    service=None,
    enabled=None,
    firewall_match=None,
    logging=None,
    description=None,
    tags=vmc_constants.VMC_NONE,
    sequence_number=None,
    display_name=None,
):
    """
    Ensure a given nat rule exists for given SDDC

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the nat rules should be added

    domain_id
        The domain_id for which the nat rules should belongs to. Possible values: mgw, cgw

    nat_rule
        Id of the nat rule to be added to SDDC

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    action
        specify type of nat rule it can have value REFLEXIVE, DNAT

            REFLEXIVE nat rule require
                source_network
                translated_network
                service should be empty
                translated_ports  should be None

            DNAT  Rule require
                service
                destination_network
                translated_network
                translated_ports
                source_network can be None or input network.

    destination_network
        Represents the destination network
            This supports single IP address or comma separated list of single IP
            addresses or CIDR. This does not support IP range or IP sets.

    scope
        Array of policy paths of labels, ProviderInterface, NetworkInterface

    service
        Represents the service on which the NAT rule will be applied

    source_network
        Represents the source network address
            This supports single IP address or comma separated list of single IP
            addresses or CIDR. This does not support IP range or IP sets.

    translated_network
        Represents the translated network address

            This supports single IP address or comma separated list of single IP
            addresses or CIDR. This does not support IP range or IP sets.

    translated_ports
        Port number or port range

            Please note, if there is service configured in this NAT rule, the translated_port
            will be realized on NSX Manager as the destination_port. If there is no sevice configured,
            the port will be ignored.
    enabled
        (Optional) Policy nat rule enabled flag

            The flag, which suggests whether the NAT rule is enabled or
            disabled. The default is True.

    firewall_match
        (Optional) Represents the firewall match flag

            It indicates how the firewall matches the address after NATing if firewall
            stage is not skipped.
            possible values: MATCH_EXTERNAL_ADDRESS, MATCH_INTERNAL_ADDRESS
            Default: "MATCH_INTERNAL_ADDRESS"

    logging
        (Optional) Policy nat rule logging flag
            default: False

    description
        (Optional) Description of of nat rule

    tags
        (Optional) Opaque identifiers meaningful to the API user. Maximum 30 tags can be associated:

        .. code-block::

            tags:
              - tag: <tag-key-1>
                scope: <tag-value-1>
              - tag: <tag-key-2>
                scope: <tag-value-2>

    sequence_number
        (Optional) Sequence number of the nat rule
            The sequence_number decides the rule_priority of a NAT rule.
            default: 0
            type: int

    display_name
        Identifier to use when displaying entity in logs or GUI. This is applicable for only update scenario.
        For create scenario, display_name would be same as rule_id.

    Example Values:

        .. code-block::

            action: REFLEXIVE
            translated_network: 203.0.113.36
            translated_ports: null
            destination_network: ''
            source_network: 198.51.100.23
            sequence_number: 0
            service: ''
            logging: false
            enabled: false
            scope:
              - /infra/labels/cgw-public
            tags:
              - tag: tag1
                scope: scope1
            description: ''
            firewall_match: MATCH_INTERNAL_ADDRESS
    """

    input_dict = {
        "action": action,
        "description": description,
        "destination_network": destination_network,
        "scope": scope,
        "service": service,
        "source_network": source_network,
        "tags": tags,
        "translated_network": translated_network,
        "translated_ports": translated_ports,
        "enabled": enabled,
        "firewall_match": firewall_match,
        "logging": logging,
        "sequence_number": sequence_number,
        "display_name": display_name,
    }

    input_dict = {k: v for k, v in input_dict.items() if v != vmc_constants.VMC_NONE}

    get_nat_rule_response = __salt__["vmc_nat_rules.get_by_id"](
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        tier1=tier1,
        nat=nat,
        nat_rule=nat_rule,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in get_nat_rule_response:
        if "could not be found" in get_nat_rule_response["error"]:
            get_nat_rule_response = None
        else:
            return vmc_state._create_state_response(
                name=name, comment=get_nat_rule_response["error"], result=False
            )

    if __opts__.get("test"):
        log.info("present is called with test option")
        return vmc_state._create_state_response(
            name=name,
            comment="State present will {} nat rule {}".format(
                "update" if get_nat_rule_response else "create", nat_rule
            ),
        )

    if get_nat_rule_response:
        updatable_keys = input_dict.keys()
        is_update_required = vmc_state._check_for_updates(
            get_nat_rule_response, input_dict, updatable_keys, ["translated_ports", "tags"]
        )

        if is_update_required:
            updated_nat_rule = __salt__["vmc_nat_rules.update"](
                hostname=hostname,
                refresh_key=refresh_key,
                authorization_host=authorization_host,
                org_id=org_id,
                sddc_id=sddc_id,
                tier1=tier1,
                nat=nat,
                nat_rule=nat_rule,
                verify_ssl=verify_ssl,
                cert=cert,
                action=action,
                destination_network=destination_network,
                source_network=source_network,
                translated_network=translated_network,
                translated_ports=translated_ports,
                scope=scope,
                service=service,
                enabled=enabled,
                firewall_match=firewall_match,
                logging=logging,
                description=description,
                tags=tags,
                sequence_number=sequence_number,
                display_name=display_name,
            )

            if "error" in updated_nat_rule:
                return vmc_state._create_state_response(
                    name=name, comment=updated_nat_rule["error"], result=False
                )

            updated_nat_rule = __salt__["vmc_nat_rules.get_by_id"](
                hostname=hostname,
                refresh_key=refresh_key,
                authorization_host=authorization_host,
                org_id=org_id,
                sddc_id=sddc_id,
                tier1=tier1,
                nat=nat,
                nat_rule=nat_rule,
                verify_ssl=verify_ssl,
                cert=cert,
            )

            if "error" in updated_nat_rule:
                return vmc_state._create_state_response(
                    name=name, comment=updated_nat_rule["error"], result=False
                )

            return vmc_state._create_state_response(
                name=name,
                comment="Updated nat rule {}".format(nat_rule),
                old_state=get_nat_rule_response,
                new_state=updated_nat_rule,
                result=True,
            )
        else:
            log.info("All fields are same as existing nat rule %s", nat_rule)
            return vmc_state._create_state_response(
                name=name, comment="Nat rule exists already, no action to perform", result=True
            )
    else:
        log.info("No nat rule found with Id %s", nat_rule)
        created_nat_rule = __salt__["vmc_nat_rules.create"](
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            tier1=tier1,
            nat=nat,
            nat_rule=nat_rule,
            verify_ssl=verify_ssl,
            cert=cert,
            action=action,
            destination_network=destination_network,
            source_network=source_network,
            translated_network=translated_network,
            translated_ports=translated_ports,
            scope=scope,
            service=service,
            enabled=enabled,
            firewall_match=firewall_match,
            logging=logging,
            description=description,
            tags=tags,
            sequence_number=sequence_number,
        )

        if "error" in created_nat_rule:
            return vmc_state._create_state_response(
                name=name, comment=created_nat_rule["error"], result=False
            )

        return vmc_state._create_state_response(
            name=name,
            comment="Created nat rule {}".format(nat_rule),
            new_state=created_nat_rule,
            result=True,
        )


def absent(
    name,
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    tier1,
    nat,
    nat_rule,
    verify_ssl=True,
    cert=None,
):
    """
    Ensure a given nat rule does not exist on given SDDC

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC from which the nat rule should be deleted

    domain_id
        The domain_id for which the nat rules should belongs to. Possible values: mgw, cgw

    nat_rule
        Id of the nat rule to be deleted from SDDC

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Checking if nat rule with Id %s is present", nat_rule)
    get_nat_rule_response = __salt__["vmc_nat_rules.get_by_id"](
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        tier1=tier1,
        nat=nat,
        nat_rule=nat_rule,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in get_nat_rule_response:
        if "could not be found" in get_nat_rule_response["error"]:
            get_nat_rule_response = None
        else:
            return vmc_state._create_state_response(
                name=name, comment=get_nat_rule_response["error"], result=False
            )

    if __opts__.get("test"):
        log.info("absent is called with test option")
        if get_nat_rule_response:
            return vmc_state._create_state_response(
                name=name, comment="State absent will delete nat rule with Id {}".format(nat_rule)
            )
        else:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will do nothing as no nat rule found with Id {}".format(
                    nat_rule
                ),
            )

    if get_nat_rule_response:
        log.info("Security found with Id %s", nat_rule)
        deleted_nat_rule = __salt__["vmc_nat_rules.delete"](
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            tier1=tier1,
            nat=nat,
            nat_rule=nat_rule,
            verify_ssl=verify_ssl,
            cert=cert,
        )

        if "error" in deleted_nat_rule:
            return vmc_state._create_state_response(
                name=name, comment=deleted_nat_rule["error"], result=False
            )

        return vmc_state._create_state_response(
            name=name,
            comment="Deleted nat rule {}".format(nat_rule),
            old_state=get_nat_rule_response,
            result=True,
        )
    else:
        log.info("No nat rule found with Id %s", nat_rule)
        return vmc_state._create_state_response(
            name=name, comment="No nat rule found with Id {}".format(nat_rule), result=True
        )
