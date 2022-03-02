"""
    Unit tests for vmc_public_ip state module
"""
from unittest.mock import create_autospec
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_public_ip as vmc_public_ip_exec
import saltext.vmware.states.vmc_public_ip as vmc_public_ip


@pytest.fixture
def configure_loader_modules():
    return {vmc_public_ip: {}}


@pytest.fixture
def mocked_ok_response():
    response = {
        "id": "TEST_PUBLIC_IP",
        "display_name": "TEST_PUBLIC_IP",
        "ip": "10.206.208.153",
        "marked_for_delete": False,
        "_create_time": 1618464918318,
        "_create_user": "pnaval@vmware.com",
        "_last_modified_time": 1618464919446,
        "_last_modified_user": "pnaval@vmware.com",
        "_protection": "UNKNOWN",
        "_revision": 1,
    }
    return response


@pytest.fixture
def mocked_error_response():
    error_response = {
        "error": "The credentials were incorrect or the account specified has been locked."
    }
    return error_response


def test_present_state_when_error_from_get_by_id(mocked_ok_response, mocked_error_response):
    mock_get_by_id = create_autospec(
        vmc_public_ip_exec.get_by_id, return_value=mocked_error_response
    )

    with patch.dict(vmc_public_ip.__salt__, {"vmc_public_ip.get_by_id": mock_get_by_id}):
        result = vmc_public_ip.present(
            name="test_present",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            public_ip_name=mocked_ok_response["id"],
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_state_when_error_from_create(mocked_ok_response, mocked_error_response):
    mock_get_by_id = create_autospec(vmc_public_ip_exec.get_by_id, return_value={})
    mock_create = create_autospec(vmc_public_ip_exec.create, return_value=mocked_error_response)

    with patch.dict(
        vmc_public_ip.__salt__,
        {
            "vmc_public_ip.get_by_id": mock_get_by_id,
            "vmc_public_ip.create": mock_create,
        },
    ):
        result = vmc_public_ip.present(
            name="test_present",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            public_ip_name=mocked_ok_response["id"],
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_state_when_error_from_update(mocked_ok_response, mocked_error_response):
    mock_get_by_id = create_autospec(vmc_public_ip_exec.get_by_id, return_value=mocked_ok_response)
    mock_update = create_autospec(vmc_public_ip_exec.update, return_value=mocked_error_response)

    with patch.dict(
        vmc_public_ip.__salt__,
        {
            "vmc_public_ip.get_by_id": mock_get_by_id,
            "vmc_public_ip.update": mock_update,
        },
    ):
        result = vmc_public_ip.present(
            name="test_present",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            public_ip_id=mocked_ok_response["id"],
            public_ip_name="updated public ip",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_state_during_update_to_add_a_new_field(mocked_ok_response):
    mocked_updated_response = mocked_ok_response.copy()
    mocked_ok_response.pop("display_name")
    mock_get_by_id = create_autospec(
        vmc_public_ip_exec.get_by_id, side_effect=[mocked_ok_response, mocked_updated_response]
    )

    mocked_updated_response["display_name"] = "updated public ip"

    mock_update = create_autospec(vmc_public_ip_exec.update, return_value=mocked_updated_response)

    with patch.dict(
        vmc_public_ip.__salt__,
        {
            "vmc_public_ip.get_by_id": mock_get_by_id,
            "vmc_public_ip.update": mock_update,
        },
    ):
        result = vmc_public_ip.present(
            name="test_present",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            public_ip_id=mocked_ok_response["id"],
            public_ip_name="updated public ip",
        )
    call_kwargs = mock_update.mock_calls[0][-1]
    assert call_kwargs["public_ip_name"] == "updated public ip"

    assert result is not None
    assert result["changes"]["old"] == mocked_ok_response
    assert result["changes"]["new"] == mocked_updated_response
    assert result["comment"] == "Updated public ip TEST_PUBLIC_IP"
    assert result["result"]


def test_present_to_create_when_module_returns_success_response(mocked_ok_response):
    mock_get_by_id_response = create_autospec(vmc_public_ip_exec.get_by_id, return_value={})
    mock_create_response = create_autospec(
        vmc_public_ip_exec.create, return_value=mocked_ok_response
    )
    public_ip = mocked_ok_response["id"]

    with patch.dict(
        vmc_public_ip.__salt__,
        {
            "vmc_public_ip.get_by_id": mock_get_by_id_response,
            "vmc_public_ip.create": mock_create_response,
        },
    ):
        result = vmc_public_ip.present(
            name="test_present",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            public_ip_name=mocked_ok_response["id"],
        )

    assert result is not None
    assert result["changes"]["new"] == mocked_ok_response
    assert result["changes"]["old"] is None
    assert result["comment"] == "Created public ip {}".format(public_ip)
    assert result["result"]


def test_present_state_for_create_when_opts_test_is_true(mocked_ok_response):
    mock_get_by_id_response = create_autospec(vmc_public_ip_exec.get_by_id, return_value={})
    public_ip_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_public_ip.__salt__,
        {"vmc_public_ip.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_public_ip.__opts__, {"test": True}):
            result = vmc_public_ip.present(
                name="test_present",
                hostname="hostname",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                public_ip_name=mocked_ok_response["id"],
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "State present will create public ip {}".format(public_ip_id)
    assert result["result"] is None


def test_present_state_for_update_when_opts_test_is_true(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_public_ip_exec.get_by_id, return_value=mocked_ok_response
    )
    public_ip_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_public_ip.__salt__,
        {"vmc_public_ip.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_public_ip.__opts__, {"test": True}):
            result = vmc_public_ip.present(
                name="test_present",
                hostname="hostname",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                public_ip_id=public_ip_id,
                public_ip_name="updated public ip",
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "State present will update public ip {}".format(public_ip_id)
    assert result["result"] is None


def test_absent_state_to_delete_when_module_returns_success_response(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_public_ip_exec.get_by_id, return_value=mocked_ok_response
    )
    mock_delete_response = create_autospec(
        vmc_public_ip_exec.delete, ok=True, return_value="Nat rule Deleted Successfully"
    )
    public_ip_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_public_ip.__salt__,
        {
            "vmc_public_ip.get_by_id": mock_get_by_id_response,
            "vmc_public_ip.delete": mock_delete_response,
        },
    ):
        result = vmc_public_ip.absent(
            name="test_absent",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            public_ip_id=mocked_ok_response["id"],
        )

    assert result is not None
    assert result["changes"] == {"new": None, "old": mocked_ok_response}
    assert result["comment"] == "Deleted public ip {}".format(public_ip_id)
    assert result["result"]


def test_absent_state_when_object_to_delete_does_not_exists(mocked_ok_response):
    mock_get_by_id_response = create_autospec(vmc_public_ip_exec.get_by_id, return_value={})
    public_ip_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_public_ip.__salt__,
        {"vmc_public_ip.get_by_id": mock_get_by_id_response},
    ):
        result = vmc_public_ip.absent(
            name="test_absent",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            public_ip_id=mocked_ok_response["id"],
        )

    assert result is not None
    assert result["changes"] == {}
    assert result["comment"] == "No public ip found with Id {}".format(public_ip_id)
    assert result["result"]


def test_absent_state_to_delete_when_opts_test_mode_is_true(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_public_ip_exec.get_by_id, return_value={"results": [mocked_ok_response]}
    )
    public_ip_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_public_ip.__salt__,
        {"vmc_public_ip.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_public_ip.__opts__, {"test": True}):
            result = vmc_public_ip.absent(
                name="test_absent",
                hostname="hostname",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                public_ip_id=mocked_ok_response["id"],
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "State absent will delete public ip with Id {}".format(public_ip_id)
    assert result["result"] is None


def test_absent_state_when_object_to_delete_doesn_not_exists_and_opts_test_mode_is_true(
    mocked_ok_response,
):
    mock_get_by_id_response = create_autospec(vmc_public_ip_exec.get_by_id, return_value={})
    public_ip_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_public_ip.__salt__,
        {"vmc_public_ip.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_public_ip.__opts__, {"test": True}):
            result = vmc_public_ip.absent(
                name="test_absent",
                hostname="hostname",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                public_ip_id=mocked_ok_response["id"],
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result[
        "comment"
    ] == "State absent will do nothing as no public ip found with Id {}".format(public_ip_id)
    assert result["result"] is None


def test_absent_with_error_from_delete(mocked_ok_response, mocked_error_response):
    mock_get_by_id = create_autospec(
        vmc_public_ip_exec.get_by_id, return_value={"results": [mocked_ok_response]}
    )
    mock_delete = create_autospec(vmc_public_ip_exec.delete, return_value=mocked_error_response)

    with patch.dict(
        vmc_public_ip.__salt__,
        {
            "vmc_public_ip.get_by_id": mock_get_by_id,
            "vmc_public_ip.delete": mock_delete,
        },
    ):
        result = vmc_public_ip.absent(
            name="test_absent",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            public_ip_id=mocked_ok_response["id"],
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_absent_state_when_error_from_get_by_id(mocked_ok_response, mocked_error_response):
    mock_get_by_id = create_autospec(
        vmc_public_ip_exec.get_by_id, return_value=mocked_error_response
    )

    with patch.dict(vmc_public_ip.__salt__, {"vmc_public_ip.get_by_id": mock_get_by_id}):
        result = vmc_public_ip.absent(
            name="test_absent",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            public_ip_id=mocked_ok_response["id"],
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]
