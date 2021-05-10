"""
Salt Module to manage VMware NSX-T configuration

"""
import json
import logging

from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)

__virtual_name__ = "nsxt_manager"

NSXT_MANAGER_BASE_URL = "https://{}/api/v1/configs/management"


def __virtual__():
    return __virtual_name__


def set_manager_config(
    hostname,
    publish_fqdns,
    revision,
    username,
    password,
    cert_common_name=None,
    verify_ssl=True,
    cert=None,
):
    """
    Set NSX-T Manager's config

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_manager.set_manager_config hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    publish_fqdns
        Boolean value to set as publish_fqdns

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.
    """

    log.info("Configuration's current Revision: %s", revision)
    req_data = {"publish_fqdns": publish_fqdns, "_revision": revision}

    log.debug("Setting value of publish_fqdns to %s", publish_fqdns)
    url = NSXT_MANAGER_BASE_URL.format(hostname)

    return nsxt_request.call_api(
        method="put",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
        data=req_data,
    )


def get_manager_config(
    hostname, username, password, cert_common_name=None, verify_ssl=True, cert=None
):
    """
    Get NSX-T Manager's config

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_manager.get_manager_config hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    publish_fqdns
        Boolean value to set as publish_fqdns

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.

    """

    url = NSXT_MANAGER_BASE_URL.format(hostname)

    return nsxt_request.call_api(
        method="get",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
    )
