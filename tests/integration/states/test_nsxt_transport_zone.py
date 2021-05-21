import json
import logging

log = logging.getLogger(__name__)

_display_name = "Check-State-Module-Create"
_description = "Creation of the transport zone"
_description_update = "Updating the description of the transport zone"


def test_state_transport_zone_verify(nsxt_config, salt_call_cli):
    response_create = salt_call_cli.run(
        "state.single",
        "nsxt_transport_zone.present",
        name="create transport zone",
        hostname=nsxt_config["hostname"],
        username=nsxt_config["username"],
        password=nsxt_config["password"],
        host_switch_name="nsxDefaultHostSwitch",
        transport_type="OVERLAY",
        verify_ssl=False,
        display_name=_display_name,
        description=_description,
    )

    result_create = dict(list(response_create.json.values())[0])["result"]
    comment_create = dict(list(response_create.json.values())[0])["comment"]
    display_name_response = json.loads(
        dict(dict(list(response_create.json.values())[0])["changes"])["new"]
    )["display_name"]
    description_create = json.loads(
        dict(dict(list(response_create.json.values())[0])["changes"])["new"]
    )["description"]

    assert result_create is True
    assert display_name_response == _display_name
    assert comment_create == "Transport Zone created successfully"
    assert description_create == _description

    response_update = salt_call_cli.run(
        "state.single",
        "nsxt_transport_zone.present",
        name="update transport zone",
        hostname=nsxt_config["hostname"],
        username=nsxt_config["username"],
        password=nsxt_config["password"],
        transport_type="OVERLAY",
        host_switch_name="nsxDefaultHostSwitch",
        verify_ssl=False,
        display_name=_display_name,
        description=_description_update,
    )

    result_update = dict(list(response_update.json.values())[0])["result"]
    comment_update = dict(list(response_update.json.values())[0])["comment"]
    description_update = json.loads(
        dict(dict(list(response_update.json.values())[0])["changes"])["new"]
    )["description"]

    assert result_update is True
    assert comment_update == "Transport Zone updated successfully"
    assert description_update == _description_update

    response_delete = salt_call_cli.run(
        "state.single",
        "nsxt_transport_zone.absent",
        name="delete transport zone",
        hostname=nsxt_config["hostname"],
        username=nsxt_config["username"],
        password=nsxt_config["password"],
        verify_ssl=False,
        display_name=_display_name,
    )

    result_delete = dict(list(response_delete.json.values())[0])["result"]
    comment_delete = dict(list(response_delete.json.values())[0])["comment"]

    assert result_delete is True
    assert comment_delete == "Transport zone deleted successfully"
