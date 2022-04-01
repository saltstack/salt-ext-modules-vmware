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
    mock_get_by_id = create_autospec(vmc_public_ip_exec.get, return_value=mocked_error_response)

    with patch.dict(vmc_public_ip.__salt__, {"vmc_public_ip.get": mock_get_by_id}):
        result = vmc_public_ip.present(
            name=mocked_ok_response["id"],
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_state_when_error_from_create(mocked_ok_response, mocked_error_response):
    mock_get_by_id = create_autospec(vmc_public_ip_exec.get, return_value={})
    mock_create = create_autospec(vmc_public_ip_exec.create, return_value=mocked_error_response)

    with patch.dict(
        vmc_public_ip.__salt__,
        {
            "vmc_public_ip.get": mock_get_by_id,
            "vmc_public_ip.create": mock_create,
        },
    ):
        result = vmc_public_ip.present(
            name=mocked_ok_response["id"],
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_state_when_error_from_update(mocked_ok_response, mocked_error_response):
    mock_get_by_id = create_autospec(vmc_public_ip_exec.get, return_value=mocked_ok_response)
    mock_update = create_autospec(vmc_public_ip_exec.update, return_value=mocked_error_response)

    with patch.dict(
        vmc_public_ip.__salt__,
        {
            "vmc_public_ip.get": mock_get_by_id,
            "vmc_public_ip.update": mock_update,
        },
    ):
        result = vmc_public_ip.present(
            name=mocked_ok_response["id"],
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            display_name="updated public ip",
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
        vmc_public_ip_exec.get, side_effect=[mocked_ok_response, mocked_updated_response]
    )

    mocked_updated_response["display_name"] = "updated public ip"

    mock_update = create_autospec(vmc_public_ip_exec.update, return_value=mocked_updated_response)

    with patch.dict(
        vmc_public_ip.__salt__,
        {
            "vmc_public_ip.get": mock_get_by_id,
            "vmc_public_ip.update": mock_update,
        },
    ):
        result = vmc_public_ip.present(
            name=mocked_ok_response["id"],
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            display_name="updated public ip",
        )
    call_kwargs = mock_update.mock_calls[0][-1]
    assert call_kwargs["display_name"] == "updated public ip"

    assert result is not None
    assert result["changes"]["old"] == mocked_ok_response
    assert result["changes"]["new"] == mocked_updated_response
    assert result["comment"] == "Updated public IP TEST_PUBLIC_IP"
    assert result["result"]


def test_present_to_create_when_module_returns_success_response(mocked_ok_response):
    mock_get_by_id_response = create_autospec(vmc_public_ip_exec.get, return_value={})
    mock_create_response = create_autospec(
        vmc_public_ip_exec.create, return_value=mocked_ok_response
    )
    public_ip = mocked_ok_response["id"]

    with patch.dict(
        vmc_public_ip.__salt__,
        {
            "vmc_public_ip.get": mock_get_by_id_response,
            "vmc_public_ip.create": mock_create_response,
        },
    ):
        result = vmc_public_ip.present(
            name=mocked_ok_response["id"],
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
        )

    assert result is not None
    assert result["changes"]["new"] == mocked_ok_response
    assert result["changes"]["old"] is None
    assert result["comment"] == "Created public IP {}".format(public_ip)
    assert result["result"]


def test_present_state_for_create_when_opts_test_is_true(mocked_ok_response):
    mock_get_by_id_response = create_autospec(vmc_public_ip_exec.get, return_value={})
    public_ip_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_public_ip.__salt__,
        {"vmc_public_ip.get": mock_get_by_id_response},
    ):
        with patch.dict(vmc_public_ip.__opts__, {"test": True}):
            result = vmc_public_ip.present(
                name=mocked_ok_response["id"],
                hostname="hostname",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "Public IP {} would have been created".format(public_ip_id)
    assert result["result"] is None


def test_present_state_for_update_when_opts_test_is_true(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_public_ip_exec.get, return_value=mocked_ok_response
    )
    public_ip_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_public_ip.__salt__,
        {"vmc_public_ip.get": mock_get_by_id_response},
    ):
        with patch.dict(vmc_public_ip.__opts__, {"test": True}):
            result = vmc_public_ip.present(
                name=public_ip_id,
                hostname="hostname",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                display_name="updated public ip",
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "Public IP {} would have been updated".format(public_ip_id)
    assert result["result"] is None


def test_present_to_update_when_user_input_and_existing_public_ip_has_identical_fields(
    mocked_ok_response,
):
    mock_get_by_id_response = create_autospec(
        vmc_public_ip_exec.get, return_value=mocked_ok_response
    )

    with patch.dict(
        vmc_public_ip.__salt__,
        {"vmc_public_ip.get": mock_get_by_id_response},
    ):
        result = vmc_public_ip.present(
            name=mocked_ok_response["id"],
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
        )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "Public IP exists already, no action to perform"
    assert result["result"]


def test_absent_state_to_delete_when_module_returns_success_response(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_public_ip_exec.get, return_value=mocked_ok_response
    )
    mock_delete_response = create_autospec(
        vmc_public_ip_exec.delete, ok=True, return_value="Nat rule Deleted Successfully"
    )
    public_ip_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_public_ip.__salt__,
        {
            "vmc_public_ip.get": mock_get_by_id_response,
            "vmc_public_ip.delete": mock_delete_response,
        },
    ):
        result = vmc_public_ip.absent(
            name=mocked_ok_response["id"],
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
        )

    assert result is not None
    assert result["changes"] == {"new": None, "old": mocked_ok_response}
    assert result["comment"] == "Deleted public IP {}".format(public_ip_id)
    assert result["result"]


def test_absent_state_when_object_to_delete_does_not_exists(mocked_ok_response):
    mock_get_by_id_response = create_autospec(vmc_public_ip_exec.get, return_value={})
    public_ip_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_public_ip.__salt__,
        {"vmc_public_ip.get": mock_get_by_id_response},
    ):
        result = vmc_public_ip.absent(
            name=mocked_ok_response["id"],
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert result["comment"] == "No public IP found with ID {}".format(public_ip_id)
    assert result["result"]


def test_absent_state_to_delete_when_opts_test_mode_is_true(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_public_ip_exec.get, return_value={"results": [mocked_ok_response]}
    )
    public_ip_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_public_ip.__salt__,
        {"vmc_public_ip.get": mock_get_by_id_response},
    ):
        with patch.dict(vmc_public_ip.__opts__, {"test": True}):
            result = vmc_public_ip.absent(
                name=mocked_ok_response["id"],
                hostname="hostname",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "State absent will delete public IP with ID {}".format(public_ip_id)
    assert result["result"] is None


def test_absent_state_when_object_to_delete_doesn_not_exists_and_opts_test_mode_is_true(
    mocked_ok_response,
):
    mock_get_by_id_response = create_autospec(vmc_public_ip_exec.get, return_value={})
    public_ip_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_public_ip.__salt__,
        {"vmc_public_ip.get": mock_get_by_id_response},
    ):
        with patch.dict(vmc_public_ip.__opts__, {"test": True}):
            result = vmc_public_ip.absent(
                name=mocked_ok_response["id"],
                hostname="hostname",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result[
        "comment"
    ] == "State absent will do nothing as no public IP found with ID {}".format(public_ip_id)
    assert result["result"] is None


def test_absent_with_error_from_delete(mocked_ok_response, mocked_error_response):
    mock_get_by_id = create_autospec(
        vmc_public_ip_exec.get, return_value={"results": [mocked_ok_response]}
    )
    mock_delete = create_autospec(vmc_public_ip_exec.delete, return_value=mocked_error_response)

    with patch.dict(
        vmc_public_ip.__salt__,
        {
            "vmc_public_ip.get": mock_get_by_id,
            "vmc_public_ip.delete": mock_delete,
        },
    ):
        result = vmc_public_ip.absent(
            name=mocked_ok_response["id"],
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_absent_state_when_error_from_get_by_id(mocked_ok_response, mocked_error_response):
    mock_get_by_id = create_autospec(vmc_public_ip_exec.get, return_value=mocked_error_response)

    with patch.dict(vmc_public_ip.__salt__, {"vmc_public_ip.get": mock_get_by_id}):
        result = vmc_public_ip.absent(
            name=mocked_ok_response["id"],
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_when_get_by_id_returns_not_found_error(mocked_ok_response):
    error_response = {"error": "PublicIp Object Not Found"}
    mock_get_by_id_response = create_autospec(vmc_public_ip_exec.get, return_value=error_response)
    mock_create_response = create_autospec(
        vmc_public_ip_exec.create, return_value=mocked_ok_response
    )

    public_ip_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_public_ip.__salt__,
        {
            "vmc_public_ip.get": mock_get_by_id_response,
            "vmc_public_ip.create": mock_create_response,
        },
    ):
        result = vmc_public_ip.present(
            name=public_ip_id,
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
        )

    assert result is not None
    assert result["changes"]["new"] == mocked_ok_response
    assert result["changes"]["old"] is None
    assert result["comment"] == "Created public IP {}".format(public_ip_id)
    assert result["result"]


@pytest.mark.parametrize(
    "actual_args",
    [
        # all actual args are None
        ({}),
    ],
)
def test_present_state_during_create_should_correctly_pass_args(mocked_ok_response, actual_args):
    mocked_updated_response = mocked_ok_response.copy()
    mock_get_by_id_response = create_autospec(vmc_public_ip_exec.get, return_value={})

    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "verify_ssl": False,
    }

    mocked_updated_response.update(actual_args)
    actual_args.update(common_actual_args)
    mock_create = create_autospec(vmc_public_ip_exec.create, return_value=mocked_updated_response)

    with patch.dict(
        vmc_public_ip.__salt__,
        {
            "vmc_public_ip.get": mock_get_by_id_response,
            "vmc_public_ip.create": mock_create,
        },
    ):
        result = vmc_public_ip.present(name=mocked_ok_response["id"], **actual_args)

    call_kwargs = mock_create.mock_calls[0][-1]

    subset = {k: v for k, v in call_kwargs.items() if k in actual_args}
    assert subset == actual_args

    assert result is not None
    assert result["changes"]["old"] is None
    assert result["changes"]["new"] == mocked_updated_response
    assert result["comment"] == "Created public IP {}".format(mocked_ok_response["id"])
    assert result["result"]


@pytest.mark.parametrize(
    "actual_args",
    [
        # One required parameter
        ({"display_name": "updated public ip"}),
    ],
)
def test_present_state_during_update_should_correctly_pass_args(mocked_ok_response, actual_args):
    mocked_updated_response = mocked_ok_response.copy()
    mocked_ok_response.pop("display_name")
    mock_get_by_id = create_autospec(
        vmc_public_ip_exec.get, side_effect=[mocked_ok_response, mocked_updated_response]
    )

    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "verify_ssl": False,
    }

    mocked_updated_response.update(actual_args)
    actual_args.update(common_actual_args)
    mock_update = create_autospec(vmc_public_ip_exec.update, return_value=mocked_updated_response)

    with patch.dict(
        vmc_public_ip.__salt__,
        {
            "vmc_public_ip.get": mock_get_by_id,
            "vmc_public_ip.update": mock_update,
        },
    ):
        result = vmc_public_ip.present(name=mocked_ok_response["id"], **actual_args)

    call_kwargs = mock_update.mock_calls[0][-1]

    subset = {k: v for k, v in call_kwargs.items() if k in actual_args}
    assert subset == actual_args

    assert result is not None
    assert result["changes"]["old"] == mocked_ok_response
    assert result["changes"]["new"] == mocked_updated_response
    assert result["comment"] == "Updated public IP {}".format(mocked_ok_response["id"])
    assert result["result"]


#
#
#
# def test_present_to_update_when_module_returns_success_response(mocked_ok_response):
#     mocked_updated_public_ip = mocked_ok_response.copy()
#     mocked_updated_public_ip["display_name"] = "public-ip-1"
#
#     mock_get_by_id_response = create_autospec(
#         vmc_public_ip_exec.get, side_effect=[mocked_ok_response, mocked_updated_public_ip]
#     )
#     mock_update_response = create_autospec(
#         vmc_public_ip_exec.update, return_value=mocked_updated_public_ip
#     )
#
#     public_ip_id = mocked_ok_response["id"]
#
#     with patch.dict(
#         vmc_public_ip.__salt__,
#         {
#             "vmc_public_ip.get": mock_get_by_id_response,
#             "vmc_public_ip.update": mock_update_response,
#         },
#     ):
#         result = vmc_public_ip.present(
#             name=public_ip_id,
#             hostname="hostname",
#             refresh_key="refresh_key",
#             authorization_host="authorization_host",
#             org_id="org_id",
#             sddc_id="sddc_id",
#             display_name="network-1",
#         )
#
#     assert result is not None
#     assert result["changes"]["new"] == mocked_updated_public_ip
#     assert result["changes"]["old"] == mocked_ok_response
#     assert result["comment"] == "Updated public IP {}".format(public_ip_id)
#     assert result["result"]
