# -*- coding: utf-8 -*-
"""
Salt Module to manage VMware NSX-T configuration

"""
from __future__ import absolute_import, print_function, unicode_literals

import json
import logging
import requests

from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError, SSLError, RequestException

from saltext.vmware.modules.ssl_adapter import HostHeaderSSLAdapter

log = logging.getLogger(__name__)

__virtual_name__ = "nsxt_manager"


def __virtual__():
    return __virtual_name__


def _get_base_url():
    return "https://{}/api/v1/configs/management"


def set_manager_config(
        hostname,
        publish_fqdns,
        revision,
        username,
        password,
        **kwargs
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
        Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.
    """

    log.info("Configuration's current Revision: %s", revision)

    req_data = {
        "publish_fqdns": publish_fqdns,
        "_revision": revision
    }

    msg = "Setting value of publish_fqdns to {}".format(publish_fqdns)
    log.debug(msg)

    session = requests.Session()
    headers = dict({"Accept": "application/json", "content-Type": "application/json"})
    cert_common_name = kwargs.get("cert_common_name")
    verify_ssl = bool(kwargs.get("verify_ssl", True))
    cert = kwargs.get("cert")

    if cert_common_name and verify_ssl:
        session.mount("https://", HostHeaderSSLAdapter())
        headers['Host'] = cert_common_name

    url = _get_base_url().format(hostname)

    try:
        if verify_ssl and not cert:
            return {"error": "No certificate path specified. Please specify certificate path in cert parameter"}
        elif not verify_ssl:
            cert = False

        response = session.put(url=url,
                               data=json.dumps(req_data),
                               headers=headers,
                               auth=HTTPBasicAuth(username, password),
                               verify=cert)

        # raise error for any client/server HTTP Error codes
        response.raise_for_status()

    except HTTPError as e:
        log.error(e)
        result = {"error": "Error occurred while updating the NSX-T configuration. Please check logs for more details."}
        # if response contains json, extract error message from it
        if e.response.text:
            log.error("Response from NSX-T Manager {}".format(e.response.text))
            try:
                error_json = e.response.json()
                if error_json['error_message']:
                    result["error"] = e.response.json()['error_message']
            except ValueError:
                log.error("Couldn't parse the response as json. Returning response text as error message")
                result["error"] = e.response.text
        return result
    except SSLError as se:
        log.error(se)
        result = {
            "error": "SSL Error occurred while updating the NSX-T configuration."
                     "Please check if the certificate is valid and hostname matches certificate common name."}
        return result
    except RequestException as re:
        log.error(re)
        result = {"error": "Error occurred while updating the NSX-T configuration. Please check logs for more details."}
        return result

    log.info("Response status code: {}".format(response.status_code))
    return response.json()


def get_manager_config(
        hostname,
        username,
        password,
        **kwargs
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
        Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.

    """

    url = _get_base_url().format(hostname)

    session = requests.Session()
    headers = dict({"Accept": "application/json"})
    verify_ssl = bool(kwargs.get("verify_ssl", True))
    cert_common_name = kwargs.get("cert_common_name")
    cert = kwargs.get("cert")

    if cert_common_name and verify_ssl:
        session.mount("https://", HostHeaderSSLAdapter())
        headers['Host'] = cert_common_name

    try:
        if verify_ssl and not cert:
            return {"error": "No certificate path specified. Please specify certificate path in cert parameter"}
        elif not verify_ssl:
            cert = False

        response = session.get(url=url,
                               headers=headers,
                               auth=HTTPBasicAuth(username, password),
                               verify=cert)

        log.debug("Response status code: {}".format(response.status_code))
        response.raise_for_status()

    except HTTPError as e:
        log.error(e)
        result = {
            "error": "Error occurred while retrieving the NSX-T configuration. Please check logs for more details."}
        # if response contains json, extract error message from it
        if e.response.text:
            log.error("Response from NSX-T Manager {}".format(e.response.text))
            try:
                error_json = e.response.json()
                if error_json['error_message']:
                    result["error"] = e.response.json()['error_message']
            except ValueError:
                log.error("Couldn't parse the response as json. Returning response text as error message")
                result["error"] = e.response.text
        return result

    except SSLError as se:
        log.error(se)
        result = {
            "error": "SSL Error occurred while retrieving the NSX-T configuration."
                     "Please check if the certificate is valid and hostname matches certificate common name."}
        return result
    except RequestException as re:
        log.error(re)
        result = {
            "error": "Error occurred while retrieving the NSX-T configuration. Please check logs for more details."}
        return result

    log.info("Response status code: {}".format(response.status_code))
    return response.json()
