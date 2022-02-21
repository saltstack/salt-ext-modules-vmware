"""
    Integration Tests for nsxt_manager execution module
"""
import pytest
from saltext.vmware.utils import nsxt_request

BASE_URL = "https://{}/api/v1/configs/management"


def _get_manager_config_from_nsxt_api(hostname, username, password):
    response_json = nsxt_request.call_api(
        method="GET",
        url=BASE_URL.format(hostname),
        username=username,
        password=password,
        verify_ssl=False,
    )

    assert "error" not in response_json
    return response_json


@pytest.mark.xfail(reason="nsxt tests not working yet")
def test_nsxt_manager_get_and_set_manager_config(nsxt_config, salt_call_cli):
    """
    nsxt_manager.get_manager_config
    nsxt_manager.set_manager_config
    """
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    response_json = _get_manager_config_from_nsxt_api(hostname, username, password)

    get_response_json = salt_call_cli.run(
        "nsxt_manager.get_manager_config",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
    ).json

    assert response_json == get_response_json

    publish_fqdn_json = salt_call_cli.run(
        "nsxt_manager.set_manager_config",
        hostname=hostname,
        username=username,
        password=password,
        publish_fqdns=response_json["publish_fqdns"],
        revision=response_json["_revision"],
        verify_ssl=False,
    ).json

    response_json = _get_manager_config_from_nsxt_api(hostname, username, password)

    assert response_json == publish_fqdn_json
