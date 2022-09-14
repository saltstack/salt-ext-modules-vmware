"""
Salt execution module for nat rules
Provides methods to Create, Update, Read and Delete nat rules.
"""
import logging
import os

from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request
from saltext.vmware.utils import vmc_templates

log = logging.getLogger(__name__)

__virtualname__ = "vmc_nat_rules"


def __virtual__():
    return __virtualname__


def _create_payload_for_nat_rule(rule_id, user_input):
    """
    This function creates the payload based on the template and user input passed
    """
    data = vmc_request.create_payload_for_request(vmc_templates.create_nat_rules, user_input)
    data["id"] = data["display_name"] = rule_id
    return data


def get(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    tier1,
    nat,
    verify_ssl=True,
    cert=None,
    cursor=None,
    page_size=None,
    sort_by=None,
    sort_ascending=None,
):
    """
    Retrieves nat rules for Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_nat_rules.get hostname=nsxt-manager.local domain_id=mgw ...


    hostname
        The host name of NSX-T manager

    refresh_key
        refresh_key to get access token

    authorization_host
        hostname to get access token

    org_id
        org_id of the SDDC

    sddc_id
        sddc_id for which nat rules should be retrieved

    tier1
        tier1 option are cgw and user defined tier1

    nat
        nat option are USER

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cursor
        (Optional) Opaque cursor to be used for getting next page of records (supplied by current result page)

    page_size
        (Optional) Maximum number of results to return in this page. Default page size is 1000.

    sort_by
        (Optional) Field by which records are sorted

    sort_ascending
        (Optional) Boolean value to sort result in ascending order. Enabled by default.

    """

    log.info("Retrieving nat rules for SDDC %s", sddc_id)

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/tier-1s/{tier1}/nat/{nat}/nat-rules"
    )
    api_url = api_url.format(
        base_url=api_url_base, org_id=org_id, sddc_id=sddc_id, tier1=tier1, nat=nat
    )

    params = vmc_request._filter_kwargs(
        allowed_kwargs=["cursor", "page_size", "sort_ascending", "sort_by"],
        cursor=cursor,
        page_size=page_size,
        sort_by=sort_by,
        sort_ascending=sort_ascending,
    )

    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_nat_rule.get",
        verify_ssl=verify_ssl,
        cert=cert,
        params=params,
    )


def get_by_id(
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
    Retrieves specific nat rule for Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_nat_rules.get_by_id hostname=nsxt-manager.local tier1=cgw ...

    hostname
        The host name of NSX-T manager

    refresh_key
        refresh_key to get access token

    authorization_host
        hostname to get access token

    org_id
        org_id of the SDDC

    sddc_id
        sddc_id for which nat rules should be retrieved

    tier1
        tier1 option are cgw and user defined tier1

    nat
        nat option are USER/default/Internal

    nat_rule
        id of specific nat rule

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.
    """
    log.info("Retrieving nat rule %s for SDDC %s", nat_rule, sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/tier-1s/{tier1}/nat/{nat}/nat-rules/{nat_rule}"
    )
    api_url = api_url.format(
        base_url=api_url_base,
        org_id=org_id,
        sddc_id=sddc_id,
        tier1=tier1,
        nat=nat,
        nat_rule=nat_rule,
    )

    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_nat_rule.get_by_id",
        verify_ssl=verify_ssl,
        cert=cert,
    )


def delete(
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
    Delete nat rules for Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_nat_rules.delete hostname=nsxt-manager.local tier1=cgw ...

    hostname
        The host name of NSX-T manager

    refresh_key
        refresh_key to get access token

    authorization_host
        hostname to get access token

    org_id
        org_id of the SDDC

    sddc_id
        sddc_id for which nat rules should be deleted

    tier1
        tier1 option are cgw and user defined tier1

    nat
        nat option are USER/default/Internal

    nat_rule
        id of specific nat rule

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    """
    log.info("Deleting nat rule %s for SDDC %s", nat_rule, sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/tier-1s/{tier1}/nat/{nat}/nat-rules/{nat_rule}"
    )
    api_url = api_url.format(
        base_url=api_url_base,
        org_id=org_id,
        sddc_id=sddc_id,
        tier1=tier1,
        nat=nat,
        nat_rule=nat_rule,
    )
    return vmc_request.call_api(
        method=vmc_constants.DELETE_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_nat_rule.delete",
        responsebody_applicable=False,
        verify_ssl=verify_ssl,
        cert=cert,
    )


def create(
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
):
    """
    Create nat rules for Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_nat_rules.create hostname=nsxt-manager.local tier1=cgw ...

    hostname
        The host name of NSX-T manager

    refresh_key
        refresh_key to get access token

    authorization_host
        hostname to get access token

    org_id
        org_id of the SDDC

    sddc_id
        sddc_id for which nat rules should be created

    tier1
        tier1 option are cgw and user defined tier1

    nat
        nat option are USER/default/Internal

    nat_rule
        id of specific nat rule

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    action
        specify type of nat rule it can have value REFLEXIVE, DNAT

            REFLEXIVE nat rule require
                source_network
                translated_network
                service should be empty
                translated_ports  should be None
                destination_network should be none

            DNAT  Rule require
                destination_network
                translated_network
                translated_ports can be none
                service can be none
                source_network can be None or input network.

    destination_network
        Represents the destination network
            This supports single IP address or comma separated list of single IP
            addresses or CIDR. This does not support IP range or IP sets.

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

            Please note, if there is service configured in this nat rule, the translated_port
            will be realized on NSX Manager as the destination_port. If there is no sevice configured,
            the port will be ignored.

    scope
        (Optional) Array of policy paths of labels, ProviderInterface, NetworkInterface
        If this value is not passed, then ["/infra/labels/cgw-public"] will be used by default.

    service
        (Optional) Represents the service on which the nat rule will be applied
        If this value is not passed, then empty string will be used by default.

    enabled
        (Optional) Policy nat rule enabled flag

            The flag, which suggests whether the nat rule is enabled or
            disabled. The default is True.

    firewall_match
        (Optional) Represents the firewall match flag

            It indicates how the firewall matches the address after nating if firewall
            stage is not skipped.
            possible values: MATCH_EXTERNAL_ADDRESS, MATCH_INTERNAL_ADDRESS
            Default: "MATCH_INTERNAL_ADDRESS"

    logging
        (Optional) Policy nat rule logging flag
            default: False

    description
        (Optional) Description of nat rule

    tags
        (Optional) Opaque identifiers meaningful to the API user. Maximum 30 tags can be associated:

        .. code-block::

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


    sequence_number
        (Optional) Sequence number of the nat rule
            The sequence_number decides the rule_priority of a nat rule.
            default: 0
            type: int

    Example values:

        .. code-block::

            {
                "action": "REFLEXIVE",
                "translated_network": "203.0.113.36",
                "translated_ports": null,
                "destination_network": "",
                "source_network": "198.51.100.23",
                "sequence_number": 0,
                "service": "",
                "logging": false,
                "enabled": false,
                "scope": [
                    "/infra/labels/cgw-public"
                ],
                "tags": [
                    {
                        "tag": "tag1",
                        "scope": "scope1"
                    }
                ],
                "description": "",
                "firewall_match": "MATCH_INTERNAL_ADDRESS"
            }

    Please refer the `Nat Rule <https://developer.vmware.com/docs/nsx-vmc-policy/latest/data-structures/InlinePolicyNatRule1/>`_ to get insight of input parameters.

    """
    log.info("Creating nat rule %s for SDDC %s ", nat_rule, sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/tier-1s/{tier1}/nat/{nat}/nat-rules/{nat_rule}"
    )
    api_url = api_url.format(
        base_url=api_url_base,
        org_id=org_id,
        sddc_id=sddc_id,
        tier1=tier1,
        nat=nat,
        nat_rule=nat_rule,
    )

    allowed_dict = {
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
    }
    req_data = vmc_request._filter_kwargs(
        allowed_kwargs=allowed_dict.keys(), allow_none=["translated_ports", "tags"], **allowed_dict
    )

    data = _create_payload_for_nat_rule(nat_rule, req_data)

    return vmc_request.call_api(
        method=vmc_constants.PUT_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_nat_rule.create",
        data=data,
        verify_ssl=verify_ssl,
        cert=cert,
    )


def update(
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
    Update nat rule for Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_nat_rules.update hostname=nsxt-manager.local tier1=cgw ...


    hostname
        The host name of NSX-T manager

    refresh_key
        refresh_key to get access token

    authorization_host
        hostname to get access token

    org_id
        org_id of the SDDC

    sddc_id
        sddc_id for which nat rules should be updated

    tier1
        tier1 option are cgw and user defined tier1

    nat
        nat option are USER/default/Internal

    nat_rule
        id of specific nat rule

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    action
        specify type of nat rule it can have value REFLEXIVE, DNAT

            REFLEXIVE nat rule require
                source_network
                translated_network
                service should be empty
                translated_ports  should be None
                destination_network should be none

            DNAT  Rule require
                destination_network
                translated_network
                translated_ports can be none
                service can be none
                source_network can be None or input network.

    destination_network
        Represents the destination network
            This supports single IP address or comma separated list of single IP
            addresses or CIDR. This does not support IP range or IP sets.

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

            Please note, if there is service configured in this nat rule, the translated_port
            will be realized on NSX Manager as the destination_port. If there is no sevice configured,
            the port will be ignored.

    scope
        (Optional) Array of policy paths of labels, ProviderInterface, NetworkInterface
        If this value is not passed, then ["/infra/labels/cgw-public"] will be used by default.

    service
        (Optional) Represents the service on which the nat rule will be applied
        If this value is not passed, then empty string will be used by default.

    enabled
        (Optional) Policy nat rule enabled flag

            The flag, which suggests whether the nat rule is enabled or
            disabled. The default is True.

    firewall_match
        (Optional) Represents the firewall match flag

            It indicates how the firewall matches the address after nating if firewall
            stage is not skipped.
            possible values: MATCH_EXTERNAL_ADDRESS, MATCH_INTERNAL_ADDRESS
            Default: "MATCH_INTERNAL_ADDRESS"

    logging
        (Optional) Policy nat rule logging flag
            default: False

    description
        (Optional) Description of nat rule

    tags
        (Optional) Opaque identifiers meaningful to the API user. Maximum 30 tags can be associated:

        .. code-block::

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

    sequence_number
        (Optional) Sequence number of the Nat Rule
            The sequence_number decides the rule_priority of a nat rule.
            default: 0
            type: int

    display_name
        Identifier to use when displaying entity in logs or GUI

    Example values:

        .. code-block::

            {
                "action": "REFLEXIVE",
                "translated_network": "203.0.113.36",
                "translated_ports": null,
                "destination_network": "",
                "source_network": "198.51.100.23",
                "sequence_number": 0,
                "service": "",
                "logging": false,
                "enabled": false,
                "scope": [
                    "/infra/labels/cgw-public"
                ],
                "tags": [
                    {
                        "tag": "tag1",
                        "scope": "scope1"
                    }
                ],
                "description": "",
                "firewall_match": "MATCH_INTERNAL_ADDRESS"
            }

    Please refer the `Nat Rule <https://developer.vmware.com/docs/nsx-vmc-policy/latest/data-structures/InlinePolicyNatRule1/>`_ to get insight of input parameters

    """
    log.info("Updating Nat rule %s for SDDC %s ", nat_rule, sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/tier-1s/{tier1}/nat/{nat}/nat-rules/{nat_rule}"
    )
    api_url = api_url.format(
        base_url=api_url_base,
        org_id=org_id,
        sddc_id=sddc_id,
        tier1=tier1,
        nat=nat,
        nat_rule=nat_rule,
    )

    # fetch the nat rule for the given nat_rule
    existing_data = get_by_id(
        hostname,
        refresh_key,
        authorization_host,
        org_id,
        sddc_id,
        tier1,
        nat,
        nat_rule,
        verify_ssl,
        cert,
    )

    if vmc_constants.ERROR in existing_data:
        return existing_data

    allowed_dict = {
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

    req_data = vmc_request._filter_kwargs(
        allowed_kwargs=allowed_dict.keys(), allow_none=["translated_ports", "tags"], **allowed_dict
    )

    payload = vmc_request.create_payload_for_request(
        vmc_templates.update_nat_rules, req_data, existing_data
    )
    return vmc_request.call_api(
        method=vmc_constants.PATCH_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_nat_rules.update",
        responsebody_applicable=False,
        data=payload,
        verify_ssl=verify_ssl,
        cert=cert,
    )
