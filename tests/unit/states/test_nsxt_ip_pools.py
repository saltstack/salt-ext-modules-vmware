"""
    Unit Tests for nsxt_ip_pools state
"""
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from saltext.vmware.states import nsxt_ip_pools


@pytest.fixture
def configure_loader_modules():
    return {nsxt_ip_pools: {}}


def _get_mocked_data():
    mocked_ok_response = {
        "pool_usage": {"total_ids": 0, "allocated_ids": 0, "free_ids": 0},
        "resource_type": "IpPool",
        "id": "9b636d18-49a2-4e63-a1ec-10c0e50d554d",
        "display_name": "Create-from_salt",
        "description": "Check",
        "_create_user": "admin",
        "_create_time": 1615905790948,
        "_last_modified_user": "admin",
        "_last_modified_time": 1615905790948,
        "_system_owned": False,
        "_protection": "NOT_PROTECTED",
        "_revision": 0,
    }
    mocked_error_response = {
        "error": "The credentials were incorrect or the account specified has been locked."
    }
    mocked_hostname = "nsx-t.vmware.com"

    return mocked_hostname, mocked_ok_response, mocked_error_response


def test_present_without_parameters():
    with pytest.raises(TypeError) as exc:
        nsxt_ip_pools.present()

        assert (
            str(exc.value)
            == "present() missing 5 required positional arguments: 'name', 'display_name', "
            "'hostname', 'username', and 'password' "
        )


def test_absent_without_parameters():
    with pytest.raises(TypeError) as exc:
        nsxt_ip_pools.absent()

    assert (
        str(exc.value)
        == "absent() missing 5 required positional arguments: 'name', 'display_name', 'hostname', "
        "'username', and 'password'"
    )


def test_present_with_error_from_get_by_display_name():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_using_display_name = MagicMock(return_value=mocked_error_response)

    with patch.dict(
        nsxt_ip_pools.__salt__, {"nsxt_ip_pools.get_by_display_name": mock_get_using_display_name}
    ):
        result = nsxt_ip_pools.present(
            name="test_present_using_basic_auth",
            hostname=mocked_hostname,
            username="username",
            password="password",
            display_name=mocked_ok_response["display_name"],
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not bool(result["result"])


def test_present_with_error_from_create():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_using_display_name = MagicMock(return_value={"results": []})
    mock_create = MagicMock(return_value=mocked_error_response)

    with patch.dict(
        nsxt_ip_pools.__salt__,
        {
            "nsxt_ip_pools.get_by_display_name": mock_get_using_display_name,
            "nsxt_ip_pools.create": mock_create,
        },
    ):
        result = nsxt_ip_pools.present(
            name="test_present_using_basic_auth",
            hostname=mocked_hostname,
            username="username",
            password="password",
            display_name=mocked_ok_response["display_name"],
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not bool(result["result"])


def test_present_with_error_from_update():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_using_display_name = MagicMock(return_value={"results": [mocked_ok_response]})
    mock_create = MagicMock(return_value=mocked_error_response)

    with patch.dict(
        nsxt_ip_pools.__salt__,
        {
            "nsxt_ip_pools.get_by_display_name": mock_get_using_display_name,
            "nsxt_ip_pools.update": mock_create,
        },
    ):
        result = nsxt_ip_pools.present(
            name="test_present_using_basic_auth",
            hostname=mocked_hostname,
            username="username",
            password="password",
            description="Sample description",
            display_name=mocked_ok_response["display_name"],
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not bool(result["result"])


def test_present_with_update_to_add_new_field():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mocked_updated_response = mocked_ok_response.copy()
    mocked_ok_response.pop("description")
    mock_get_using_display_name = MagicMock(return_value={"results": [mocked_ok_response]})

    mocked_updated_response["description"] = "Sample description"
    mock_create = MagicMock(return_value=mocked_updated_response)

    with patch.dict(
        nsxt_ip_pools.__salt__,
        {
            "nsxt_ip_pools.get_by_display_name": mock_get_using_display_name,
            "nsxt_ip_pools.update": mock_create,
        },
    ):
        result = nsxt_ip_pools.present(
            name="test_present_using_basic_auth",
            hostname=mocked_hostname,
            username="username",
            password="password",
            description="Sample description",
            display_name=mocked_ok_response["display_name"],
        )

    assert result is not None
    assert result["changes"]["old"] == mocked_ok_response
    assert result["changes"]["new"] == mocked_updated_response
    assert result["comment"] == "Updated IP Pool Create-from_salt"
    assert bool(result["result"])


def test_present_to_create_with_basic_auth():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_using_display_name_response = MagicMock(return_value={"results": []})
    mock_create_response = MagicMock(return_value=mocked_ok_response)
    display_name = mocked_ok_response["display_name"]

    with patch.dict(
        nsxt_ip_pools.__salt__,
        {
            "nsxt_ip_pools.get_by_display_name": mock_get_using_display_name_response,
            "nsxt_ip_pools.create": mock_create_response,
        },
    ):
        result = nsxt_ip_pools.present(
            name="test_present_using_basic_auth",
            hostname=mocked_hostname,
            username="username",
            password="password",
            display_name=display_name,
        )

    assert result is not None
    assert result["changes"] == {"new": mocked_ok_response, "old": None}
    assert result["comment"] == "Created IP Pool {}".format(display_name)
    assert bool(result["result"])


def test_present_to_update_with_basic_auth():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()
    mocked_updated_ip_pool = mocked_ok_response.copy()
    mocked_updated_ip_pool["description"] = "Updated Using Salt"

    mock_get_using_display_name_response = MagicMock(return_value={"results": [mocked_ok_response]})
    mock_update_response = MagicMock(return_value=mocked_updated_ip_pool)
    display_name = mocked_ok_response["display_name"]

    with patch.dict(
        nsxt_ip_pools.__salt__,
        {
            "nsxt_ip_pools.get_by_display_name": mock_get_using_display_name_response,
            "nsxt_ip_pools.update": mock_update_response,
        },
    ):
        result = nsxt_ip_pools.present(
            name="test_present_using_basic_auth",
            hostname=mocked_hostname,
            username="username",
            password="password",
            display_name=display_name,
            description="Updated Using Salt",
        )

    assert result is not None
    assert result["changes"] == {"new": mocked_updated_ip_pool, "old": mocked_ok_response}
    assert result["comment"] == "Updated IP Pool {}".format(display_name)
    assert bool(result["result"])


def test_present_to_update_with_identical_fields():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_using_display_name_response = MagicMock(return_value={"results": [mocked_ok_response]})
    display_name = mocked_ok_response["display_name"]

    with patch.dict(
        nsxt_ip_pools.__salt__,
        {"nsxt_ip_pools.get_by_display_name": mock_get_using_display_name_response},
    ):
        result = nsxt_ip_pools.present(
            name="test_present_using_basic_auth",
            hostname=mocked_hostname,
            username="username",
            password="password",
            display_name=display_name,
            description="Check",
        )

    assert result is not None
    assert result["changes"].__len__() == 0
    assert result["comment"] == "IP Address Pool exists already, no action to perform"
    assert bool(result["result"])


def test_present_to_create_in_test_mode():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_using_display_name_response = MagicMock(return_value={"results": []})
    display_name = mocked_ok_response["display_name"]

    with patch.dict(
        nsxt_ip_pools.__salt__,
        {"nsxt_ip_pools.get_by_display_name": mock_get_using_display_name_response},
    ):
        with patch.dict(nsxt_ip_pools.__opts__, {"test": True}):
            result = nsxt_ip_pools.present(
                name="test_absent_using_basic_auth",
                hostname=mocked_hostname,
                username="username",
                password="password",
                display_name=display_name,
            )

    assert result is not None
    assert result["changes"].__len__() == 0
    assert result["comment"] == "State present will create IP Pool with name {}".format(
        display_name
    )
    assert result["result"] is None


def test_present_to_update_in_test_mode():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_using_display_name_response = MagicMock(return_value={"results": [mocked_ok_response]})
    display_name = mocked_ok_response["display_name"]

    with patch.dict(
        nsxt_ip_pools.__salt__,
        {"nsxt_ip_pools.get_by_display_name": mock_get_using_display_name_response},
    ):
        with patch.dict(nsxt_ip_pools.__opts__, {"test": True}):
            result = nsxt_ip_pools.present(
                name="test_absent_using_basic_auth",
                hostname=mocked_hostname,
                username="username",
                password="password",
                display_name=display_name,
            )

    assert result is not None
    assert result["changes"].__len__() == 0
    assert result["comment"] == "State present will update IP Pool with name {}".format(
        display_name
    )
    assert result["result"] is None


def test_present_when_multiple_pools_with_same_display_name():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_using_display_name_response = MagicMock(
        return_value={"results": [mocked_ok_response, mocked_ok_response]}
    )
    display_name = mocked_ok_response["display_name"]

    with patch.dict(
        nsxt_ip_pools.__salt__,
        {"nsxt_ip_pools.get_by_display_name": mock_get_using_display_name_response},
    ):
        with patch.dict(nsxt_ip_pools.__opts__, {"test": True}):
            result = nsxt_ip_pools.present(
                name="test_absent_using_basic_auth",
                hostname=mocked_hostname,
                username="username",
                password="password",
                display_name=display_name,
            )

    assert result is not None
    assert result["changes"].__len__() == 0
    assert result["comment"] == "Multiple IP Pools found for the provided display name {}".format(
        display_name
    )
    assert not result["result"]


def test_absent_to_delete_with_basic_auth():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_using_display_name_response = MagicMock(return_value={"results": [mocked_ok_response]})
    mock_delete_response = MagicMock(ok=True, return_value=None)
    display_name = mocked_ok_response["display_name"]

    with patch.dict(
        nsxt_ip_pools.__salt__,
        {
            "nsxt_ip_pools.get_by_display_name": mock_get_using_display_name_response,
            "nsxt_ip_pools.delete": mock_delete_response,
        },
    ):
        result = nsxt_ip_pools.absent(
            name="test_absent_using_basic_auth",
            hostname=mocked_hostname,
            username="username",
            password="password",
            display_name=display_name,
        )

    assert result is not None
    assert result["changes"] == {"new": None, "old": mocked_ok_response}
    assert result["comment"] == "Deleted IP Pool {}".format(display_name)
    assert bool(result["result"])


def test_absent_do_nothing_with_basic_auth():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_using_display_name_response = MagicMock(return_value={"results": []})
    display_name = mocked_ok_response["display_name"]

    with patch.dict(
        nsxt_ip_pools.__salt__,
        {"nsxt_ip_pools.get_by_display_name": mock_get_using_display_name_response},
    ):
        result = nsxt_ip_pools.absent(
            name="test_publish_using_basic_auth",
            hostname=mocked_hostname,
            username="username",
            password="password",
            display_name=display_name,
        )

    assert result is not None
    assert result["changes"] == {}
    assert result["comment"] == "No IP Address Pool found with name {}".format(display_name)
    assert bool(result["result"])


def test_absent_to_delete_in_test_mode():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_using_display_name_response = MagicMock(return_value={"results": [mocked_ok_response]})
    display_name = mocked_ok_response["display_name"]

    with patch.dict(
        nsxt_ip_pools.__salt__,
        {"nsxt_ip_pools.get_by_display_name": mock_get_using_display_name_response},
    ):
        with patch.dict(nsxt_ip_pools.__opts__, {"test": True}):
            result = nsxt_ip_pools.absent(
                name="test_absent_using_basic_auth",
                hostname=mocked_hostname,
                username="username",
                password="password",
                display_name=display_name,
            )

    assert result is not None
    assert result["changes"].__len__() == 0
    assert result["comment"] == "State absent will delete IP Pool with name {}".format(display_name)
    assert result["result"] is None


def test_absent_to_do_nothing_in_test_mode():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_using_display_name_response = MagicMock(return_value={"results": []})
    display_name = mocked_ok_response["display_name"]

    with patch.dict(
        nsxt_ip_pools.__salt__,
        {"nsxt_ip_pools.get_by_display_name": mock_get_using_display_name_response},
    ):
        with patch.dict(nsxt_ip_pools.__opts__, {"test": True}):
            result = nsxt_ip_pools.absent(
                name="test_absent_using_basic_auth",
                hostname=mocked_hostname,
                username="username",
                password="password",
                display_name=display_name,
            )

    assert result is not None
    assert result["changes"].__len__() == 0
    assert result[
        "comment"
    ] == "State absent will do nothing as no IP Pool found with name {}".format(display_name)
    assert result["result"] is None


def test_absent_when_multiple_pools_with_same_display_name():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_using_display_name_response = MagicMock(
        return_value={"results": [mocked_ok_response, mocked_ok_response]}
    )
    display_name = mocked_ok_response["display_name"]

    with patch.dict(
        nsxt_ip_pools.__salt__,
        {"nsxt_ip_pools.get_by_display_name": mock_get_using_display_name_response},
    ):
        with patch.dict(nsxt_ip_pools.__opts__, {"test": True}):
            result = nsxt_ip_pools.absent(
                name="test_absent_using_basic_auth",
                hostname=mocked_hostname,
                username="username",
                password="password",
                display_name=display_name,
            )

    assert result is not None
    assert result["changes"].__len__() == 0
    assert result["comment"] == "Multiple IP Pools found for the provided display name {}".format(
        display_name
    )
    assert not result["result"]


def test_absent_with_error_from_update():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_using_display_name = MagicMock(return_value={"results": [mocked_ok_response]})
    mock_create = MagicMock(return_value=mocked_error_response)

    with patch.dict(
        nsxt_ip_pools.__salt__,
        {
            "nsxt_ip_pools.get_by_display_name": mock_get_using_display_name,
            "nsxt_ip_pools.delete": mock_create,
        },
    ):
        result = nsxt_ip_pools.absent(
            name="test_present_using_basic_auth",
            hostname=mocked_hostname,
            username="username",
            password="password",
            description="Sample description",
            display_name=mocked_ok_response["display_name"],
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not bool(result["result"])
