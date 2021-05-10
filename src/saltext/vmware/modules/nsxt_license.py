"""
Manage VMware NSX-T Data Center Licenses

"""
import json
import logging

from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)

__virtualname__ = "nsxt_license"

NSXT_LICENSE_BASE_URL = "https://{management_host}/api/v1/licenses"


def __virtual__():
    return __virtualname__


def get_licenses(hostname, username, password, verify_ssl=True, cert=None, cert_common_name=None):
    """
    Retrieves license keys from Given NSX-T Manager

    CLI Example:

    .. code-block:: bash

    salt vm_minion nsxt_license.get_licenses hostname=nsxt-manager.local username=admin ...


    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.
    """

    url = NSXT_LICENSE_BASE_URL.format(management_host=hostname)
    log.info("Retrieving license from NSX Manager %s", hostname)

    return nsxt_request.call_api(
        method="get",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
    )


def apply_license(
    hostname, username, password, license_key, verify_ssl=True, cert=None, cert_common_name=None
):
    """
    Applies given license key to NSX-T Manager

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_license.apply_license hostname=nsxt-manager.local username=admin ...


    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    license_key
        The license key to be added to NSX-T Manager

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
    url = NSXT_LICENSE_BASE_URL.format(management_host=hostname)
    data = {"license_key": license_key}
    log.debug("Applying license to NSX Manager %s", hostname)

    return nsxt_request.call_api(
        method="post",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
        data=data,
    )


def delete_license(
    hostname, username, password, license_key, verify_ssl=True, cert=None, cert_common_name=None
):
    """
    Deletes given license key in NSX-T Manager

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_license.delete_license hostname=nsxt-manager.local username=admin ...


    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    license_key
        The license key to be deleted in NSX-T Manager

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
    url = (NSXT_LICENSE_BASE_URL + "?action=delete").format(management_host=hostname)
    data = {"license_key": license_key}
    log.debug("Deleting license from NSX Manager %s", hostname)

    response = nsxt_request.call_api(
        method="post",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
        data=data,
    )

    return response or {"message": "License deleted successfully"}
