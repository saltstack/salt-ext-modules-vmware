# SPDX-License-Identifier: Apache-2.0
import json
import logging
import os
import ssl

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from requests.exceptions import RequestException
from requests.exceptions import SSLError

# pylint: disable=no-name-in-module
try:
    from pyVim import connect
    from pyVim.connect import GetSi, SmartConnect, Disconnect, GetStub, SoapStubAdapter
    from pyVmomi import vim, vmodl, VmomiSupport

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False

log = logging.getLogger(__name__)


def get_username_password(esxi_host, opts=None, pillar=None):
    password = (
        pillar.get("vmware_config", {}).get("esxi_host", {}).get(esxi_host, {}).get("password")
        or opts.get("vmware_config", {}).get("esxi_host", {}).get(esxi_host, {}).get("password")
        or os.environ.get("VMWARE_CONFIG_PASSWORD")
        or opts.get("vmware_config", {}).get("password")
        or pillar.get("vmware_config", {}).get("password")
    )
    user = (
        pillar.get("vmware_config", {}).get("esxi_host", {}).get(esxi_host, {}).get("user")
        or opts.get("vmware_config", {}).get("esxi_host", {}).get(esxi_host, {}).get("user")
        or os.environ.get("VMWARE_CONFIG_USER")
        or opts.get("vmware_config", {}).get("user")
        or pillar.get("vmware_config", {}).get("user")
    )
    return user, password


def get_service_instance(opts=None, pillar=None, esxi_host=None):
    """
    Connect to VMware service instance

    opts
        (optional) Any additional options.

    pillar
        (optional) If specified, allows for a dictionary of pillar data to be made
        available to pillar and ext_pillar rendering. These pillar variables
        will also override any variables of the same name in pillar or
        ext_pillar.

    esxi_host
        (optional) If specified, retrieves the configured username and password for this host.

    Pillar Example:

    .. code-block::

        vmware_config:
            host: 198.51.100.100
            password: ****
            user: @example.com

        vmware_config:
            host: 198.51.100.100
            password: ****
            user: @example.com
            esxi_host:
                198.52.100.105:
                    user: admin
                    password: ***
                198.52.100.106:
                    user: admin
                    password: ***

    """
    ctx = ssl._create_unverified_context()
    opts = opts or {}
    pillar = pillar or {}
    host = (
        esxi_host
        or os.environ.get("VMWARE_CONFIG_HOST")
        or opts.get("vmware_config", {}).get("host")
        or pillar.get("vmware_config", {}).get("host")
    )
    user, password = get_username_password(esxi_host=host, opts=opts, pillar=pillar)
    config = {
        "host": host,
        "password": password,
        "user": user,
    }
    service_instance = connect.SmartConnect(
        host=config["host"],
        user=config["user"],
        pwd=config["password"],
        sslContext=ctx,
    )
    return service_instance


def request(url, method, body=None, token=None, opts=None, pillar=None):
    """
    Make a request to VMware rest api

    url
        url address for request.

    method
        Method for api request.

    body
        Body of the api request.

    token
        (optional) Api session token for api access, will create new token if not passed.

    opts
        (optional) Any additional options.

    pillar
        (optional) If specified, allows for a dictionary of pillar data to be made
        available to pillar and ext_pillar rendering. These pillar variables
        will also override any variables of the same name in pillar or
        ext_pillar.
    """
    host = (
        os.environ.get("VMWARE_CONFIG_REST_API_HOST")
        or opts.get("vmware_config", {}).get("rest_api_host")
        or pillar.get("vmware_config", {}).get("rest_api_host")
        or os.environ.get("VMWARE_CONFIG_HOST")
        or opts.get("vmware_config", {}).get("host")
        or pillar.get("vmware_config", {}).get("host")
    )
    cert = (
        os.environ.get("VMWARE_CONFIG_REST_API_CERT")
        or opts.get("vmware_config", {}).get("rest_api_cert")
        or pillar.get("vmware_config", {}).get("rest_api_cert")
    )
    if not cert:
        cert = False
    if token is None:
        user = (
            os.environ.get("VMWARE_CONFIG_REST_API_USER")
            or opts.get("vmware_config", {}).get("rest_api_user")
            or pillar.get("vmware_config", {}).get("rest_api_user")
            or os.environ.get("VMWARE_CONFIG_USER")
            or opts.get("vmware_config", {}).get("user")
            or pillar.get("vmware_config", {}).get("user")
        )
        password = (
            os.environ.get("VMWARE_CONFIG_REST_API_PASSWORD")
            or opts.get("vmware_config", {}).get("rest_api_password")
            or pillar.get("vmware_config", {}).get("rest_api_password")
            or os.environ.get("VMWARE_CONFIG_PASSWORD")
            or opts.get("vmware_config", {}).get("password")
            or pillar.get("vmware_config", {}).get("password")
        )
        token = _get_session(host, user, password, cert)
    headers = {
        "Accept": "application/json",
        "content-Type": "application/json",
        "vmware-api-session-id": token,
    }
    session = requests.Session()
    response = session.request(
        method=method,
        url=f"https://{host}{url}",
        headers=headers,
        verify=cert,
        params=None,
        data=json.dumps(body),
    )
    return {"response": response, "token": token}


def _get_session(host, user, password, cert):
    """
    Create REST API session

    host
        Host for api request.

    user
        User to create session token for subsequent requests.

    password
        Password to create session token for subsequent requests.

    cert
        certificate for ssl verification.
    """
    headers = {"Accept": "application/json", "content-Type": "application/json"}
    session = requests.Session()
    if not cert:
        cert = False
    try:
        response = session.request(
            method="POST",
            url=f"https://{host}/rest/com/vmware/cis/session",
            headers=headers,
            auth=HTTPBasicAuth(user, password),
            verify=cert,
            params=None,
            data=json.dumps(None),
        )
        response.raise_for_status()
        json_response = response.json()
        return json_response["value"]

    except HTTPError as e:
        log.error(e)
        result = {"error": "Error occurred while calling vCenter API."}
        # if response contains json, extract error message from it
        if e.response.text:
            log.error(f"Response from vCenter {e.response.text}")
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
        result = {"error": "SSL Error occurred while calling vCenter API."}
        return result
    except RequestException as re:
        log.error(re)
        result = {"error": "Error occurred while calling vCenter API."}
        return result
