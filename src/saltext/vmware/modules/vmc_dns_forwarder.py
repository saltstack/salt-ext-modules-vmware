"""
Salt execution module for VMC DNS Forwarder zones and services
Provides methods to show DNS zones and services.
"""
import logging

from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request

log = logging.getLogger(__name__)

__virtualname__ = "vmc_dns_forwarder"


def __virtual__():
    return __virtualname__


def get_dns_zones(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    verify_ssl=True,
    cert=None,
    sort_by=None,
    sort_ascending=None,
    page_size=None,
    cursor=None,
):
    """
    Retrieves DNS zones for Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_dns_forwarder.get_dns_zones hostname=nsxt-manager.local...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the DNS zones should be retrieved

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    sort_by
        (Optional) Field by which records are sorted

    sort_ascending
        (Optional) Boolean value to sort result in ascending order. Enabled by default.

    page_size
        (Optional) Maximum number of results to return in this page. Default page size is 1000.

    cursor
        (Optional) Opaque cursor to be used for getting next page of records (supplied by current result page)

    """

    log.info("Retrieving DNS zones for SDDC %s", sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/dns-forwarder-zones"
    )
    api_url = api_url.format(base_url=api_url_base, org_id=org_id, sddc_id=sddc_id)

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
        description="vmc_dns_forwarder.get_dns_zones",
        verify_ssl=verify_ssl,
        cert=cert,
        params=params,
    )


def get_dns_services(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    verify_ssl=True,
    cert=None,
    page_size=None,
    cursor=None,
):
    """
    Retrieves DNS services for the given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_dns_forwarder.get_dns_services hostname=nsxt-manager.local ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the DNS services should be retrieved

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    page_size
        (Optional) Maximum number of results to return in this page. Default page size is 1000.

    cursor
        (Optional) Integer cursor to be used for getting next page of records (supplied by current result page)

    """

    log.info("Retrieving DNS services for SDDC %s", sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/search?query=resource_type:PolicyDnsForwarder"
    )

    api_url = api_url.format(base_url=api_url_base, org_id=org_id, sddc_id=sddc_id)

    params = vmc_request._filter_kwargs(
        allowed_kwargs=["cursor", "page_size"], cursor=cursor, page_size=page_size
    )

    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_dns_forwarder.get_dns_services",
        verify_ssl=verify_ssl,
        cert=cert,
        params=params,
    )
