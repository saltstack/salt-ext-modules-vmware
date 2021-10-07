"""
Salt execution module for security groups
Provides methods to Create, Read, Update and Delete security groups.
"""
import logging
import os

from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request
from saltext.vmware.utils import vmc_templates

log = logging.getLogger(__name__)

__virtualname__ = "vmc_security_groups"


def __virtual__():
    return __virtualname__


def _create_payload_for_security_group(security_group_id, domain_id, user_input):
    """
    This function creates the payload based on the template and user input passed
    """
    template_data = getattr(
        vmc_templates,
        "create_security_groups_" + domain_id,
        vmc_templates.create_security_groups_cgw,
    )
    data = vmc_request.create_payload_for_request(template_data, user_input)
    data["id"] = data["display_name"] = security_group_id
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
    cursor=None,
    page_size=None,
    sort_by=None,
    sort_ascending=None,
):
    """
    Retrieves security groups from Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_security_groups.get hostname=nsxt-manager.local  ...


    hostname
        The host name of NSX-T manager

    refresh_key
        refresh_key to get access token

    authorization_host
        hostname to get access token

    org_id
        org_id of the SDDC

    sddc_id
        sddc_id from which security groupss should be retrieved

    domain_id
        The domain_id for which the security groups should be retrieved

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
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
    log.info("Retrieving security groups for SDDC %s", sddc_id)

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/groups"
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
        description="vmc_security_groups.get",
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
    security_group_id,
    verify_ssl=True,
    cert=None,
):
    """
    Retrieves security groups from Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_security_groups.get_by_id hostname=nsxt-manager.local security_group_id ...

    hostname
        The host name of NSX-T manager

    refresh_key
        refresh_key to get access token

    authorization_host
        hostname to get access token

    org_id
        org_id of the SDDC

    sddc_id
        sddc_id from which security groups should be retrieved

    domain_id
        The domain_id for which the security groups should be retrieved

    scurity_group_id
        Id of the security group to be retrieved from SDDC

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.
    """
    log.info("Retrieving security group %s for SDDC %s", security_group_id, sddc_id)

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/groups/{security_group_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_group_id=security_group_id,
    )

    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_security_groups.get_by_id",
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
    security_group_id,
    verify_ssl=True,
    cert=None,
):
    """
    Delete security groups from Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_security_groups.delete hostname=nsxt-manager.local security_group_id=security_group_id ...

    hostname
        The host name of NSX-T manager

    refresh_key
        refresh_key to get access token

    authorization_host
        hostname to get access token

    org_id
        org_id of the SDDC

    sddc_id
        sddc_id from which security groups will be deleted

    domain_id
        The domain_id for which the security groups should be deleted

    security_group_id
        sepcific security groups id

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """
    log.info("Deleting security group %s for SDDC %s", security_group_id, sddc_id)

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/groups/{security_group_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_group_id=security_group_id,
    )
    return vmc_request.call_api(
        method=vmc_constants.DELETE_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_security_groups.delete",
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
    security_group_id,
    verify_ssl=True,
    cert=None,
    expression=None,
    description=None,
    tags=vmc_constants.VMC_NONE,
):
    """
    Create security groups for Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_security_groups.create hostname=nsxt-manager.local public_ip_name=vmc_security_groups ...

    hostname
        The host name of NSX-T manager

    refresh_key
        refresh_key to get access token

    authorization_host
        hostname to get access token

    org_id
        org_id of the SDDC

    sddc_id
        sddc_id for which security groups should be retrieved.

    domain_id
        The domain_id for which the security groups should be retrieved.  Possible values: mgw and cgw

    security_group_id
        name of security groups it will create id same as name.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    expression
        (Optional) Expression for security group members
            The expression list must follow below criteria:
            1. A non-empty expression list, must be of odd size. In a list, with
            indices starting from 0, all non-conjunction expressions must be at
            even indices, separated by a conjunction expression at odd
            indices.
            2. The total of ConditionExpression and NestedExpression in a list
            should not exceed 5.
            3. The total of IPAddressExpression, MACAddressExpression, external
            IDs in an ExternalIDExpression and paths in a PathExpression must not exceed
            500.
            4. Each expression must be a valid Expression. See the definition of
            the Expression type for more information.

        Its list of dicts

            Example values

            1. [{"member_type":"VirtualMachine","resource_type":"ExternalIDExpression",
            "external_ids":["52bf8bd0-95b1-2e58-5180-ccfa743da576"]}]

            2. [{"value":"Linux","member_type":"VirtualMachine","key":"OSName",
               "operator":"EQUALS","resource_type":"Condition"},
               {"resource_type":"ConjunctionOperator","conjunction_operator":"OR"},
               {"member_type":"VirtualMachine","resource_type":"ExternalIDExpression",
               "external_ids":["52bf8bd0-95b1-2e58-5180-ccfa743da576"]}]

            3. [{"ip_addresses" : ["10.2.23.1", "10.2.23.2"],
                  "resource_type" : "IPAddressExpression"} ]

            default value is []

    description
        (Optional) Description of Security Groups
            default value is ""

    tags
        (Optional) Opaque identifiers meaningful to the API user. Maximum 30 tags can be associated:
            default value is []

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

    Example values:

        .. code-block::

            {
                "expression": [
                  {
                    "member_type": "VirtualMachine",
                    "value": "webvm",
                    "key": "Tag",
                    "operator": "EQUALS",
                    "resource_type": "Condition"
                  }
                ],
                "description": "web group"
            }

    Please refer the `Security Groups <https://developer.vmware.com/docs/nsx-vmc-policy/latest/policy/api/v1/infra/domains/domain-id/groups/group-id/put/>`_ to get insight of input parameters

    """
    log.info("Creating security group %s for SDDC %s", security_group_id, sddc_id)

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/groups/{security_group_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_group_id=security_group_id,
    )

    allowed_dict = {
        "expression": expression,
        "description": description,
        "tags": tags,
    }
    req_data = vmc_request._filter_kwargs(
        allowed_kwargs=allowed_dict.keys(), allow_none=["tags"], **allowed_dict
    )

    payload = _create_payload_for_security_group(security_group_id, domain_id, req_data)
    return vmc_request.call_api(
        method=vmc_constants.PUT_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_security_groups.create",
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
    security_group_id,
    verify_ssl=True,
    cert=None,
    expression=None,
    description=None,
    tags=vmc_constants.VMC_NONE,
    display_name=None,
):
    """
    Update security groups for Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_security_groups.update hostname=nsxt-manager.local public_ip_name=vmc_security_groups ...

    hostname
        The host name of NSX-T manager

    refresh_key
        refresh_key to get access token

    authorization_host
        hostname to get access token

    org_id
        org_id of the SDDC

    sddc_id
        sddc_id for which security groups should be retrieved

    domain_id
        The domain_id for which the security groups should be retrieved. Possible values: mgw and cgw

    security_group_id
        name of security groups it will update

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    expression
        (Optional) Expression for security group members
            The expression list must follow below criteria:
            1. A non-empty expression list, must be of odd size. In a list, with
            indices starting from 0, all non-conjunction expressions must be at
            even indices, separated by a conjunction expression at odd
            indices.
            2. The total of ConditionExpression and NestedExpression in a list
            should not exceed 5.
            3. The total of IPAddressExpression, MACAddressExpression, external
            IDs in an ExternalIDExpression and paths in a PathExpression must not exceed
            500.
            4. Each expression must be a valid Expression. See the definition of
            the Expression type for more information.

        Its list of dicts
            Example values

            1. [{"member_type":"VirtualMachine","resource_type":"ExternalIDExpression",
            "external_ids":["52bf8bd0-95b1-2e58-5180-ccfa743da576"]}]

            2. [{"value":"Linux","member_type":"VirtualMachine","key":"OSName",
               "operator":"EQUALS","resource_type":"Condition"},
               {"resource_type":"ConjunctionOperator","conjunction_operator":"OR"},
               {"member_type":"VirtualMachine","resource_type":"ExternalIDExpression",
               "external_ids":["52bf8bd0-95b1-2e58-5180-ccfa743da576"]}]

            3. [{ip_addresses" : ["10.2.23.1", "10.2.23.2"],
                  "resource_type" : "IPAddressExpression"} ]

            default value is []

    description
        (Optional) Description of Security Groups
        default value is ""

    tags
        (Optional) Opaque identifiers meaningful to the API user. Maximum 30 tags can be associated:
        default value is [] empty list

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

    display_name
        Identifier to use when displaying entity in logs or GUI

    Example values:

        .. code-block::

            {
                "expression": [
                  {
                    "member_type": "VirtualMachine",
                    "value": "webvm",
                    "key": "Tag",
                    "operator": "EQUALS",
                    "resource_type": "Condition"
                  }
                ],
                "description": "web group"
            }

    Please refer the `Security groups update <https://developer.vmware.com/docs/nsx-vmc-policy/latest/policy/api/v1/infra/domains/domain-id/groups/group-id/patch/>`_ to get insight of input parameters

    """
    log.info("Updating security group %s for SDDC %s", security_group_id, sddc_id)

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/groups/{security_group_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_group_id=security_group_id,
    )

    existing_data = get_by_id(
        hostname,
        refresh_key,
        authorization_host,
        org_id,
        sddc_id,
        domain_id,
        security_group_id,
        verify_ssl,
        cert,
    )

    if "error" in existing_data:
        return existing_data

    allowed_dict = {
        "display_name": display_name,
        "expression": expression,
        "description": description,
        "tags": tags,
    }
    req_data = vmc_request._filter_kwargs(
        allowed_kwargs=allowed_dict.keys(), allow_none=["tags"], **allowed_dict
    )

    payload = vmc_request.create_payload_for_request(
        vmc_templates.update_security_groups, req_data, existing_data
    )
    return vmc_request.call_api(
        method=vmc_constants.PATCH_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_security_groups.update",
        responsebody_applicable=False,
        data=payload,
        verify_ssl=verify_ssl,
        cert=cert,
    )
