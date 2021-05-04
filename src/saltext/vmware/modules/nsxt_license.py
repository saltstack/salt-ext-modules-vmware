"""
Manage VMware NSX-T Data Center Licenses

"""
import json
import logging

import requests
from requests.exceptions import HTTPError
from requests.exceptions import RequestException
from requests.exceptions import SSLError
from saltext.vmware.modules.ssl_adapter import HostHeaderSSLAdapter

log = logging.getLogger(__name__)

__virtualname__ = "nsxt_license"


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
        Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.
    """

    url = "https://{management_host}/api/v1/licenses".format(management_host=hostname)

    msg = "Retrieving license from NSX Manager {}".format(hostname)
    log.info(msg)

    session = requests.Session()
    headers = dict({"Accept": "application/json"})

    verify = verify_ssl
    if verify_ssl and not cert:
        result = {
            "error": "No certificate path specified. Please specify certificate path in cert parameter"
        }
        return result

    if verify_ssl:
        verify = cert

    if cert_common_name and verify_ssl:
        session.mount("https://", HostHeaderSSLAdapter())
        headers["Host"] = cert_common_name

    try:
        response = session.get(url=url, auth=(username, password), verify=verify, headers=headers)
        # raise error if any
        response.raise_for_status()
    except HTTPError as e:
        log.error(e)
        result = {
            "error": "Error occurred while retrieving the license. Please check logs for more details."
        }
        # if response contains json, extract error message from it
        if e.response.text:
            log.error("Response from NSX Manager {}".format(e.response.text))
            try:
                error_json = e.response.json()
                if error_json["error_message"]:
                    result["error"] = e.response.json()["error_message"]
            except ValueError:
                log.error(
                    "Couldn't parse the response as json. Returning response text as error message"
                )
                result["error"] = e.response.text
        return result
    except SSLError as se:
        log.error(se)
        result = {
            "error": "SSL Error occurred while retrieving licenses."
            "Please check if the certificate is valid and hostname matches certificate common name."
        }
        return result
    except RequestException as re:
        log.error(re)
        result = {
            "error": "Error occurred while retrieving licenses. Please check logs for more details."
        }
        return result
    return response.json()


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
        Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.

    """
    url = "https://{management_host}/api/v1/licenses".format(management_host=hostname)
    data = {"license_key": license_key}
    msg = "Applying license to NSX Manager {}".format(hostname)
    log.debug(msg)
    session = requests.Session()
    headers = dict({"Accept": "application/json", "Content-Type": "application/json"})

    verify = verify_ssl
    if verify_ssl and not cert:
        result = {
            "error": "No certificate path specified. Please specify certificate path in cert parameter"
        }
        return result

    if verify_ssl:
        verify = cert

    if cert_common_name and verify_ssl:
        session.mount("https://", HostHeaderSSLAdapter())
        headers["Host"] = cert_common_name

    try:
        response = session.post(
            url=url,
            auth=(username, password),
            data=json.dumps(data),
            verify=verify,
            headers=headers,
        )
        # raise error if any
        response.raise_for_status()
    except HTTPError as e:
        log.error(e)
        result = {
            "error": "Error occurred while applying the license. Please check logs for more details."
        }
        if e.response.text:
            log.error("Response from NSX Manager {}".format(e.response.text))
            try:
                error_json = e.response.json()
                if error_json["error_message"]:
                    result["error"] = e.response.json()["error_message"]
            except ValueError:
                log.error(
                    "Couldn't parse the response as json. Returning response text as error message"
                )
                result["error"] = e.response.text
        return result
    except SSLError as se:
        log.error(se)
        result = {
            "error": "SSL Error occurred while applying the license."
            "Please check if the certificate is valid and hostname matches certificate common name."
        }
        return result
    except RequestException as re:
        log.error(re)
        result = {
            "error": "Error occurred while applying license. Please check logs for more details."
        }
        return result
    return response.json()


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
        Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.

    """
    url = "https://{management_host}/api/v1/licenses?action=delete".format(management_host=hostname)
    data = {"license_key": license_key}
    msg = "Deleting license from NSX Manager {}".format(hostname)
    log.debug(msg)
    session = requests.Session()
    headers = dict({"Accept": "application/json", "Content-Type": "application/json"})

    verify = verify_ssl
    if verify_ssl and not cert:
        result = {
            "error": "No certificate path specified. Please specify certificate path in cert parameter"
        }
        return result

    if verify_ssl:
        verify = cert

    if cert_common_name and verify_ssl:
        session.mount("https://", HostHeaderSSLAdapter())
        headers["Host"] = cert_common_name

    try:
        response = session.post(
            url=url,
            auth=(username, password),
            data=json.dumps(data),
            verify=verify,
            headers=headers,
        )
        # raise error if any
        response.raise_for_status()
    except HTTPError as e:
        log.error(e)
        result = {
            "error": "Error occurred while deleting the license. Please check logs for more details."
        }
        # if response contains json, extract error message from it
        if e.response.text:
            log.error("Response from NSX Manager {}".format(e.response.text))
            try:
                error_json = e.response.json()
                if error_json["error_message"]:
                    result["error"] = e.response.json()["error_message"]
            except ValueError:
                log.error(
                    "Couldn't parse the response as json. Returning response text as error message"
                )
                result["error"] = e.response.text

        return result
    except SSLError as se:
        log.error(se)
        result = {
            "error": "SSL Error occurred while deleting the license."
            "Please check if the certificate is valid and hostname matches certificate common name."
        }
        return result
    except RequestException as re:
        log.error(re)
        result = {
            "error": "Error occurred while deleting license. Please check logs for more details."
        }
        return result
    success_result = {"message": "License deleted successfully"}
    return success_result
