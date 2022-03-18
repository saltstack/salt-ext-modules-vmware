"""
Salt execution module for VMC distributed firewall rules
Provides methods to Create, Read, Update and Delete distributed firewall rules.
"""
import logging
import os

from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request
from saltext.vmware.utils import vmc_templates

log = logging.getLogger(__name__)

__virtualname__ = "vmc_distributed_firewall_rules"
__func_alias__ = {"list_": "list"}


def __virtual__():
    return __virtualname__


def _create_payload_for_distributed_firewall_rule(rule_id, user_input):
    """
    This function creates the payload based on the template and user input passed
    """
    data = vmc_request.create_payload_for_request(
        vmc_templates.create_distributed_firewall_rules, user_input
    )
    data["id"] = data["display_name"] = rule_id
    return data


def list_(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    domain_id,
    security_policy_id,
    verify_ssl=True,
    cert=None,
    cursor=None,
    page_size=None,
    sort_by=None,
    sort_ascending=None,
):
    """
    Retrieves distributed firewall rules for Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_distributed_firewall_rules.list hostname=nsxt-manager.local domain_id=cgw ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the distributed firewall rules should be retrieved

    domain_id
        The domain_id for which the distributed firewall rules should be retrieved. Possible values: mgw, cgw

    security_policy_id
        Security policy id for which rule should be retrieved

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
    log.info("Retrieving %s distributed firewall rules for SDDC %s", domain_id, sddc_id)

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/security-policies/{security_policy_id}/rules"
    )
    api_url = api_url.format(
        base_url=api_url_base,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_policy_id=security_policy_id,
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
        description="vmc_distributed_firewall_rules.list",
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
    domain_id,
    security_policy_id,
    rule_id,
    verify_ssl=True,
    cert=None,
):
    """
    Retrieves given distributed firewall rule from the given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_distributed_firewall_rules.get_by_id hostname=nsxt-manager.local domain_id=cgw ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the distributed firewall rule should be retrieved

    domain_id
        The domain_id for which the distributed firewall rule should be retrieved. Possible values: mgw, cgw

    security_policy_id
        Security policy id for which rule should be retrieved

    rule_id
        The distribute firewall rule id, any static unique string identifying the rule.
        Also same as the display_name by default.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    """
    log.info("Retrieving distributed firewall rule %s for SDDC %s", rule_id, sddc_id)

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/security-policies/{security_policy_id}/rules/{rule_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_policy_id=security_policy_id,
        rule_id=rule_id,
    )

    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_distributed_firewall_rules.get_by_id",
        verify_ssl=verify_ssl,
        cert=cert,
    )


def delete(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    domain_id,
    security_policy_id,
    rule_id,
    verify_ssl=True,
    cert=None,
):
    """
    Deletes given distributed firewall rule from the given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_distributed_firewall_rules.delete hostname=nsxt-manager.local domain_id=cgw ...

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
        The domain_id for which the distributed firewall rule should be deleted. Possible values: mgw, cgw

    security_policy_id
        Security policy id for which rule should be deleted

    rule_id
        The distribute firewall rule id, any static unique string identifying the rule.
        Also same as the display_name by default.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    """
    log.info("Deleting distributed firewall rule %s for SDDC %s", rule_id, sddc_id)

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/security-policies/{security_policy_id}/rules/{rule_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_policy_id=security_policy_id,
        rule_id=rule_id,
    )

    return vmc_request.call_api(
        method=vmc_constants.DELETE_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_distributed_firewall_rules.delete",
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
    domain_id,
    security_policy_id,
    rule_id,
    verify_ssl=True,
    cert=None,
    source_groups=None,
    destination_groups=None,
    services=None,
    scope=None,
    action=None,
    sequence_number=None,
    disabled=None,
    logged=None,
    description=None,
    direction=None,
    notes=None,
    tag=None,
    tags=vmc_constants.VMC_NONE,
):
    """
    Creates Distributed firewall rule for the given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_distributed_firewall_rules.create hostname=nsxt-manager.local domain_id=cgw ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the Distributed firewall rule should be added

    domain_id
        The domain_id for which the Distributed firewall rule should be added. Possible values: default, cgw

    security_policy_id
        Security policy id for which rule should be added

    rule_id
        Id of the distribute firewall rule to be added to given SDDC

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

    Example Values:

       .. code-block::

           {
              "description": " comm entry",
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

    Notes:
        For domain_id cgw
        Rule must have valid values for source, and destination: either source or destination should have valid groups

    Please refer the `Distributed firewall rules <https://developer.vmware.com/apis/nsx-vmc-policy/latest/policy/api/v1/infra/domains/domain-id/security-policies/security-policy-id/rules/rule-id/put/>`_ to get insight of input parameters

    """
    log.info("Creating Distributed firewall rule %s for SDDC %s", rule_id, sddc_id)

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/security-policies/{security_policy_id}/rules/{rule_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_policy_id=security_policy_id,
        rule_id=rule_id,
    )

    allowed_dict = {
        "source_groups": source_groups,
        "destination_groups": destination_groups,
        "services": services,
        "scope": scope,
        "action": action,
        "sequence_number": sequence_number,
        "disabled": disabled,
        "logged": logged,
        "description": description,
        "direction": direction,
        "notes": notes,
        "tag": tag,
        "tags": tags,
    }

    req_data = vmc_request._filter_kwargs(
        allowed_kwargs=allowed_dict.keys(), allow_none=["tags"], **allowed_dict
    )

    payload = _create_payload_for_distributed_firewall_rule(rule_id, req_data)
    return vmc_request.call_api(
        method=vmc_constants.PUT_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_distributed_firewall_rules.create",
        data=payload,
        verify_ssl=verify_ssl,
        cert=cert,
    )


def update(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    domain_id,
    security_policy_id,
    rule_id,
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
    Updates Distributed firewall rule for the given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_distributed_firewall_rules.update hostname=nsxt-manager.local domain_id=cgw ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the Distributed firewall rule belongs to

    domain_id
        The domain_id for which the Distributed firewall rule belongs to. Possible values: default, cgw

    rule_id
        Id of the distributed firewall rule to be updated for given SDDC

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

    Please refer the `Update Distributed firewall rules <https://developer.vmware.com/apis/nsx-vmc-policy/latest/policy/api/v1/infra/domains/domain-id/security-policies/security-policy-id/rules/rule-id/patch/>`_ to get insight of input parameters

    """
    log.info("Updating Distributed firewall rule %s for SDDC %s", rule_id, sddc_id)

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/security-policies/{security_policy_id}/rules/{rule_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_policy_id=security_policy_id,
        rule_id=rule_id,
    )

    # fetch the Distributed firewall rule for the given rule_id
    existing_data = get_by_id(
        hostname,
        refresh_key,
        authorization_host,
        org_id,
        sddc_id,
        domain_id,
        security_policy_id,
        rule_id,
        verify_ssl,
        cert,
    )

    if vmc_constants.ERROR in existing_data:
        return existing_data

    allowed_dict = {
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

    req_data = vmc_request._filter_kwargs(
        allowed_kwargs=allowed_dict.keys(), allow_none=["tags"], **allowed_dict
    )

    payload = vmc_request.create_payload_for_request(
        vmc_templates.update_distributed_firewall_rules, req_data, existing_data
    )
    return vmc_request.call_api(
        method=vmc_constants.PATCH_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_distributed_firewall_rules.update",
        responsebody_applicable=False,
        data=payload,
        verify_ssl=verify_ssl,
        cert=cert,
    )
