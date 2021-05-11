"""
    NSX-T API Request Module
"""
import json
import logging

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from requests.exceptions import RequestException
from requests.exceptions import SSLError
from saltext.vmware.modules.ssl_adapter import HostHeaderSSLAdapter

log = logging.getLogger(__name__)


def call_api(
    method,
    url,
    username,
    password,
    cert_common_name=None,
    verify_ssl=True,
    cert=None,
    data=None,
    params=None,
):
    headers = {"Accept": "application/json", "content-Type": "application/json"}
    session = requests.Session()

    if cert_common_name and verify_ssl:
        session.mount("https://", HostHeaderSSLAdapter())
        headers["Host"] = cert_common_name

    verify = verify_ssl
    if verify_ssl:
        if cert:
            verify = cert
        else:
            result = {
                "error": "No certificate path specified. Please specify certificate path in cert parameter"
            }
            return result

    try:
        response = session.request(
            method=method,
            url=url,
            headers=headers,
            auth=HTTPBasicAuth(username, password),
            verify=verify,
            params=params,
            data=json.dumps(data),
        )
        log.info("Response status code: {}".format(response.status_code))
        # raise error for any client/server HTTP Error codes
        response.raise_for_status()

        if not response.text:
            return None
        return response.json()

    except HTTPError as e:
        log.error(e)
        result = {
            "error": "Error occurred while calling NSX-T API {}. Please check logs for more details.".format(
                url
            )
        }
        # if response contains json, extract error message from it
        if e.response.text:
            log.error("Response from NSX-T Manager %s", e.response.text)
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
            "error": "SSL Error occurred while calling NSX-T API {}."
            "Please check if the certificate is valid and hostname matches certificate common name.".format(
                url
            )
        }
        return result
    except RequestException as re:
        log.error(re)
        result = {
            "error": "Error occurred while calling NSX-T API {}. Please check logs for more details.".format(
                url
            )
        }
        return result
