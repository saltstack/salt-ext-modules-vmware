import pytest
import requests

_hostname = ""
_username = ""
_password = ""


@pytest.fixture(autouse=True)
def setup(nsxt_config):
    """
    This is called once for module
    It loads global values from config section
    """
    globals().update(nsxt_config)


@pytest.fixture
def delete_transport_zone():
    url = f"https://{_hostname}/api/v1/transport-zones"
    session = requests.Session()
    headers = dict({"Accept": "application/json", "Content-Type": "application/json"})
    verify_ssl = False

    transport_zone_id, transport_zone_dict = None, None

    response = session.get(url=url, auth=(_username, _password), verify=verify_ssl, headers=headers)

    response.raise_for_status()
    transport_zone_dict = response.json()

    if transport_zone_dict["result_count"] != 0:
        results = transport_zone_dict["results"]
        for result in results:
            if result["display_name"] == "Test_Create_Transport_Zone-IT":
                transport_zone_id = result["id"]
                return

    response = session.delete(
        url=url + "/%s" % transport_zone_id,
        auth=(_username, _password),
        verify=False,
        headers=headers,
    )

    response.raise_for_status()


@pytest.mark.xfail(reason="nsxt tests not working yet")
def test_check_transport_zone(nsxt_config, salt_call_cli):
    ret_create = salt_call_cli.run(
        "nsxt_transport_zone.create",
        hostname=nsxt_config["hostname"],
        username=nsxt_config["username"],
        password=nsxt_config["password"],
        host_switch_name="nsxDefaultHostSwitch",
        transport_type="OVERLAY",
        display_name="Test_Create_Transport_Zone-IT",
        verify_ssl=False,
    )

    assert ret_create is not None
    result_as_json_create = ret_create.json
    assert result_as_json_create["display_name"] == "Test_Create_Transport_Zone-IT"

    ret_update = salt_call_cli.run(
        "nsxt_transport_zone.update",
        hostname=nsxt_config["hostname"],
        username=nsxt_config["username"],
        password=nsxt_config["password"],
        transport_zone_id=result_as_json_create["id"],
        transport_type="OVERLAY",
        revision=result_as_json_create["_revision"],
        description="Edit description from IT",
        verify_ssl=False,
    )

    assert ret_update is not None
    result_as_json_update = ret_update.json
    assert result_as_json_update["description"] == "Edit description from IT"

    ret_delete = salt_call_cli.run(
        "nsxt_transport_zone.delete",
        hostname=nsxt_config["hostname"],
        username=nsxt_config["username"],
        password=nsxt_config["password"],
        transport_zone_id=result_as_json_create["id"],
        verify_ssl=False,
    )

    result_as_json_delete = ret_delete.json
    assert result_as_json_delete["message"] == "Deleted transport zone successfully"

    ret_get = salt_call_cli.run(
        "nsxt_transport_zone.get_by_display_name",
        hostname=nsxt_config["hostname"],
        username=nsxt_config["username"],
        password=nsxt_config["password"],
        display_name="Test_Create_Transport_Zone-IT",
        verify_ssl=False,
    )

    ret_result_as_json = ret_get.json
    assert len(ret_result_as_json["results"]) == 0
