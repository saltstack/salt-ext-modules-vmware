"""
Salt execution module for Nat Rules
Provides methods to Create, Update, Read and Delete Nat rules.
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

    log.info("Retrieving Nat rules for SDDC %s", sddc_id)

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
    log.info("Retrieving Nat rule %s for SDDC %s", nat_rule, sddc_id)
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
    log.info("Deleting Nat rule %s for SDDC %s", nat_rule, sddc_id)
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
