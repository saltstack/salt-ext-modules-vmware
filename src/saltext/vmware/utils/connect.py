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


def get_config(config, profile=None, esxi_host=None):
    if profile:
        credentials = (config.get("saltext.vmware", {}) or config.get("vmware_config"))[profile]
    else:
        credentials = config.get("saltext.vmware") or config.get("vmware_config", {})

    if esxi_host:
        host = esxi_host
        credentials = credentials.get("esxi_host", {}).get(esxi_host)
        password = credentials.get("password")
        user = credentials.get("user")
    else:
        host = os.environ.get("SALTEXT_VMWARE_HOST") or credentials.get("host")
        password = os.environ.get("SALTEXT_VMWARE_PASSWORD") or credentials.get("password")
        user = os.environ.get("SALTEXT_VMWARE_USER") or credentials.get("user")

    return {"host": host, "user": user, "password": password}


def get_service_instance(config=None, esxi_host=None, profile=None):
    """
    Connect to VMware service instance

    config
        (optional) If specified, allows for a dictionary of data to be made
        available to pillar and ext_pillar rendering. These variables
        will also override any variables of the same name in pillar or
        ext_pillar.

    esxi_host
        (optional) If specified, retrieves the configured username and password for this host.

    profile
        Profile to use (optional)

    Pillar Example:

    .. code-block:: yaml

        saltext.vmware:
            host: 198.51.100.100
            password: CorrectHorseBatteryStaple
            user: admin@example.com
            esxi_host:
                198.52.100.105:
                    user: admin
                    password: CorrectHorseBatteryStaple
                198.52.100.106:
                    user: admin
                    password: CorrectHorseBatteryStaple

    If configuration for multiple VMware services instances is required, they can be
    set up as different configuration profiles:

    .. code-block:: yaml

        saltext.vmware:
          profile1:
            host: 198.51.100.100
            password: CorrectHorseBatteryStaple
            user: admin@example.com
          profile2:
            host: 198.51.100.100
            password: CorrectHorseBatteryStaple
            user: admin@example.com
            esxi_host:
              198.52.100.105:
                user: admin
                password: CorrectHorseBatteryStaple
              198.52.100.106:
                user: admin
                password: CorrectHorseBatteryStaple

    """
    ctx = ssl._create_unverified_context()
    config = config or {}

    config = get_config(config=config, profile=profile, esxi_host=esxi_host)

    if config["host"] is None or config["password"] is None or config["user"] is None:
        raise ValueError("Cannot create service instance, VMware credentials incomplete.")

    service_instance = connect.SmartConnect(
        host=config.get("host"),
        user=config.get("user"),
        pwd=config.get("password"),
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
        os.environ.get("SALTEXT_VMWARE_REST_API_HOST")
        or opts.get("saltext.vmware", {}).get("rest_api_host")
        or pillar.get("saltext.vmware", {}).get("rest_api_host")
        or os.environ.get("SALTEXT_VMWARE_HOST")
        or opts.get("saltext.vmware", {}).get("host")
        or pillar.get("saltext.vmware", {}).get("host")
    )
    cert = (
        os.environ.get("SALTEXT_VMWARE_REST_API_CERT")
        or opts.get("saltext.vmware", {}).get("rest_api_cert")
        or pillar.get("saltext.vmware", {}).get("rest_api_cert")
    )
    if not cert:
        cert = False
    if token is None:
        user = (
            os.environ.get("SALTEXT_VMWARE_REST_API_USER")
            or opts.get("saltext.vmware", {}).get("rest_api_user")
            or pillar.get("saltext.vmware", {}).get("rest_api_user")
            or os.environ.get("SALTEXT_VMWARE_USER")
            or opts.get("saltext.vmware", {}).get("user")
            or pillar.get("saltext.vmware", {}).get("user")
        )
        password = (
            os.environ.get("SALTEXT_VMWARE_REST_API_PASSWORD")
            or opts.get("saltext.vmware", {}).get("rest_api_password")
            or pillar.get("saltext.vmware", {}).get("rest_api_password")
            or os.environ.get("SALTEXT_VMWARE_PASSWORD")
            or opts.get("saltext.vmware", {}).get("password")
            or pillar.get("saltext.vmware", {}).get("password")
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
