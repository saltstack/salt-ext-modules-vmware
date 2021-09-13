"""
    VMC vCenter API Request Module
"""
import logging

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from requests.exceptions import RequestException
from requests.exceptions import SSLError
from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request

log = logging.getLogger(__name__)


def get_api_session_id(hostname, username, password):
    """
    This function returns api_session_id required to perform operations for VMC vCenter.

    hostname
        Hostname of the vCenter console

    username
        username required to login to vCenter console

    password
        password required to login to vCenter console

    """
    url = vmc_request.set_base_url(hostname) + vmc_constants.VCENTER_API_SESSION_URL
    headers = {vmc_constants.CONTENT_TYPE: vmc_constants.APPLICATION_JSON}
    response = requests.post(url, headers=headers, auth=HTTPBasicAuth(username, password))
    return response.json()


def get_headers(hostname, username, password):
    """
    This function returns HTTP headers required to perform operations for VMC vCenter.

    hostname
        Hostname of the vCenter console

    username
        username required to login to vCenter console

    password
        password required to login to vCenter console

    """
    api_session_id = get_api_session_id(hostname, username, password)
    return {
        vmc_constants.CONTENT_TYPE: vmc_constants.APPLICATION_JSON,
        vmc_constants.VMWARE_API_SESSION_ID: api_session_id,
    }


def call_api(
    method,
    url,
    headers,
    description,
    responsebody_applicable=True,
    verify_ssl=True,
    cert=None,
    data=None,
    params=None,
):
    """
    This function is used to make the http requests for the given operation on vCenter and return its response

    method
        http request method : post, get, patch, put and delete

    url
        url to perform the operation

    headers
        headers required to perform the given operation

    description
        indicates the operation for which this function gets called. <module>.<function_name>

    responsebody_applicable
        boolean value which indicates if the requested api returns response body or not. Enabled by Default.

    verify_ssl
        Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        Path to the SSL certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    data
        payload required for post and patch operations.

    params
        query params required to perform the given operation.

    """

    session = requests.Session()
    verify = verify_ssl
    if verify_ssl:
        if cert:
            verify = cert
        else:
            return {vmc_constants.ERROR: vmc_constants.NO_CERTIFICATE_ERROR_MSG}

    try:
        response = session.request(
            method=method, url=url, headers=headers, verify=verify, json=data, params=params
        )

        log.info("Response status code: %s for: %s", response.status_code, description)
        # raise error for any client/server HTTP Error codes
        response.raise_for_status()

        if not responsebody_applicable:
            return {"description": description, "result": "success"}
        return response.json()

    except HTTPError as e:
        log.error(e)
        result = {vmc_constants.ERROR: vmc_constants.HTTP_ERROR_MSG.format(url, description)}
        # if response contains json, extract error message from it
        if e.response.text:
            log.error("Response from VMC vCenter %s for %s", e.response.text, description)
            try:
                error_json = e.response.json()
                result[vmc_constants.ERROR] = error_json
            except ValueError:
                log.error(vmc_constants.PARSE_ERROR_MSG)
                result[vmc_constants.ERROR] = e.response.text
        return result
    except SSLError as se:
        log.error(se)
        result = {vmc_constants.ERROR: vmc_constants.SSL_ERROR_MSG.format(url, description)}
        return result
    except RequestException as re:
        log.error(re)
        result = {vmc_constants.ERROR: vmc_constants.REQUEST_EXCEPTION_MSG.format(url, description)}
        return result
