from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import saltext.vmware.states.nsxt_transport_zone as transport_zone
from salt.utils import dictdiffer

_mocked_hostname = "nsxt-vmware.local"
_mocked_username = "username"
_mocked_password = "pass"


@pytest.fixture
def configure_loader_modules():
    return {transport_zone: {}}


def test_present_state_when_opts_test_is_true_during_create_transport_zone():

    ret = {"name": "register-transport-zone", "result": None, "comment": "", "changes": {}}

    data = {"results": [], "result_count": 0, "sort_by": "display_name", "sort_ascending": "true"}

    get_transport_zone = MagicMock(return_value=data)
    with patch.dict(
        transport_zone.__salt__, {"nsxt_transport_zone.get_by_display_name": get_transport_zone}
    ):
        with patch.dict(transport_zone.__opts__, {"test": True}):
            ret["comment"] = "Transport zone will be created in NSX-T Manager"

            assert (
                transport_zone.present(
                    name="register-transport-zone",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    host_switch_name="Test-Host-Switch",
                    transport_type="Overlay",
                    display_name="Test-Transport-Zone",
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_when_creating_a_new_transport_zone():
    ret = {"name": "register-transport-zone", "result": None, "comment": "", "changes": {}}

    transport_zones = {
        "results": [],
        "result_count": 0,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }

    new_transport_zone = {
        "transport_type": "Overlay",
        "host_switch_name": "nsxDefaultHostSwitch",
        "host_switch_id": "0d6411e2-8c82-4e37-9fca-7082e2bff4c1",
        "is_default": False,
        "resource_type": "TransportZone",
        "id": "57a05017-e272-4562-bce1-e46bf6b820c9",
        "display_name": "Test-Host-Switch",
        "_revision": 0,
    }

    with patch.dict(
        transport_zone.__salt__,
        {
            "nsxt_transport_zone.get_by_display_name": MagicMock(return_value=transport_zones),
            "nsxt_transport_zone.create": MagicMock(return_value=new_transport_zone),
        },
    ):
        ret["comment"] = "Transport Zone created successfully"
        ret["changes"]["new"] = new_transport_zone
        ret["result"] = True

        with patch.dict(transport_zone.__opts__, {"test": False}):
            actual = transport_zone.present(
                name="register-transport-zone",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                host_switch_name="Test-Host-Switch",
                transport_type="Overlay",
                display_name="Test-Host-Switch",
                verify_ssl=False,
            )
            assert dictdiffer.deep_diff(ret, actual)


def test_present_state_to_create_new_transport_zone_with_error_in_get_call():
    ret = {"name": "register-transport-zone", "result": None, "comment": "", "changes": {}}

    error_msg = "Http error occurred. Please provide correct credentials"
    err_json = {"error": error_msg}

    with patch.dict(
        transport_zone.__salt__,
        {"nsxt_transport_zone.get_by_display_name": MagicMock(return_value=err_json)},
    ):
        ret["comment"] = "Failed to get the transport zones : {}".format(error_msg)
        ret["result"] = False

        with patch.dict(transport_zone.__opts__, {"test": False}):
            assert (
                transport_zone.present(
                    name="register-transport-zone",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    host_switch_name="Test-Host-Switch",
                    transport_type="Overlay",
                    display_name="Create-IT1",
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_to_create_new_transport_zone_with_multiple_transport_zones_with_same_display_name():
    ret = {"name": "register-transport-zone", "result": None, "comment": "", "changes": {}}

    transport_zones = {
        "results": [
            {
                "transport_type": "OVERLAY",
                "host_switch_name": "nsxDefaultHostSwitch",
                "host_switch_id": "0d6411e2-8c82-4e37-9fca-7082e2bff4c1",
                "is_default": False,
                "resource_type": "TransportZone",
                "id": "2545c5a6-c46c-4cb4-9ee6-5d62acaf1ae7",
                "display_name": "Create-IT1",
                "_revision": 0,
            },
            {
                "transport_type": "OVERLAY",
                "host_switch_name": "nsxDefaultHostSwitch",
                "host_switch_id": "0d6411e2-8c82-4e37-9fca-7082e2bff4c1",
                "is_default": False,
                "resource_type": "TransportZone",
                "id": "2545c5a6-c46c-4cb4-9ee6-5d62acaf1ae7",
                "display_name": "Create-IT1",
                "_revision": 0,
            },
        ],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }

    new_transport_zone = {
        "transport_type": "Overlay",
        "host_switch_name": "nsxDefaultHostSwitch",
        "host_switch_id": "0d6411e2-8c82-4e37-9fca-7082e2bff4c1",
        "is_default": False,
        "resource_type": "TransportZone",
        "id": "57a05017-e272-4562-bce1-e46bf6b820c9",
        "display_name": "Test-Host-Switch",
        "_revision": 0,
    }

    with patch.dict(
        transport_zone.__salt__,
        {
            "nsxt_transport_zone.get_by_display_name": MagicMock(return_value=transport_zones),
            "nsxt_transport_zone.create": MagicMock(return_value=new_transport_zone),
        },
    ):
        ret["comment"] = "More than one transport zone exist with same display name : {}".format(
            "Create-IT1"
        )
        ret["result"] = False

        with patch.dict(transport_zone.__opts__, {"test": False}):
            assert (
                transport_zone.present(
                    name="register-transport-zone",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    host_switch_name="Test-Host-Switch",
                    transport_type="Overlay",
                    display_name="Create-IT1",
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_to_create_new_transport_zone_with_error_from_execution_module():
    ret = {"name": "register-transport-zone", "result": None, "comment": "", "changes": {}}

    error_msg = "Http error occurred. Please provide correct credentials"
    err_json = {"error": error_msg}

    transport_zones = {
        "results": [],
        "result_count": 0,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }

    with patch.dict(
        transport_zone.__salt__,
        {
            "nsxt_transport_zone.get_by_display_name": MagicMock(return_value=transport_zones),
            "nsxt_transport_zone.create": MagicMock(return_value=err_json),
        },
    ):
        ret[
            "comment"
        ] = "Fail to create transport_zone : Http error occurred. Please provide correct credentials"
        ret["changes"] = {}
        ret["result"] = False

        with patch.dict(transport_zone.__opts__, {"test": False}):
            assert (
                transport_zone.present(
                    name="register-transport-zone",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    host_switch_name="Test-Host-Switch",
                    transport_type="Overlay",
                    display_name="Test-Create-Transport-Zone",
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_to_create_new_transport_zone_when_same_transport_zone_already_exists():
    ret = {"name": "register-transport-zone", "result": None, "comment": "", "changes": {}}

    transport_zones = {
        "results": [
            {
                "transport_type": "Overlay",
                "host_switch_name": "nsxDefaultHostSwitch",
                "host_switch_id": "0d6411e2-8c82-4e37-9fca-7082e2bff4c1",
                "id": "57a05017-e272-4562-bce1-e46bf6b820c9",
                "display_name": "Test-Host-Switch",
                "_revision": 0,
            }
        ],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }

    new_transport_zone = {
        "transport_type": "Overlay",
        "host_switch_name": "nsxDefaultHostSwitch",
        "host_switch_id": "0d6411e2-8c82-4e37-9fca-7082e2bff4c1",
        "display_name": "Test-Host-Switch",
    }

    with patch.dict(
        transport_zone.__salt__,
        {
            "nsxt_transport_zone.get_by_display_name": MagicMock(return_value=transport_zones),
            "nsxt_transport_zone.create": MagicMock(return_value=new_transport_zone),
        },
    ):
        ret["comment"] = "Transport zone with display_name %s already exists", "Test-Host-Switch"
        ret["changes"] = {}
        ret["result"] = True

        with patch.dict(transport_zone.__opts__, {"test": False}):
            assert (
                transport_zone.present(
                    name="register-transport-zone",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    verify_ssl=False,
                    **new_transport_zone
                )
                == ret
            )


def test_present_state_to_update_existing_transport_zone():

    ret = {"name": "register-transport-zone", "result": None, "comment": "", "changes": {}}

    transport_zones = {
        "results": [
            {
                "transport_type": "Overlay",
                "host_switch_name": "nsxDefaultHostSwitch",
                "host_switch_id": "0d6411e2-8c82-4e37-9fca-7082e2bff4c1",
                "is_default": False,
                "resource_type": "TransportZone",
                "id": "57a05017-e272-4562-bce1-e46bf6b820c9",
                "display_name": "Test-Host-Switch",
                "_revision": 0,
            }
        ],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }

    new_transport_zone = {
        "transport_type": "Overlay",
        "host_switch_name": "nsxDefaultHostSwitch",
        "host_switch_id": "0d6411e2-8c82-4e37-9fca-7082e2bff4c1",
        "is_default": False,
        "resource_type": "TransportZone",
        "id": "57a05017-e272-4562-bce1-e46bf6b820c9",
        "display_name": "Test-Host-Switch",
        "_revision": 0,
    }

    with patch.dict(
        transport_zone.__salt__,
        {
            "nsxt_transport_zone.get_by_display_name": MagicMock(return_value=transport_zones),
            "nsxt_transport_zone.update": MagicMock(return_value=new_transport_zone),
        },
    ):
        ret["comment"] = "Transport Zone updated successfully"
        ret["changes"]["old"] = transport_zones["results"][0]
        ret["changes"]["new"] = new_transport_zone
        ret["result"] = True

        with patch.dict(transport_zone.__opts__, {"test": False}):
            assert (
                transport_zone.present(
                    name="register-transport-zone",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    host_switch_name="Test-Host-Switch",
                    transport_type="Overlay",
                    display_name="Test-Host-Switch",
                    description="Test-Edit",
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_to_update_transport_zone_when_error_from_update_call():

    ret = {"name": "register-transport-zone", "result": None, "comment": "", "changes": {}}

    error_msg = "Http error occurred. Please provide correct credentials"
    err_json = {"error": error_msg}

    transport_zones = {
        "results": [
            {
                "transport_type": "Overlay",
                "host_switch_name": "nsxDefaultHostSwitch",
                "host_switch_id": "0d6411e2-8c82-4e37-9fca-7082e2bff4c1",
                "is_default": False,
                "resource_type": "TransportZone",
                "id": "57a05017-e272-4562-bce1-e46bf6b820c9",
                "display_name": "Test-Host-Switch",
                "_revision": 0,
            }
        ],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }

    with patch.dict(
        transport_zone.__salt__,
        {
            "nsxt_transport_zone.get_by_display_name": MagicMock(return_value=transport_zones),
            "nsxt_transport_zone.update": MagicMock(return_value=err_json),
        },
    ):
        ret[
            "comment"
        ] = "Fail to update transport_zone : Http error occurred. Please provide correct credentials"
        ret["changes"] = {}
        ret["result"] = False

        with patch.dict(transport_zone.__opts__, {"test": False}):
            assert (
                transport_zone.present(
                    name="register-transport-zone",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    host_switch_name="Test-Host-Switch",
                    transport_type="Overlay",
                    display_name="Test-Host-Switch",
                    description="Test-Edit",
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_state_to_delete_an_existing_transport_zone():

    transport_zone_resp = {
        "transport_type": "Overlay",
        "host_switch_name": "nsxDefaultHostSwitch",
        "host_switch_id": "0d6411e2-8c82-4e37-9fca-7082e2bff4c1",
        "is_default": False,
        "resource_type": "TransportZone",
        "id": "57a05017-e272-4562-bce1-e46bf6b820c9",
        "display_name": "Test-Host-Switch",
        "_revision": 0,
    }

    transport_zones = {
        "results": [transport_zone_resp],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }

    with patch.dict(
        transport_zone.__salt__,
        {
            "nsxt_transport_zone.get_by_display_name": MagicMock(return_value=transport_zones),
            "nsxt_transport_zone.delete": MagicMock(
                return_value={"message": "Removed transport zone successfully"}
            ),
        },
    ):

        with patch.dict(transport_zone.__opts__, {"test": False}):
            response = transport_zone.absent(
                name="register-transport-zone",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name="Test-Host-Switch",
                verify_ssl=False,
            )

        assert response["result"] == True
        assert response["comment"] == "Transport zone deleted successfully"


def test_absent_state_error_when_get_transport_zone_call_returns_error():
    ret = {"name": "register-transport-zone", "result": None, "comment": "", "changes": {}}

    error_msg = "Http error occurred. Please provide correct credentials"
    err_json = {"error": error_msg}

    with patch.dict(
        transport_zone.__salt__,
        {"nsxt_transport_zone.get_by_display_name": MagicMock(return_value=err_json)},
    ):
        ret[
            "comment"
        ] = "Failed to get the transport zones : Http error occurred. Please provide correct credentials"
        ret["result"] = False

        with patch.dict(transport_zone.__opts__, {"test": False}):
            assert (
                transport_zone.absent(
                    name="register-transport-zone",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name="Test-Host-Switch",
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_state_error_when_delete_call_returns_error():
    ret = {"name": "register-transport-zone", "result": None, "comment": "", "changes": {}}

    error_msg = "Http error occurred. Please provide correct credentials"
    err_json = {"error": error_msg}

    transport_zones = {
        "results": [
            {
                "transport_type": "Overlay",
                "host_switch_name": "nsxDefaultHostSwitch",
                "host_switch_id": "0d6411e2-8c82-4e37-9fca-7082e2bff4c1",
                "is_default": False,
                "resource_type": "TransportZone",
                "id": "57a05017-e272-4562-bce1-e46bf6b820c9",
                "display_name": "Test-Host-Switch",
                "_revision": 0,
            }
        ],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }

    with patch.dict(
        transport_zone.__salt__,
        {
            "nsxt_transport_zone.get_by_display_name": MagicMock(return_value=transport_zones),
            "nsxt_transport_zone.delete": MagicMock(return_value=err_json),
        },
    ):
        ret[
            "comment"
        ] = "Failed to delete the transport-zone : Http error occurred. Please provide correct credentials"
        ret["result"] = False

        with patch.dict(transport_zone.__opts__, {"test": False}):
            assert (
                transport_zone.absent(
                    name="register-transport-zone",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name="Test-Host-Switch",
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_state_error_when_get_returns_multiple_transport_zones_with_same_name():
    ret = {"name": "register-transport-zone", "result": None, "comment": "", "changes": {}}

    transport_zones = {
        "results": [
            {
                "transport_type": "OVERLAY",
                "host_switch_name": "nsxDefaultHostSwitch",
                "host_switch_id": "0d6411e2-8c82-4e37-9fca-7082e2bff4c1",
                "is_default": False,
                "resource_type": "TransportZone",
                "id": "2545c5a6-c46c-4cb4-9ee6-5d62acaf1ae7",
                "display_name": "Create-IT1",
                "_revision": 0,
            },
            {
                "transport_type": "OVERLAY",
                "host_switch_name": "nsxDefaultHostSwitch",
                "host_switch_id": "0d6411e2-8c82-4e37-9fca-7082e2bff4c1",
                "is_default": False,
                "resource_type": "TransportZone",
                "id": "2545c5a6-c46c-4cb4-9ee6-5d62acaf1ae7",
                "display_name": "Create-IT1",
                "_revision": 0,
            },
        ],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }

    with patch.dict(
        transport_zone.__salt__,
        {"nsxt_transport_zone.get_by_display_name": MagicMock(return_value=transport_zones)},
    ):
        ret["comment"] = "More than one transport zone exist with same display name : {}".format(
            "Create-IT1"
        )
        ret["result"] = False

        with patch.dict(transport_zone.__opts__, {"test": False}):
            assert (
                transport_zone.absent(
                    name="register-transport-zone",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name="Create-IT1",
                    verify_ssl=False,
                )
                == ret
            )
