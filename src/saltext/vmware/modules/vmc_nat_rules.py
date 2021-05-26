"""
Salt execution module for Nat Rules
Provides methods to Create, Update, Read and Delete Nat rules.
"""
from __future__ import absolute_import

import logging
import os

from saltext.vmware.utils import vmc_request
from saltext.vmware.utils import vmc_constants

log = logging.getLogger(__name__)

__virtualname__ = "vmc_nat_rules"


def __virtual__():
    return __virtualname__


def _create_payload_for_nat_rule(rule_id, user_input):
    """
    Helper function for creating nat rule
    """
    script_dir = os.path.dirname(__file__)
    rel_path = "templates/create_nat_rules.json"
    data = vmc_request.create_payload_for_request(script_dir, rel_path, user_input)
    data['id'] = rule_id
    data['display_name'] = rule_id
    return data


def _update_payload_for_nat_rule(existing_data, user_input):
    """
    This function creates the payload for update Nat rule based on the json template, existing data
    and user input passed
    """
    script_dir = os.path.dirname(__file__)
    rel_path = "templates/update_nat_rules.json"
    data = vmc_request.create_payload_for_update_request(script_dir, rel_path, user_input, existing_data)
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
    sort_ascending=None
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
            (Optional) Maximum number of results to return in this page

        sort_by
            (Optional) Field by which records are sorted

        sort_ascending
            (Optional) Boolean value to sort result in ascending order

    """

    log.info("Retrieving Nat rules for SDDC %s", sddc_id)

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = '{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/' \
              'policy/api/v1/infra/tier-1s/{tier1}/nat/{nat}/nat-rules'
    api_url = api_url.format(base_url=api_url_base, org_id=org_id, sddc_id=sddc_id,
                             tier1=tier1, nat=nat)

    params = vmc_request._filter_kwargs(
        allowed_kwargs=["cursor", "page_size", "sort_ascending", "sort_by"],
        default_dict=None,
        cursor=cursor,
        page_size=page_size,
        sort_by=sort_by,
        sort_ascending=sort_ascending,
    )

    return vmc_request.call_api(method=vmc_constants.GET_REQUEST_METHOD,
                                url=api_url,
                                refresh_key=refresh_key,
                                authorization_host=authorization_host,
                                description="vmc_nat_rule.get",
                                responsebody_applicable=True,
                                verify_ssl=verify_ssl,
                                cert=cert,
                                params=params)


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
    cert=None
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
    log.info("Retrieving Nat rule %s for SDDC %s", nat_rule, sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = '{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/' \
              'policy/api/v1/infra/tier-1s/{tier1}/nat/{nat}/nat-rules/{nat_rule}'
    api_url = api_url.format(base_url=api_url_base, org_id=org_id, sddc_id=sddc_id,
                             tier1=tier1, nat=nat, nat_rule=nat_rule)

    return vmc_request.call_api(method=vmc_constants.GET_REQUEST_METHOD,
                                url=api_url,
                                refresh_key=refresh_key,
                                authorization_host=authorization_host,
                                description="vmc_nat_rule.get_by_id",
                                responsebody_applicable=True,
                                verify_ssl=verify_ssl,
                                cert=cert)


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
    cert=None
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
    log.info("Deleting Nat rule %s for SDDC %s", nat_rule, sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = '{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/' \
              'policy/api/v1/infra/tier-1s/{tier1}/nat/{nat}/nat-rules/{nat_rule}'
    api_url = api_url.format(base_url=api_url_base, org_id=org_id, sddc_id=sddc_id,
                             tier1=tier1, nat=nat, nat_rule=nat_rule)
    return vmc_request.call_api(method=vmc_constants.DELETE_REQUEST_METHOD,
                                url=api_url,
                                refresh_key=refresh_key,
                                authorization_host=authorization_host,
                                description="vmc_nat_rule.delete",
                                responsebody_applicable=False,
                                verify_ssl=verify_ssl,
                                cert=cert)


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
    sequence_number=None
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
            specify type of NAT Rule it can have value REFLEXIVE, DNAT

                REFLEXIVE NAT Rule require
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
            (Optional) Policy NAT Rule enabled flag

                The flag, which suggests whether the NAT rule is enabled or
                disabled. The default is True.

        firewall_match
            (Optional) Represents the firewall match flag

                It indicates how the firewall matches the address after NATing if firewall
                stage is not skipped.
                Choices
                    MATCH_EXTERNAL_ADDRESS,
                    MATCH_INTERNAL_ADDRESS
                    Default: "MATCH_INTERNAL_ADDRESS"

        logging
            (Optional) Policy NAT Rule logging flag
                default: False

        description
            (Optional) Description of of NAT Rule

        tags
            (Optional) Opaque identifiers meaningful to the API user. Maximum 30 tags can be associated:
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
                The sequence_number decides the rule_priority of a NAT rule.
                default: 0
            type: int

        following fields user need to enter  field with overriding values

            {
                "action": "REFLEXIVE",
                "translated_network": "10.182.171.36",
                "translated_ports": null,
                "destination_network": "",
                "source_network": "192.168.1.23",
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

    """
    log.info("Creating Nat rule %s for SDDC %s ",nat_rule, sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = '{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/' \
              'policy/api/v1/infra/tier-1s/{tier1}/nat/{nat}/nat-rules/{nat_rule}'
    api_url = api_url.format(base_url=api_url_base, org_id=org_id, sddc_id=sddc_id,
                             tier1=tier1, nat=nat, nat_rule=nat_rule)

    allowed_dict = {
        "action":action,
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
        "sequence_number": sequence_number
    }
    req_data = vmc_request._filter_kwargs(allowed_dict.keys(),
        ["translated_ports", "tags"],
        default_dict={},
        **allowed_dict)

    data = _create_payload_for_nat_rule(nat_rule, req_data)

    return vmc_request.call_api(method=vmc_constants.PUT_REQUEST_METHOD,
                                url=api_url,
                                refresh_key=refresh_key,
                                authorization_host=authorization_host,
                                description="vmc_nat_rule.create",
                                responsebody_applicable=True,
                                data = data,
                                verify_ssl=verify_ssl,
                                cert=cert)


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
    display_name=None
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
            specify type of NAT Rule it can have value REFLEXIVE, DNAT

                REFLEXIVE NAT Rule require
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
            (Optional) Policy NAT Rule enabled flag

                The flag, which suggests whether the NAT rule is enabled or
                disabled. The default is True.

        firewall_match
            (Optional) Represents the firewall match flag

                It indicates how the firewall matches the address after NATing if firewall
                stage is not skipped.
                Choices
                    MATCH_EXTERNAL_ADDRESS,
                    MATCH_INTERNAL_ADDRESS
                    Default: "MATCH_INTERNAL_ADDRESS"

        logging
            (Optional) Policy NAT Rule logging flag
                default: False

        description
            (Optional) Description of of NAT Rule

        tags
            (Optional) Opaque identifiers meaningful to the API user. Maximum 30 tags can be associated:
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
                The sequence_number decides the rule_priority of a NAT rule.
                default: 0
            type: int

        display_name
            Identifier to use when displaying entity in logs or GUI

        following fields user need to enter  field with overriding values

            {
                "action": "REFLEXIVE",
                "translated_network": "10.182.171.36",
                "translated_ports": null,
                "destination_network": "",
                "source_network": "192.168.1.23",
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

    """
    log.info("Updating Nat rule %s for SDDC %s ",nat_rule, sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = '{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/' \
              'policy/api/v1/infra/tier-1s/{tier1}/nat/{nat}/nat-rules/{nat_rule}'
    api_url = api_url.format(base_url=api_url_base, org_id=org_id, sddc_id=sddc_id,
                             tier1=tier1, nat=nat, nat_rule=nat_rule)


    # fetch the nat rule for the given nat_rule
    existing_data = get_by_id(hostname,
                              refresh_key,
                              authorization_host,
                              org_id,
                              sddc_id,
                              tier1,
                              nat,
                              nat_rule,
                              verify_ssl,
                              cert)

    if vmc_constants.ERROR in existing_data:
        return existing_data

    allowed_dict = {
        "action":action,
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
        "display_name": display_name
    }

    req_data = vmc_request._filter_kwargs(allowed_dict.keys(),
        ["translated_ports", "tags"],
        default_dict={},
        **allowed_dict)

    payload = _update_payload_for_nat_rule(existing_data, req_data)
    return vmc_request.call_api(method=vmc_constants.PATCH_REQUEST_METHOD,
                                url=api_url,
                                refresh_key=refresh_key,
                                authorization_host=authorization_host,
                                description="vmc_nat_rules.update",
                                responsebody_applicable=False,
                                data=payload,
                                verify_ssl=verify_ssl,
                                cert=cert)
