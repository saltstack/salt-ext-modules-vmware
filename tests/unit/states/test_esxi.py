"""
    Unit Tests for esxi state
"""
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from saltext.vmware.states import esxi

dummy_advanced_config = {
    "host1": {
        "config1": "old",
        "config2": "new",
    },
    "host2": {
        "config1": "old",
        "config2": "old",
    },
}

dummy_advanced_config_new = {
    "host1": {
        "config1": "new",
        "config2": "new",
    },
    "host2": {
        "config1": "new",
        "config2": "new",
    },
}

dummy_desired_advanced_config = {
    "config1": "new",
    "config2": "new",
}

dummy_expected_advanced_config_changes_less = {
    "host1": {
        "config1": "old",
    },
    "host2": {
        "config1": "old",
        "config2": "old",
    },
}


@pytest.fixture
def configure_loader_modules():
    return {esxi: {}}


def test_get_advanced_config_success_test_less():
    mock_get_advanced_config = MagicMock(return_value=dummy_advanced_config)
    esxi.connect = MagicMock()

    with patch.dict(esxi.__salt__, {"vmware_esxi.get_advanced_config": mock_get_advanced_config}):
        with patch.dict(esxi.__opts__, {"test": True}):
            result = esxi.advanced_configs(configs=dummy_desired_advanced_config, less=True)


def test_get_advanced_config_success_less():
    mock_get_advanced_config = MagicMock(return_value=dummy_advanced_config)
    mock_set_advanced_config = MagicMock()
    esxi.connect = MagicMock()

    with patch.dict(
        esxi.__salt__,
        {
            "vmware_esxi.get_advanced_config": mock_get_advanced_config,
            "vmware_esxi.set_advanced_configs": mock_set_advanced_config,
        },
    ):
        with patch.dict(esxi.__opts__, {"test": False}):
            result = esxi.advanced_configs(configs=dummy_desired_advanced_config, less=True)

    assert result is not None
    assert result["changes"] == dummy_expected_advanced_config_changes_less
    assert result["result"]
    mock_set_advanced_config.assert_called()


def test_get_advanced_config_no_changes():
    mock_get_advanced_config = MagicMock(return_value=dummy_advanced_config_new)
    mock_set_advanced_config = MagicMock()
    esxi.connect = MagicMock()

    with patch.dict(
        esxi.__salt__,
        {
            "vmware_esxi.get_advanced_config": mock_get_advanced_config,
            "vmware_esxi.set_advanced_configs": mock_set_advanced_config,
        },
    ):
        with patch.dict(esxi.__opts__, {"test": False}):
            result = esxi.advanced_configs(configs=dummy_desired_advanced_config, less=True)

    assert result is not None
    assert result["changes"] == {}
    assert result["result"]
    mock_set_advanced_config.assert_not_called()


def test_get_advanced_config_test_verbose_changes():
    mock_get_advanced_config = MagicMock(return_value=dummy_advanced_config)
    esxi.connect = MagicMock()

    with patch.dict(esxi.__salt__, {"vmware_esxi.get_advanced_config": mock_get_advanced_config}):
        with patch.dict(esxi.__opts__, {"test": True}):
            result = esxi.advanced_configs(configs=dummy_desired_advanced_config, less=False)

    assert result is not None
    assert result["result"]


def test_get_advanced_config_verbose_changes():
    mock_get_advanced_config = MagicMock(return_value=dummy_advanced_config)
    mock_set_advanced_config = MagicMock()
    esxi.connect = MagicMock()

    with patch.dict(
        esxi.__salt__,
        {
            "vmware_esxi.get_advanced_config": mock_get_advanced_config,
            "vmware_esxi.set_advanced_configs": mock_set_advanced_config,
        },
    ):
        with patch.dict(esxi.__opts__, {"test": False}):
            result = esxi.advanced_configs(configs=dummy_desired_advanced_config, less=False)

    assert result is not None
    assert result["result"]
    mock_set_advanced_config.assert_called()
