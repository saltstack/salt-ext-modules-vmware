import time

import pytest
import requests


@pytest.fixture
def delete_compute_manager(nsxt_config):
    """
    Sets up test requirements:
    Queries nsx api for compute manager 10.206.243.180
    Deletes compute manager if exists
    """
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    cert = nsxt_config.get("cert", False)
    compute_manager_server = nsxt_config["compute_manager_server"]

    url = "https://{management_host}/api/v1/fabric/compute-managers".format(
        management_host=hostname
    )
    response = requests.get(url=url, auth=(username, password), verify=cert)
    response.raise_for_status()
    compute_managers_list = response.json()
    compute_manager_id_to_delete = None
    if compute_managers_list["result_count"] <= 0:
        return
    else:
        for compute_manager in compute_managers_list["results"]:
            if compute_manager["server"] == compute_manager_server:
                compute_manager_id_to_delete = compute_manager["id"]
    if compute_manager_id_to_delete is not None:
        url = "https://{management_host}/api/v1/fabric/compute-managers/{id}".format(
            management_host=hostname, id=compute_manager_id_to_delete
        )
        response = requests.delete(url=url, auth=(username, password), verify=cert)
        response.raise_for_status()


def test_get(nsxt_config, salt_call_cli):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]

    ret = salt_call_cli.run(
        "nsxt_compute_manager.get",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
    )
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json["result_count"] >= 0


def test_register_update_and_remove(nsxt_config, salt_call_cli, delete_compute_manager):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    compute_manager_server = nsxt_config["compute_manager_server"]
    credential = nsxt_config["credential"]

    time.sleep(30)
    # Register a compute manager
    ret = salt_call_cli.run(
        "nsxt_compute_manager.register",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        compute_manager_server=compute_manager_server,
        credential=credential,
    )
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json["server"] == compute_manager_server
    assert result_as_json["credential"]["thumbprint"] == credential["thumbprint"]
    assert result_as_json["origin_type"] == "vCenter"
    assert result_as_json["description"] == ""
    _compute_manager_id = result_as_json["id"]
    _compute_manager_revision = result_as_json["_revision"]
    # Update existing compute manager
    time.sleep(30)
    ret = salt_call_cli.run(
        "nsxt_compute_manager.update",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        compute_manager_server=compute_manager_server,
        credential=credential,
        compute_manager_revision=_compute_manager_revision,
        compute_manager_id=_compute_manager_id,
        display_name="updated display name",
        description="updated description",
    )
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json["server"] == compute_manager_server
    assert result_as_json["credential"]["thumbprint"] == credential["thumbprint"]
    assert result_as_json["origin_type"] == "vCenter"
    assert result_as_json["description"] == "updated description"
    assert result_as_json["display_name"] == "updated display name"
    assert result_as_json["_revision"] == _compute_manager_revision + 1
    # De-register compute manager
    time.sleep(20)
    ret = salt_call_cli.run(
        "nsxt_compute_manager.remove",
        hostname=hostname,
        username=username,
        password=password,
        compute_manager_id=_compute_manager_id,
        verify_ssl=False,
    ).json
    assert ret is not None
    assert ret["message"] == "Removed compute manager successfully"
