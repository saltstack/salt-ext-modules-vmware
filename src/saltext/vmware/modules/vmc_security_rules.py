"""
Salt execution module for VMC Security Rules
Provides methods to Create, Read, Update and Delete security rules.
"""
import logging

from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request
from saltext.vmware.utils import vmc_templates

log = logging.getLogger(__name__)

__virtualname__ = "vmc_security_rules"


def __virtual__():
    return __virtualname__


def _create_payload_for_security_rule(rule_id, domain_id, user_input):
    """
    This function creates the payload based on the template and user input passed
    """
    template_data = getattr(
        vmc_templates, "create_security_rules_" + domain_id, vmc_templates.create_security_rules_cgw
    )
    data = vmc_request.create_payload_for_request(template_data, user_input)
    data["id"] = data["display_name"] = rule_id
    return data


def get(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    domain_id,
    verify_ssl=True,
    cert=None,
    sort_by=None,
    sort_ascending=None,
    page_size=None,
    cursor=None,
):
    """
    Retrieves security rules for Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_security_rules.get hostname=nsxt-manager.local domain_id=mgw ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the security rules should be retrieved

    domain_id
        The domain_id for which the security rules should be retrieved. Possible values: mgw, cgw

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    sort_by
        (Optional) Field by which records are sorted

    sort_ascending
        (Optional) Boolean value to sort result in ascending order

    page_size
        (Optional) Maximum number of results to return in this page

    cursor
        (Optional) Opaque cursor to be used for getting next page of records (supplied by current result page)

    """

    log.info("Retrieving %s Security rules for SDDC %s", domain_id, sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/gateway-policies/default/rules"
    )
    api_url = api_url.format(
        base_url=api_url_base, org_id=org_id, sddc_id=sddc_id, domain_id=domain_id
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
        description="vmc_security_rules.get",
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
    rule_id,
    verify_ssl=True,
    cert=None,
):
    """
    Retrieves given security rule from the given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_security_rules.get_by_id hostname=nsxt-manager.local domain_id=mgw ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the security rule should be retrieved

    domain_id
        The domain_id for which the security rule should be retrieved. Possible values: mgw, cgw

    rule_id
        Id of the security_rule to be retrieved from SDDC

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Retrieving Security rule %s for SDDC %s", rule_id, sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/gateway-policies/default/rules/{rule_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base, org_id=org_id, sddc_id=sddc_id, domain_id=domain_id, rule_id=rule_id
    )

    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_security_rules.get_by_id",
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
    rule_id,
    verify_ssl=True,
    cert=None,
):
    """
    Deletes given security rule from the given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_security_rules.delete hostname=nsxt-manager.local domain_id=mgw ...

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
        The domain_id for which the security rule should be deleted. Possible values: mgw, cgw

    rule_id
        Id of the security_rule to be deleted from SDDC

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Deleting Security rule %s for SDDC %s", rule_id, sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/gateway-policies/default/rules/{rule_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base, org_id=org_id, sddc_id=sddc_id, domain_id=domain_id, rule_id=rule_id
    )

    return vmc_request.call_api(
        method=vmc_constants.DELETE_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_security_rules.delete",
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
):
    """
    Creates security rule for the given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_security_rules.create hostname=nsxt-manager.local domain_id=mgw ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the security rule should be added

    domain_id
        The domain_id for which the security rule should be added. Possible values: mgw, cgw

    rule_id
        Id of the security_rule to be added to given SDDC

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

    Example values:

        .. code::

            {
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
                "tags": [
                    {
                        "tag": "tag1",
                        "scope": "scope1"
                    }
                ]
            }

    """

    log.info("Creating Security rule %s for SDDC %s", rule_id, sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/gateway-policies/default/rules/{rule_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base, org_id=org_id, sddc_id=sddc_id, domain_id=domain_id, rule_id=rule_id
    )

    allowed_dict = {
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
    }

    req_data = vmc_request._filter_kwargs(
        allowed_kwargs=allowed_dict.keys(), allow_none=["tags"], **allowed_dict
    )

    payload = _create_payload_for_security_rule(rule_id, domain_id, req_data)
    return vmc_request.call_api(
        method=vmc_constants.PUT_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_security_rules.create",
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
    Updates security rule for the given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_security_rules.update hostname=nsxt-manager.local domain_id=mgw ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the security rule belongs to

    domain_id
        The domain_id for which the security rule belongs to. Possible values: mgw, cgw

    rule_id
        Id of the security_rule to be updated for given SDDC

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
        Identifier to use when displaying entity in logs or GUI

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
                "tags": [
                    {
                        "tag": "tag1",
                        "scope": "scope1"
                    }
                ]
            }

    """

    log.info("Updating Security rule %s for SDDC %s", rule_id, sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/gateway-policies/default/rules/{rule_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base, org_id=org_id, sddc_id=sddc_id, domain_id=domain_id, rule_id=rule_id
    )

    # fetch the security rule for the given rule_id
    existing_data = get_by_id(
        hostname,
        refresh_key,
        authorization_host,
        org_id,
        sddc_id,
        domain_id,
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
        "tag": tag,
        "logged": logged,
        "disabled": disabled,
        "notes": notes,
        "sequence_number": sequence_number,
        "display_name": display_name,
        "tags": tags,
    }

    req_data = vmc_request._filter_kwargs(
        allowed_kwargs=allowed_dict.keys(), allow_none=["tags"], **allowed_dict
    )

    payload = vmc_request.create_payload_for_request(
        vmc_templates.update_security_rules, req_data, existing_data
    )
    return vmc_request.call_api(
        method=vmc_constants.PATCH_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_security_rules.update",
        responsebody_applicable=False,
        data=payload,
        verify_ssl=verify_ssl,
        cert=cert,
    )
