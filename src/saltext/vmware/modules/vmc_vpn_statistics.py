"""
Salt execution module for VPN statistics
Provides methods to Display VPN Statistics and Sessions.
"""
import logging

from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request

log = logging.getLogger(__name__)

__virtualname__ = "vmc_vpn_statistics"


def __virtual__():
    return __virtualname__


def get_ipsec_statistics(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    locale_service_id,
    service_id,
    session_id,
    tier0_id=None,
    tier1_id=None,
    verify_ssl=True,
    cert=None,
    enforcement_point_path=None,
):
    """
    Retrieves VPN IPSec Statistics from Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_vpn_statistics.get_ipsec_statistics hostname=nsxt-manager.local  ...


    hostname
        The host name of NSX-T manager

    refresh_key
        refresh_key to get access token

    authorization_host
        hostname to get access token

    org_id
        org_id of the SDDC

    sddc_id
        sddc_id from which ipsec statistics should be retrieved

    locale_service_id
        id of locale service for example default

    service_id
        id of service for example default

    session_id
        id of session

    Enter one of the tier0 or tier1 id

    tier0_id
        id of tier0 for example vmc

    tier1_id is currently not supported
        id of tier1

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    enforcement_point_path
        (Optional) String Path of the enforcement point

    """
    log.info("Retrieving ipsec statistics for SDDC %s", sddc_id)

    if tier0_id and tier1_id:
        log.error(vmc_constants.VPN_ERROR_SPECIFY_ONE)
        return {"error": vmc_constants.VPN_ERROR_SPECIFY_ONE}
    elif not (tier0_id or tier1_id):
        log.error(vmc_constants.VPN_ERROR_SPECIFY_ATLEAST_ONE)
        return {"error": vmc_constants.VPN_ERROR_SPECIFY_ATLEAST_ONE}

    if tier0_id:
        tier = "tier-0s"
        tier_id = tier0_id
    else:
        tier = "tier-1s"
        tier_id = tier1_id

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/{tier}/{tier_id}/locale-services/{locale_service_id}/"
        "ipsec-vpn-services/{service_id}/sessions/{session_id}/statistics"
    )
    api_url = api_url.format(
        base_url=api_url_base,
        org_id=org_id,
        sddc_id=sddc_id,
        tier=tier,
        tier_id=tier_id,
        locale_service_id=locale_service_id,
        service_id=service_id,
        session_id=session_id,
    )

    params = vmc_request._filter_kwargs(
        allowed_kwargs=["enforcement_point_path"], enforcement_point_path=enforcement_point_path
    )
    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_vpn_statistics.get_ipsec_statistics",
        verify_ssl=verify_ssl,
        cert=cert,
        params=params,
    )


def get_ipsec_sessions(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    locale_service_id,
    service_id,
    tier0_id=None,
    tier1_id=None,
    verify_ssl=True,
    cert=None,
    cursor=None,
    page_size=None,
    sort_by=None,
    sort_ascending=None,
):
    """
    Retrieves ipsec session from Given SDDC
        this also include l2vpn sessions

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_vpn_statistics.get_ipsec_sessions hostname=nsxt-manager.local  ...

    hostname
        The host name of NSX-T manager

    refresh_key
        refresh_key to get access token

    authorization_host
        hostname to get access token

    org_id
        org_id of the SDDC

    sddc_id
        sddc_id from which public ips should be retrieved

    locale_service_id
        id of locale service for example default

    service_id
        id of service for example default

    Enter one of the tier0 or tier1 id

    tier0_id
        id of tier0 for example vmc

    tier1_id is currently not supported
        id of tier1

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

    log.info("Retrieving ipsec sessions for SDDC %s", sddc_id)

    if tier0_id and tier1_id:
        log.error(vmc_constants.VPN_ERROR_SPECIFY_ONE)
        return {"error": vmc_constants.VPN_ERROR_SPECIFY_ONE}
    elif not (tier0_id or tier1_id):
        log.error(vmc_constants.VPN_ERROR_SPECIFY_ATLEAST_ONE)
        return {"error": vmc_constants.VPN_ERROR_SPECIFY_ATLEAST_ONE}

    if tier0_id:
        tier = "tier-0s"
        tier_id = tier0_id
    else:
        tier = "tier-1s"
        tier_id = tier1_id

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/{tier}/{tier_id}/locale-services/{locale_service_id}/"
        "ipsec-vpn-services/{service_id}/sessions"
    )
    api_url = api_url.format(
        base_url=api_url_base,
        org_id=org_id,
        sddc_id=sddc_id,
        tier=tier,
        tier_id=tier_id,
        locale_service_id=locale_service_id,
        service_id=service_id,
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
        description="vmc_vpn_statistics.get_ipsec_sessions",
        verify_ssl=verify_ssl,
        cert=cert,
        params=params,
    )


def get_l2vpn_statistics(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    locale_service_id,
    service_id,
    session_id,
    tier0_id=None,
    tier1_id=None,
    verify_ssl=True,
    cert=None,
    enforcement_point_path=None,
    source=None,
):
    """
    Retrieves L2VPN Statistics from Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_vpn_statistics.get_l2vpn_statistics hostname=nsxt-manager.local  ...


    hostname
        The host name of NSX-T manager

    refresh_key
        refresh_key to get access token

    authorization_host
        hostname to get access token

    org_id
        org_id of the SDDC

    sddc_id
        sddc_id from which ipsec statistics should be retrieved

    locale_service_id
        id of locale service for example default

    service_id
        id of service for example default

    session_id
        id of session

    Enter one of the tier0 or tier1 id

    tier0_id
        id of tier0 for example vmc

    tier1_id is currently not supported
        id of tier1

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    enforcement_point_path
        (Optional) String Path of the enforcement point

    source
        (Optional) valid options are realtime, cached
    """

    log.info("Retrieving l2vpn statistics for SDDC %s", sddc_id)

    if tier0_id and tier1_id:
        log.error(vmc_constants.VPN_ERROR_SPECIFY_ONE)
        return {"error": vmc_constants.VPN_ERROR_SPECIFY_ONE}
    elif not (tier0_id or tier1_id):
        log.error(vmc_constants.VPN_ERROR_SPECIFY_ATLEAST_ONE)
        return {"error": vmc_constants.VPN_ERROR_SPECIFY_ATLEAST_ONE}

    if tier0_id:
        tier = "tier-0s"
        tier_id = tier0_id
    else:
        tier = "tier-1s"
        tier_id = tier1_id

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/{tier}/{tier_id}/locale-services/{locale_service_id}/"
        "l2vpn-services/{service_id}/sessions/{session_id}/statistics"
    )
    api_url = api_url.format(
        base_url=api_url_base,
        org_id=org_id,
        sddc_id=sddc_id,
        tier=tier,
        tier_id=tier_id,
        locale_service_id=locale_service_id,
        service_id=service_id,
        session_id=session_id,
    )

    params = vmc_request._filter_kwargs(
        allowed_kwargs=["enforcement_point_path", "source"],
        enforcement_point_path=enforcement_point_path,
        source=source,
    )

    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_vpn_statistics.get_l2vpn_statistics",
        verify_ssl=verify_ssl,
        cert=cert,
        params=params,
    )


def get_l2vpn_sessions(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    locale_service_id,
    service_id,
    tier0_id=None,
    tier1_id=None,
    verify_ssl=True,
    cert=None,
    cursor=None,
    page_size=None,
    sort_by=None,
    sort_ascending=None,
):
    """
    Retrieves l2vpn session from Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_vpn_statistics.get_l2vpn_sessions hostname=nsxt-manager.local  ...

    hostname
        The host name of NSX-T manager

    refresh_key
        refresh_key to get access token

    authorization_host
        hostname to get access token

    org_id
        org_id of the SDDC

    sddc_id
        sddc_id from which public ips should be retrieved

    locale_service_id
        id of locale service for example default

    service_id
        id of service for example default

    Enter one of the tier0 or tier1 id

    tier0_id
        id of tier0 for example vmc

    tier1_id is currently not supported
        id of tier1

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

    log.info("Retrieving l2vpn sessions for SDDC %s", sddc_id)

    if tier0_id and tier1_id:
        log.error(vmc_constants.VPN_ERROR_SPECIFY_ONE)
        return {"error": vmc_constants.VPN_ERROR_SPECIFY_ONE}
    elif not (tier0_id or tier1_id):
        log.error(vmc_constants.VPN_ERROR_SPECIFY_ATLEAST_ONE)
        return {"error": vmc_constants.VPN_ERROR_SPECIFY_ATLEAST_ONE}

    if tier0_id:
        tier = "tier-0s"
        tier_id = tier0_id
    else:
        tier = "tier-1s"
        tier_id = tier1_id

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/{tier}/{tier_id}/locale-services/{locale_service_id}/"
        "l2vpn-services/{service_id}/sessions"
    )
    api_url = api_url.format(
        base_url=api_url_base,
        org_id=org_id,
        sddc_id=sddc_id,
        tier=tier,
        tier_id=tier_id,
        locale_service_id=locale_service_id,
        service_id=service_id,
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
        description="vmc_vpn_statistics.get_l2vpn_sessions",
        verify_ssl=verify_ssl,
        cert=cert,
        params=params,
    )
