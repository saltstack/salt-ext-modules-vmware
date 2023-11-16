"""
    Unit Tests for esxi state
"""
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import saltext.vmware.utils.esxi
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
    "host2": {
        "new": {"config1": "new", "config2": "new"},
        "old": {"config1": "old", "config2": "old"},
    },
    "host1": {
        "new": {"config1": "new"},
        "old": {"config1": "old"},
    },
}


NAME = "test"


@pytest.fixture
def configure_loader_modules():
    return {esxi: {}}


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
            result = esxi.advanced_configs(name=NAME, configs=dummy_desired_advanced_config)

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
            result = esxi.advanced_configs(name=NAME, configs=dummy_desired_advanced_config)

    assert result is not None
    assert result["changes"] == {}
    assert result["result"]
    mock_set_advanced_config.assert_not_called()


def test_get_advanced_config_test_verbose_changes():
    mock_get_advanced_config = MagicMock(return_value=dummy_advanced_config)
    esxi.connect = MagicMock()

    with patch.dict(esxi.__salt__, {"vmware_esxi.get_advanced_config": mock_get_advanced_config}):
        with patch.dict(esxi.__opts__, {"test": True}):
            result = esxi.advanced_configs(name=NAME, configs=dummy_desired_advanced_config)

    assert result is not None
    assert result["result"] is None


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
            result = esxi.advanced_configs(name=NAME, configs=dummy_desired_advanced_config)

    assert result is not None
    assert result["result"]
    mock_set_advanced_config.assert_called()


def test_remediate_success():
    # Assign
    name = "test_name"
    cluster_paths = "/SDDC-Datacenter/vlcm_cluster1"
    desired_config = {"some_key": "some_value"}
    profile = "my_profile"

    # Mock required functions
    saltext.vmware.utils.esxi.create_esx_config = MagicMock(return_value={"some-key": "some-value"})
    mock_pre_check = MagicMock(return_value={"status": True})
    mock_remediate = MagicMock(return_value={"status": True})

    # Act
    with patch.dict(
        esxi.__salt__,
        {
            "vmware_esxi.pre_check": mock_pre_check,
            "vmware_esxi.remediate": mock_remediate,
        },
    ):
        with patch.dict(esxi.__opts__, {"test": False}):
            result = esxi.remediate(name, cluster_paths, desired_config, profile)

    # Assertions
    assert result["result"]
    assert result["comment"] == "Configuration remediated successfully"
    assert "remediate" in result["changes"]

    mock_pre_check.assert_called_once_with(
        cluster_paths=cluster_paths,
        desired_state_spec=desired_config,
        esx_config={"some-key": "some-value"},
    )
    mock_remediate.assert_called_once_with(
        cluster_paths=cluster_paths,
        desired_state_spec=desired_config,
        esx_config={"some-key": "some-value"},
    )


def test_remediate_test_mode():
    # Assign
    name = "test_name"
    cluster_paths = "/SDDC-Datacenter/vlcm_cluster1"
    desired_config = {"some_key": "some_value"}
    profile = "my_profile"

    # Mock required functions
    saltext.vmware.utils.esxi.create_esx_config = MagicMock(return_value={"some-key": "some-value"})
    mock_pre_check = MagicMock(return_value={"status": True})
    mock_remediate = MagicMock(return_value={"status": True})

    # Act
    with patch.dict(
        esxi.__salt__,
        {
            "vmware_esxi.pre_check": mock_pre_check,
            "vmware_esxi.remediate": mock_remediate,
        },
    ):
        with patch.dict(esxi.__opts__, {"test": True}):
            result = esxi.remediate(name, cluster_paths, desired_config, profile)
    # Assert
    assert result["result"] is None
    assert "pre_check" in result["changes"]
    assert (
        result["comment"] == "Pre-check completed successfully. You can continue with remediation."
    )

    mock_pre_check.assert_called_once_with(
        cluster_paths=cluster_paths,
        desired_state_spec=desired_config,
        esx_config={"some-key": "some-value"},
    )
    mock_remediate.assert_not_called()


def test_remediate_precheck_fail():
    # Assign
    name = "test_name"
    cluster_paths = "/SDDC-Datacenter/vlcm_cluster1"
    desired_config = {"some_key": "some_value"}
    profile = "my_profile"

    # Mock required functions
    saltext.vmware.utils.esxi.create_esx_config = MagicMock(return_value={"some-key": "some-value"})
    mock_pre_check = MagicMock(return_value={"status": False, "details": "Pre-check failed"})
    mock_remediate = MagicMock(return_value={"status": True})

    # Act
    with patch.dict(
        esxi.__salt__,
        {
            "vmware_esxi.pre_check": mock_pre_check,
            "vmware_esxi.remediate": mock_remediate,
        },
    ):
        with patch.dict(esxi.__opts__, {"test": False}):
            result = esxi.remediate(name, cluster_paths, desired_config, profile)

    # Assert
    assert not result["result"]
    assert result["comment"] == "Pre-check failed."
    mock_pre_check.assert_called_once_with(
        cluster_paths=cluster_paths,
        desired_state_spec=desired_config,
        esx_config={"some-key": "some-value"},
    )
    mock_remediate.assert_not_called()


def test_remediate_remediation_fail():
    # Assign
    name = "test_name"
    cluster_paths = "/SDDC-Datacenter/vlcm_cluster1"
    desired_config = {"some_key": "some_value"}
    profile = "my_profile"

    # Mock required functions
    saltext.vmware.utils.esxi.create_esx_config = MagicMock(return_value={"some-key": "some-value"})
    mock_pre_check = MagicMock(return_value={"status": True})
    mock_remediate = MagicMock(return_value={"status": False, "details": "Remediation failed"})

    # Act
    with patch.dict(
        esxi.__salt__,
        {
            "vmware_esxi.pre_check": mock_pre_check,
            "vmware_esxi.remediate": mock_remediate,
        },
    ):
        with patch.dict(esxi.__opts__, {"test": False}):
            result = esxi.remediate(name, cluster_paths, desired_config, profile)

    # Assert
    assert not result["result"]
    assert result["comment"] == "Remediation failed."
    mock_pre_check.assert_called_once_with(
        cluster_paths=cluster_paths,
        desired_state_spec=desired_config,
        esx_config={"some-key": "some-value"},
    )
    mock_remediate.assert_called_once_with(
        cluster_paths=cluster_paths,
        desired_state_spec=desired_config,
        esx_config={"some-key": "some-value"},
    )


def test_remediate_exception():
    # Assign
    name = "test_name"
    cluster_paths = "/SDDC-Datacenter/vlcm_cluster1"
    desired_config = {"some_key": "some_value"}
    profile = "my_profile"
    # Mock required functions
    saltext.vmware.utils.esxi.create_esx_config = MagicMock(return_value={"some-key": "some-value"})
    mock_pre_check = MagicMock(return_value={"status": True})
    mock_remediate = MagicMock()
    mock_remediate.side_effect = Exception("Some error")

    # Act
    with patch.dict(
        esxi.__salt__,
        {
            "vmware_esxi.pre_check": mock_pre_check,
            "vmware_esxi.remediate": mock_remediate,
        },
    ):
        with patch.dict(esxi.__opts__, {"test": False}):
            result = esxi.remediate(name, cluster_paths, desired_config, profile)
    # Assert
    assert not result["result"]
    assert result["comment"] == "An error occurred during remediation: Some error"

    mock_pre_check.assert_called_once_with(
        cluster_paths=cluster_paths,
        desired_state_spec=desired_config,
        esx_config={"some-key": "some-value"},
    )
    mock_remediate.assert_called_once_with(
        cluster_paths=cluster_paths,
        desired_state_spec=desired_config,
        esx_config={"some-key": "some-value"},
    )
