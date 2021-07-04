"""
Salt execution module for VMC DHCP Profiles
Provides methods to Create, Read, Update and Delete DHCP Profiles.
"""
import logging

from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request
from saltext.vmware.utils import vmc_templates

log = logging.getLogger(__name__)

__virtualname__ = "vmc_dhcp_profiles"


def __virtual__():
    return __virtualname__


def get(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    type,
    verify_ssl=True,
    cert=None,
    sort_by=None,
    sort_ascending=None,
    page_size=None,
    cursor=None,
):
    """
    Retrieves DHCP profiles of given profile type for given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_dhcp_profiles.get hostname=nsxt-manager.local type=server ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the DHCP profiles should be retrieved

    type
        The type of DHCP profiles to be retrieved. Possible values: server, relay

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

    log.info("Retrieving DHCP %s profiles for SDDC %s", type, sddc_id)
    profile_type = vmc_constants.DHCP_CONFIGS.format(type)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/{profile_type}"
    )
    api_url = api_url.format(
        base_url=api_url_base, org_id=org_id, sddc_id=sddc_id, profile_type=profile_type
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
        description="vmc_dhcp_profiles.get",
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
    type,
    dhcp_profile_id,
    verify_ssl=True,
    cert=None,
):
    """
    Retrieves given DHCP profile of given profile type for given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_dhcp_profiles.get_by_id hostname=nsxt-manager.local type=server ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the DHCP profile should be retrieved

    type
        The type of DHCP profile for which the given DHCP belongs to. Possible values: server, relay

    dhcp_profile_id
        Id of the DHCP profile to be retrieved from SDDC.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Retrieving DHCP profile %s for SDDC %s", dhcp_profile_id, sddc_id)
    profile_type = vmc_constants.DHCP_CONFIGS.format(type)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/{profile_type}/{profile_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base,
        org_id=org_id,
        sddc_id=sddc_id,
        profile_type=profile_type,
        profile_id=dhcp_profile_id,
    )

    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_dhcp_profiles.get_by_id",
        verify_ssl=verify_ssl,
        cert=cert,
    )


def delete(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    type,
    dhcp_profile_id,
    verify_ssl=True,
    cert=None,
):
    """
    Deletes given DHCP profile from the given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_dhcp_profiles.delete hostname=nsxt-manager.local type=server ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC from which the DHCP profile should be deleted

    type
        The type of DHCP profile for which the given dhcp belongs to. Possible values: server, relay

    dhcp_profile_id
        Id of the DHCP profile to be deleted from SDDC.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Deleting DHCP profile %s for SDDC %s", dhcp_profile_id, sddc_id)
    profile_type = vmc_constants.DHCP_CONFIGS.format(type)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/{profile_type}/{profile_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base,
        org_id=org_id,
        sddc_id=sddc_id,
        profile_type=profile_type,
        profile_id=dhcp_profile_id,
    )

    return vmc_request.call_api(
        method=vmc_constants.DELETE_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_dhcp_profiles.delete",
        responsebody_applicable=False,
        verify_ssl=verify_ssl,
        cert=cert,
    )
