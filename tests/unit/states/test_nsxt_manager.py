"""
    Unit Tests for nsxt_manager state
"""
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import saltext.vmware.states.nsxt_manager as nsxt_manager

_mocked_response_enabled = {"publish_fqdns": True, "_revision": 1}
_mocked_response_disabled = {"publish_fqdns": False, "_revision": 1}
_mocked_auth_error = {
    "error": "The credentials were incorrect or the account specified has been locked."
}
_mocked_error_response = {
    "module_name": "common-services",
    "error_message": "The credentials were incorrect or the account specified has been locked.",
    "error_code": 403,
}
_mocked_hostname = "nsx-t.vmware.com"


@pytest.fixture
def configure_loader_modules():
    return {nsxt_manager: {}}


def test_publish_fqdns_enabled_without_parameters():
    with pytest.raises(TypeError) as exc:
        nsxt_manager.publish_fqdns_enabled()

        assert (
            str(exc.value)
            == "publish_fqdns_enabled() missing 4 required positional arguments: 'name', "
            "'hostname', 'username', and 'password'"
        )


def test_publish_fqdns_disabled_without_parameters():
    with pytest.raises(TypeError) as exc:
        nsxt_manager.publish_fqdns_disabled()

    assert (
        str(exc.value)
        == "publish_fqdns_disabled() missing 4 required positional arguments: 'name', "
        "'hostname', 'username', and 'password'"
    )


def test_publish_fqdns_enabled_with_execution_error():
    mock_set_manager_config_output = MagicMock(return_value=_mocked_response_enabled)
    mock_get_manager_config_output = MagicMock(return_value=_mocked_auth_error)

    with patch.dict(
        nsxt_manager.__salt__,
        {
            "nsxt_manager.get_manager_config": mock_get_manager_config_output,
            "nsxt_manager.set_manager_config": mock_set_manager_config_output,
        },
    ):
        result = nsxt_manager.publish_fqdns_enabled(
            name="test_publish_using_basic_auth",
            hostname=_mocked_hostname,
            username="username",
            password="password",
        )

    assert result
    assert {} == result["changes"]
    assert (
        "The credentials were incorrect or the account specified has been locked."
        == result["comment"]
    )
    assert result["result"] == False


def test_publish_fqdns_enabled_when_disabled_with_basic_auth():
    mock_set_manager_config_output = MagicMock(return_value=_mocked_response_enabled)
    mock_get_manager_config_output = MagicMock(return_value=_mocked_response_disabled)

    with patch.dict(
        nsxt_manager.__salt__,
        {
            "nsxt_manager.get_manager_config": mock_get_manager_config_output,
            "nsxt_manager.set_manager_config": mock_set_manager_config_output,
        },
    ):
        result = nsxt_manager.publish_fqdns_enabled(
            name="test_publish_using_basic_auth",
            hostname=_mocked_hostname,
            username="username",
            password="password",
        )

    assert result
    assert {"new": _mocked_response_enabled, "old": _mocked_response_disabled} == result["changes"]
    assert "publish_fqdns has been set to True" == result["comment"]
    assert result["result"] == True


def test_publish_fqdns_disabled_when_enabled_with_basic_auth():
    mock_set_manager_config_output = MagicMock(return_value=_mocked_response_disabled)
    mock_get_manager_config_output = MagicMock(return_value=_mocked_response_enabled)

    with patch.dict(
        nsxt_manager.__salt__,
        {
            "nsxt_manager.get_manager_config": mock_get_manager_config_output,
            "nsxt_manager.set_manager_config": mock_set_manager_config_output,
        },
    ):
        result = nsxt_manager.publish_fqdns_disabled(
            name="test_publish_using_basic_auth",
            hostname=_mocked_hostname,
            username="username",
            password="password",
        )

    assert result
    assert {"new": _mocked_response_disabled, "old": _mocked_response_enabled} == result["changes"]
    assert "publish_fqdns has been set to False" == result["comment"]
    assert result["result"] == True


def test_publish_fqdns_enabled_when_enabled_with_basic_auth():
    mock_set_manager_config_output = MagicMock(return_value=_mocked_response_enabled)
    mock_get_manager_config_output = MagicMock(return_value=_mocked_response_enabled)

    with patch.dict(
        nsxt_manager.__salt__,
        {
            "nsxt_manager.get_manager_config": mock_get_manager_config_output,
            "nsxt_manager.set_manager_config": mock_set_manager_config_output,
        },
    ):
        result = nsxt_manager.publish_fqdns_enabled(
            name="test_publish_using_basic_auth",
            hostname=_mocked_hostname,
            username="username",
            password="password",
        )

    assert result
    assert {} == result["changes"]
    assert "publish_fqdns is already set to True" == result["comment"]
    assert result["result"] == True


def test_publish_fqdns_disabled_when_disabled_with_basic_auth():
    mock_set_manager_config_output = MagicMock(return_value=_mocked_response_disabled)
    mock_get_manager_config_output = MagicMock(return_value=_mocked_response_disabled)

    with patch.dict(
        nsxt_manager.__salt__,
        {
            "nsxt_manager.get_manager_config": mock_get_manager_config_output,
            "nsxt_manager.set_manager_config": mock_set_manager_config_output,
        },
    ):
        result = nsxt_manager.publish_fqdns_disabled(
            name="test_publish_using_basic_auth",
            hostname=_mocked_hostname,
            username="username",
            password="password",
        )

    assert result
    assert {} == result["changes"]
    assert "publish_fqdns is already set to False" == result["comment"]
    assert result["result"] == True


def test_publish_fqdns_disabled_test_mode():
    mock_get_manager_config_output = MagicMock(return_value=_mocked_response_disabled)

    with patch.dict(
        nsxt_manager.__salt__,
        {"nsxt_manager.get_manager_config": mock_get_manager_config_output},
    ):
        with patch.dict(nsxt_manager.__opts__, {"test": True}):
            result = nsxt_manager.publish_fqdns_disabled(
                name="test_publish_using_basic_auth",
                hostname=_mocked_hostname,
                username="username",
                password="password",
            )

    assert result
    assert {} == result["changes"]
    assert (
        "State publish_fqdns_disabled will execute with params test_publish_using_basic_auth, nsx-t.vmware.com, "
        "username, password, True" == result["comment"]
    )
    assert result["result"] is None


def test_publish_fqdns_enabled_test_mode():
    mock_get_manager_config_output = MagicMock(return_value=_mocked_response_disabled)

    with patch.dict(
        nsxt_manager.__salt__,
        {"nsxt_manager.get_manager_config": mock_get_manager_config_output},
    ):
        with patch.dict(nsxt_manager.__opts__, {"test": True}):
            result = nsxt_manager.publish_fqdns_enabled(
                name="test_publish_using_basic_auth",
                hostname=_mocked_hostname,
                username="username",
                password="password",
            )

    assert result
    assert {} == result["changes"]
    assert (
        "State publish_fqdns_enabled will execute with params test_publish_using_basic_auth, nsx-t.vmware.com, "
        "username, password, True" == result["comment"]
    )
    assert result["result"] is None
