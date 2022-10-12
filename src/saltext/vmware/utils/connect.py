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
    conf = (
        config.get("saltext.vmware")
        or config.get("grains", {}).get("saltext.vmware")
        or config.get("pillar", {}).get("saltext.vmware")
        or {}
    )
    if not conf:
        conf = (
            config.get("vmware_config")
            or config.get("grains", {}).get("vmware_config")
            or config.get("pillar", {}).get("vmware_config")
            or {}
        )
        if conf:
            log.warning(
                "Config found under vmware_config and not saltext.vmware. vmware_config has been deprecated and will be removed in 2023"
            )
    if profile:
        credentials = conf[profile]
    else:
        credentials = conf

    if esxi_host:
        host = esxi_host
        credentials = credentials.get("esxi_host", {}).get(esxi_host)
        password = credentials.get("password")
        user = credentials.get("user")
    else:
        host = os.environ.get("SALTEXT_VMWARE_HOST") or credentials.get("host")
        password = os.environ.get("SALTEXT_VMWARE_PASSWORD") or credentials.get("password")
        user = os.environ.get("SALTEXT_VMWARE_USER") or credentials.get("user")

    if host is None or password is None or user is None:
        raise ValueError("Cannot create service instance, VMware credentials incomplete.")
    return {"host": host, "user": user, "password": password}


def get_service_instance(*, config, esxi_host=None, profile=None):
    """
    Connect to VMware service instance.

    config
        The config to use to search for connection information. The search
        order matches that found in Salt's `config.get
        <https://docs.saltproject.io/en/latest/ref/modules/all/salt.modules.config.html#salt.modules.config.get>_`.
        Specifically the order is:

            1. Environment variables
            2. Minion config
            3. Minion grains
            4. Minion pillar data

        Environment variables are:
            SALTEXT_VMWARE_HOST
            SALTEXT_VMWARE_PASSWORD
            SALTEXT_VMWARE_USER
            SALTEXT_VMWARE_ESXI_USER
            SALTEXT_VMWARE_ESXI_PASSWORD

    esxi_host
        (optional) If specified, retrieves the configured username and password for the ESXi host.

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
    # TODO: request needs test coverage -W. Werner, 2022-09-30
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
