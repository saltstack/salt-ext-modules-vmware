"""
Salt execution module for VMC Direct Connect
Provides methods to Display Direct Connect Information of an SDDC.
"""
import logging

from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request

log = logging.getLogger(__name__)

__virtualname__ = "vmc_direct_connect"


def __virtual__():
    return __virtualname__


def get_accounts(
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl=True, cert=None
):
    """
    Retrieves Direct Connect Account information for given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_direct_connect.get_accounts hostname=nsxt-manager.local ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the Direct Connect Account information should be retrieved

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Retrieving Direct Connect Account information for SDDC %s", sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "cloud-service/api/v1/infra/accounts"
    )
    api_url = api_url.format(base_url=api_url_base, org_id=org_id, sddc_id=sddc_id)
    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_direct_connect.get_accounts",
        verify_ssl=verify_ssl,
        cert=cert,
    )


def get_associated_groups(
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl=True, cert=None
):
    """
    Retrieves Direct Connect Associated Groups information for given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_direct_connect.get_associated_groups hostname=nsxt-manager.local ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the Direct Connect Associated Groups information should be retrieved

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Retrieving Direct Connect Associated Groups information for SDDC %s", sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "cloud-service/api/v1/infra/associated-groups/"
    )
    api_url = api_url.format(base_url=api_url_base, org_id=org_id, sddc_id=sddc_id)
    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_direct_connect.get_associated_groups",
        verify_ssl=verify_ssl,
        cert=cert,
    )


def get_bgp_info(
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl=True, cert=None
):
    """
    Retrieves Direct Connect BGP related information for given SDDC, including current Autonomous System Number
    of the VGW attached to the VPC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_direct_connect.get_bgp_info hostname=nsxt-manager.local ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the Direct Connect BGP related information should be retrieved

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Retrieving Direct Connect BGP related information for SDDC %s", sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "cloud-service/api/v1/infra/direct-connect/bgp"
    )
    api_url = api_url.format(base_url=api_url_base, org_id=org_id, sddc_id=sddc_id)
    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_direct_connect.get_bgp_info",
        verify_ssl=verify_ssl,
        cert=cert,
    )


def get_bgp_status(
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl=True, cert=None
):
    """
    Retrieves Direct Connect BGP status information for given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_direct_connect.get_bgp_status hostname=nsxt-manager.local ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the Direct Connect BGP status information should be retrieved

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Retrieving Direct Connect BGP status information for SDDC %s", sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "cloud-service/api/v1/infra/realized-state/status?intent_path=/infra/direct-connect/bgp"
    )
    api_url = api_url.format(base_url=api_url_base, org_id=org_id, sddc_id=sddc_id)
    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_direct_connect.get_bgp_status",
        verify_ssl=verify_ssl,
        cert=cert,
    )


def get_advertised_routes(
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl=True, cert=None
):
    """
    Retrieves BGP routes that are advertised by Direct Connect from VMC provider to on-premise datacenter.

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_direct_connect.get_advertised_routes hostname=nsxt-manager.local ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the BGP routes that are advertised by Direct Connect should be retrieved

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Retrieving BGP routes that are advertised by Direct Connect of an SDDC %s", sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "cloud-service/api/v1/infra/direct-connect/routes/advertised"
    )
    api_url = api_url.format(base_url=api_url_base, org_id=org_id, sddc_id=sddc_id)
    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_direct_connect.get_advertised_routes",
        verify_ssl=verify_ssl,
        cert=cert,
    )


def get_learned_routes(
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl=True, cert=None
):
    """
    Retrieve BGP routes that are learned by Direct Connect from on-premise datacenter.

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_direct_connect.get_learned_routes hostname=nsxt-manager.local ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the BGP routes that are learned by Direct Connect should be retrieved

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Retrieving BGP routes that are learned by Direct Connect of an SDDC %s", sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "cloud-service/api/v1/infra/direct-connect/routes/learned"
    )
    api_url = api_url.format(base_url=api_url_base, org_id=org_id, sddc_id=sddc_id)
    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_direct_connect.get_learned_routes",
        verify_ssl=verify_ssl,
        cert=cert,
    )


def get_vifs(
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl=True, cert=None
):
    """
    Retrieves Direct Connect VIFs (Virtual Interface) available in the given SDDC. The response includes all
    non-connected VIFs (with states "available", "down", "pending" and "confirming") and connected VIFs that are
    available to the given SDDC.

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_direct_connect.get_vifs hostname=nsxt-manager.local ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the Direct Connect VIFs should be retrieved

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Retrieving Direct Connect VIFs available in the SDDC %s", sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "cloud-service/api/v1/infra/direct-connect/vifs"
    )
    api_url = api_url.format(base_url=api_url_base, org_id=org_id, sddc_id=sddc_id)
    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_direct_connect.get_vifs",
        verify_ssl=verify_ssl,
        cert=cert,
    )
