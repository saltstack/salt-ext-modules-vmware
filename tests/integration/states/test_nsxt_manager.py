"""
    Integration Tests for nsxt_manager state module
"""
import logging

import pytest
import requests
from requests.auth import HTTPBasicAuth

log = logging.getLogger(__name__)

BASE_URL = "https://{}/api/v1/configs/management"


def _get_manager_config_from_nsxt(nsxt_config):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    cert = nsxt_config.get("cert", False)

    return requests.get(
        url=BASE_URL.format(hostname), auth=HTTPBasicAuth(username, password), verify=cert
    ).json()


def _set_manager_config_to_nsxt(nsxt_config, data):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    cert = nsxt_config.get("cert", False)

    return requests.put(
        url=BASE_URL.format(hostname),
        auth=HTTPBasicAuth(username, password),
        verify=cert,
        data=data,
        headers={"content-type": "application/json"},
    ).json()


@pytest.fixture
def publish_fqdns(nsxt_config):
    # get current config
    current_manager_config = _get_manager_config_from_nsxt(nsxt_config)
    publish_fqdns = current_manager_config["publish_fqdns"]
    log.info("Initial publish_fqdns value %s", publish_fqdns)

    # yield the current publish_fqdns
    yield publish_fqdns

    # get current config for latest revision number after tests ran
    current_manager_config = _get_manager_config_from_nsxt(nsxt_config)
    current_manager_config["publish_fqdns"] = publish_fqdns

    log.info("Final publish_fqdns value %s", publish_fqdns)
    # restore the config state to original
    _set_manager_config_to_nsxt(nsxt_config, current_manager_config)


def test_nsxt_manager(nsxt_config, salt_call_cli, publish_fqdns):
    """
    Tests NSX-T Manager State module to verify publish_fqdns_enabled/publish_fqdns_disabled
    when it is enabled/disabled in NSX-T Manager
    """
    if bool(publish_fqdns):
        changes, comment = _execute_publish_fqdns_enabled(nsxt_config, salt_call_cli)
        assert not changes
        assert comment == "publish_fqdns is already set to True"

        changes, comment = _execute_publish_fqdns_disabled(nsxt_config, salt_call_cli)
        assert dict(changes)["new"]["publish_fqdns"] is False
        assert dict(changes)["old"]["publish_fqdns"] is True
        assert comment == "publish_fqdns has been set to False"

        changes, comment = _execute_publish_fqdns_disabled(nsxt_config, salt_call_cli)
        assert not changes
        assert comment == "publish_fqdns is already set to False"

        changes, comment = _execute_publish_fqdns_enabled(nsxt_config, salt_call_cli)
        assert dict(changes)["new"]["publish_fqdns"] is True
        assert dict(changes)["old"]["publish_fqdns"] is False
        assert comment == "publish_fqdns has been set to True"
    else:
        changes, comment = _execute_publish_fqdns_disabled(nsxt_config, salt_call_cli)
        assert not changes
        assert comment == "publish_fqdns is already set to False"

        changes, comment = _execute_publish_fqdns_enabled(nsxt_config, salt_call_cli)
        assert dict(changes)["new"]["publish_fqdns"] is True
        assert dict(changes)["old"]["publish_fqdns"] is False
        assert comment == "publish_fqdns has been set to True"

        changes, comment = _execute_publish_fqdns_enabled(nsxt_config, salt_call_cli)
        assert not changes
        assert comment == "publish_fqdns is already set to True"

        changes, comment = _execute_publish_fqdns_disabled(nsxt_config, salt_call_cli)
        assert dict(changes)["new"]["publish_fqdns"] is False
        assert dict(changes)["old"]["publish_fqdns"] is True
        assert comment == "publish_fqdns has been set to False"


def _execute_publish_fqdns_enabled(nsxt_config, salt_call_cli):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]

    response = salt_call_cli.run(
        "state.single",
        "nsxt_manager.publish_fqdns_enabled",
        name="publish_fqdns_enabled",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
    ).json

    result = dict(list(response.values())[0])
    return result.get("changes"), result.get("comment")


def _execute_publish_fqdns_disabled(nsxt_config, salt_call_cli):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]

    response = salt_call_cli.run(
        "state.single",
        "nsxt_manager.publish_fqdns_disabled",
        name="publish_fqdns_disabled",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
    ).json

    result = dict(list(response.values())[0])
    return result.get("changes"), result.get("comment")
