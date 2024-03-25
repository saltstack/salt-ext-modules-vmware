"""
    Unit Tests for content library state
"""
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from saltext.vmware.states import content_library

dummy_list_detailed = {
    "existing": {
        "creation_time": "2022-12-14T14:46:13.538Z",
        "storage_backings": [{"datastore_id": "datastore-35032", "type": "DATASTORE"}],
        "last_modified_time": "2022-12-14T14:47:42.785Z",
        "server_guid": "cc6c3419-d4e3-4253-864d-7150e1be1430",
        "description": "Modified 1",
        "type": "LOCAL",
        "version": "3",
        "name": "existing",
        "publish_info": {
            "authentication_method": "NONE",
            "published": True,
            "publish_url": "https://vc-l-01a.corp.local:443/cls/vcsp/lib/d9e26762-493c-4722-856d-ca00097269b5/lib.json",
            "persist_json_enabled": False,
        },
        "id": "d9e26762-493c-4722-856d-ca00097269b5",
    }
}

dummy_config_unchanged = [
    {
        "name": "existing",
        "published": True,
    }
]

dummy_config_existing = [
    {
        "name": "existing",
        "published": False,
    }
]

dummy_config_new = [{"name": "new", "published": False, "datastore": "datastore-35032"}]

dummy_expected_changes_existing = {"existing": {"published": False}}

dummy_expected_changes_new = {"new": {"published": False, "datastore": "datastore-35032"}}


@pytest.fixture
def configure_loader_modules():
    return {content_library: {}}


def test_content_library_local_state_test_existing():
    content_library.connect = Mock()
    mock_list = Mock(return_value=dummy_list_detailed)

    with patch.dict(
        content_library.__salt__,
        {
            "vsphere_content_library.list_detailed": mock_list,
        },
    ):
        with patch.dict(content_library.__opts__, {"test": True}):
            result = content_library.local("", dummy_config_existing)

    assert result is not None
    assert result["result"]
    assert result["changes"]["new"] == dummy_expected_changes_existing
    mock_list.assert_called()


def test_content_library_local_state_existing():
    content_library.connect = Mock()
    mock_list = Mock(return_value=dummy_list_detailed)
    mock_create = Mock()

    with patch.dict(
        content_library.__salt__,
        {
            "vsphere_content_library.list_detailed": mock_list,
            "vsphere_content_library.update": mock_create,
        },
    ):
        with patch.dict(content_library.__opts__, {"test": False}):
            result = content_library.local("", dummy_config_existing)

    assert result is not None
    assert result["result"]
    assert result["changes"]["new"] == dummy_expected_changes_existing
    mock_list.assert_called()
    mock_create.assert_called()


def test_content_library_local_state_test_new():
    content_library.connect = Mock()
    mock_list = Mock(return_value=dummy_list_detailed)

    with patch.dict(
        content_library.__salt__,
        {
            "vsphere_content_library.list_detailed": mock_list,
        },
    ):
        with patch.dict(content_library.__opts__, {"test": True}):
            result = content_library.local("", dummy_config_new)

    assert result is not None
    assert result["result"]
    assert result["changes"]["new"] == dummy_expected_changes_new
    mock_list.assert_called()


def test_content_library_local_state_new():
    content_library.connect = Mock()
    mock_list = Mock(return_value=dummy_list_detailed)
    mock_create = Mock()

    with patch.dict(
        content_library.__salt__,
        {
            "vsphere_content_library.list_detailed": mock_list,
            "vsphere_content_library.create": mock_create,
        },
    ):
        with patch.dict(content_library.__opts__, {"test": False}):
            result = content_library.local("", dummy_config_new)

    assert result is not None
    assert result["result"]
    assert result["changes"]["new"] == dummy_expected_changes_new
    mock_list.assert_called()
    mock_create.assert_called()


def test_get_advanced_config_unchanged():
    content_library.connect = MagicMock()
    mock_list = Mock(return_value=dummy_list_detailed)

    with patch.dict(
        content_library.__salt__,
        {
            "vsphere_content_library.list_detailed": mock_list,
        },
    ):
        with patch.dict(content_library.__opts__, {"test": False}):
            result = content_library.local("", dummy_config_unchanged)

    assert result is not None
    assert result["changes"]["new"]["existing"] == {}
    assert result["result"]
    mock_list.assert_called()
