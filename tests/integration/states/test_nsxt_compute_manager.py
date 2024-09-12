import time

import pytest
import requests

BASE_URL = "https://{management_host}/api/v1/fabric/compute-managers"


@pytest.fixture
def delete_compute_manager(nsxt_config):
    """
    Sets up test requirements:
    Queries nsx api for compute manager {compute_manager_server}
    Deletes compute manager if exists
    """
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    cert = nsxt_config.get("cert", False)

    compute_manager_server = nsxt_config["compute_manager_server"]

    url = BASE_URL.format(management_host=hostname)
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

        url = (url + "/{id}").format(management_host=hostname, id=compute_manager_id_to_delete)
        response = requests.delete(url=url, auth=(username, password), verify=cert)
        response.raise_for_status()


@pytest.mark.xfail(reason="nsxt tests not working yet")
def test_register_update_and_delete(nsxt_config, salt_call_cli, delete_compute_manager):
    # Register a compute manager
    # Sleep for 30sec as deletion of compute manager might happen during delete_compute_manager fixture run
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    compute_manager_server = nsxt_config["compute_manager_server"]
    credential = nsxt_config["credential"]

    time.sleep(30)
    ret = salt_call_cli.run(
        "state.single",
        "nsxt_compute_manager.present",
        name="compute manager registration",
        hostname=hostname,
        username=username,
        password=password,
        compute_manager_server=compute_manager_server,
        display_name="Compute_Manager_from_IT",
        credential=credential,
        description="compute manager registered by IT",
        verify_ssl=False,
    ).json
    assert ret is not None
    result_as_json = ret[list(ret.keys())[0]]
    assert result_as_json["name"] == "compute manager registration"
    assert result_as_json["result"] is True
    assert (
        result_as_json["comment"]
        == f"Compute manager {compute_manager_server} successfully registered with NSX-T"
    )
    new_changes_json = result_as_json["changes"]["new"]
    assert new_changes_json["server"] == compute_manager_server
    assert new_changes_json["description"] == "compute manager registered by IT"
    # Update existing compute manager
    time.sleep(30)

    ret = salt_call_cli.run(
        "state.single",
        "nsxt_compute_manager.present",
        name="compute manager registration",
        hostname=hostname,
        username=username,
        password=password,
        compute_manager_server=compute_manager_server,
        credential=credential,
        display_name="Updated display name",
        description="compute manager registration updated by IT",
        verify_ssl=False,
    ).json
    assert ret is not None
    result_as_json = ret[list(ret.keys())[0]]
    assert result_as_json["name"] == "compute manager registration"
    assert result_as_json["result"] is True
    assert result_as_json[
        "comment"
    ] == "Compute manager {} registration successfully updated with NSX-T".format(
        compute_manager_server
    )
    new_changes_json = result_as_json["changes"]["new"]
    assert new_changes_json["server"] == compute_manager_server
    assert new_changes_json["description"] == "compute manager registration updated by IT"
    assert new_changes_json["display_name"] == "Updated display name"

    old_changes_json = result_as_json["changes"]["old"]
    assert old_changes_json["description"] == "compute manager registered by IT"

    # De-register compute manager
    time.sleep(20)
    ret = salt_call_cli.run(
        "state.single",
        "nsxt_compute_manager.absent",
        name="De-registration",
        hostname=hostname,
        username=username,
        password=password,
        compute_manager_server=compute_manager_server,
        verify_ssl=False,
    ).json
    assert ret is not None
    result_as_json = ret[list(ret.keys())[0]]
    assert (
        result_as_json["comment"]
        == "Compute manager registration removed successfully from NSX-T manager"
    )
    assert result_as_json["name"] == "De-registration"
    assert result_as_json["result"]
