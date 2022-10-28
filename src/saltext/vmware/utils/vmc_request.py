"""
    VMC API Request Module
"""
import json
import logging
import os

import requests
from requests.exceptions import HTTPError
from requests.exceptions import RequestException
from requests.exceptions import SSLError
from saltext.vmware.utils import vmc_constants

log = logging.getLogger(__name__)


def set_base_url(url):
    """
    This function appends the https prefix to the given url
    """
    api_url_base = vmc_constants.HTTPS_URL_PREFIX + url + vmc_constants.URL_SUFFIX
    return api_url_base


def get_access_token(refresh_key, authorization_host):
    """
    This function returns access_token required to perform operations for VMC.

    refresh_key
        API Token of the user for VMC cloud console

    authorization_host
        Hostname of the VMC cloud console
    """

    url = set_base_url(authorization_host) + vmc_constants.CSP_AUTHORIZATION_URL
    params = {vmc_constants.REFRESH_TOKEN: refresh_key}
    headers = {vmc_constants.CONTENT_TYPE: vmc_constants.APPLICATION_URLENCODED}
    try:
        response = requests.post(url, data=params, headers=headers)
        response.raise_for_status()
        json_response = response.json()
        access_token = json_response[vmc_constants.ACCESS_TOKEN]
        return access_token
    except HTTPError as e:
        log.error("Failed to get access token %s , please check the refresh_key", e.response.text)
        raise e


def get_headers(refresh_key, authorization_host):
    """
    This function returns HTTP headers required to perform operations for VMC.

    refresh_key
        API Token of the user for VMC cloud console

    authorization_host
        Hostname of the VMC cloud console
    """
    access_token = get_access_token(refresh_key, authorization_host)
    return {vmc_constants.CSP_AUTH_TOKEN: access_token}


def get_params(kwargs, valid_params):
    """
    Filter valid_params from kwargs and return as dict
    """
    params = {}
    for field in valid_params:
        if field in kwargs:
            params[field] = kwargs.get(field)
    return params


def call_api(
    method,
    url,
    refresh_key,
    authorization_host,
    description,
    responsebody_applicable=True,
    verify_ssl=True,
    cert=None,
    data=None,
    params=None,
):
    """
    This function is used to make the http requests for the given operation on VMC and return its response

    method
        http request method : post, get, patch, put and delete

    url
        url to perform the operation

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    description
        indicates the operation for which this function gets called. <module>.<function_name>

    responsebody_applicable
        boolean value which indicates if the requested api returns response body or not

    verify_ssl
        Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        Path to the SSL certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.
    """
    verify = verify_ssl
    if verify_ssl:
        if cert:
            verify = cert
        else:
            return {vmc_constants.ERROR: vmc_constants.NO_CERTIFICATE_ERROR_MSG}

    try:
        headers = get_headers(refresh_key, authorization_host)
        session = requests.Session()
        response = session.request(
            method=method, url=url, headers=headers, params=params, verify=verify, json=data
        )

        log.info("Response status code: %s for: %s", response.status_code, description)
        # raise error for any client/server HTTP Error codes
        response.raise_for_status()

        if not responsebody_applicable:
            return {"description": description, "result": "success"}
        return response.json()

    except HTTPError as e:
        log.error(e)
        result = {
            vmc_constants.ERROR: vmc_constants.HTTP_ERROR_MSG.format(e.request.url, description)
        }
        # if response contains json, extract error message from it
        if e.response.text:
            log.error("Response from VMC %s for %s", e.response.text, description)
            try:
                error_json = e.response.json()
                if vmc_constants.ERROR_MSG in error_json:
                    result[vmc_constants.ERROR] = error_json[vmc_constants.ERROR_MSG]
                elif vmc_constants.ERROR_MSGS in error_json:
                    result[vmc_constants.ERROR] = error_json[vmc_constants.ERROR_MSGS]
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
        result = {
            vmc_constants.ERROR: vmc_constants.REQUEST_EXCEPTION_MSG.format(
                re.request.url, description
            )
        }
        return result


def create_payload_for_request(template_data, user_input_dict, existing_data=None):
    """
    This function creates the payload using the user provided input based on the respective template data
    and the existing data

    template_data
        dict which contains the data required for the resource(security rule, Nat rule, Network etc..)

    user_input_dict
        user provided data required for the resource(security rule, Nat rule, Network etc..)

    existing_data
        existing data for the resource(security rule, Nat rule, Network etc..)

    """
    template_data = template_data.copy()
    if existing_data:
        template_data.update(
            (k, existing_data[k]) for k in template_data.keys() & existing_data.keys()
        )

    template_data.update(user_input_dict)
    return template_data


def _filter_kwargs(allowed_kwargs, allow_none=[], default_dict=None, **kwargs):
    result = default_dict or {}
    for field in allowed_kwargs:
        val = kwargs.get(field)
        if val not in [None, vmc_constants.VMC_NONE]:
            result[field] = val
        if field in allow_none and val != vmc_constants.VMC_NONE:
            result[field] = val
    return result


def _filter_vmc_none(**kwargs):
    return {k: v for k, v in kwargs.items() if v != vmc_constants.VMC_NONE}
