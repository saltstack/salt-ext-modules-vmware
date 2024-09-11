"""
Unit Tests for compliance control execution module.
"""

import logging
from unittest.mock import patch

import pytest
import salt.exceptions
import saltext.vmware.modules.compliance_control as compliance_control

log = logging.getLogger(__name__)


@pytest.fixture
def configure_loader_modules():
    return {compliance_control: {"__opts__": {}, "__pillar__": {}}}


@pytest.fixture(autouse=True)
def patch_salt_loaded_objects():
    with patch(
        "saltext.vmware.modules.compliance_control.__opts__",
        {
            "saltext.vmware": {"host": "test.vcenter.local", "user": "test", "password": "test"},
        },
        create=True,
    ), patch.object(compliance_control, "__pillar__", {}, create=True), patch.object(
        compliance_control, "__salt__", {}, create=True
    ):
        yield


@pytest.mark.parametrize(
    "exception",
    [False, True],
)
def test_control_config_compliance_check(exception):
    # mock auth
    patch_auth_context = patch(
        "saltext.vmware.utils.compliance_control.create_auth_context",
        autospec=True,
        return_value={},
    )
    # mock successful compliance check
    mock_response = {"status": "COMPLIANT"}
    patch_compliance_check = patch(
        "config_modules_vmware.interfaces.controller_interface.ControllerInterface.check_compliance",
        autospec=True,
        return_value=mock_response,
    )
    # mock exception in compliance check
    patch_compliance_check_exception = patch(
        "config_modules_vmware.interfaces.controller_interface.ControllerInterface.check_compliance",
        autospec=True,
        side_effect=Exception("Testing"),
    )
    # mock input
    mock_control_config = {
        "compliance_config": {
            "vcenter": {
                "ntp": {
                    "value": {"mode": "NTP", "servers": ["ntp server"]},
                    "metadata": {"configuration_id": "1246", "configuration_title": "time server"},
                }
            }
        }
    }
    if not exception:
        with patch_auth_context and patch_compliance_check:
            compliance_check_response = compliance_control.control_config_compliance_check(
                mock_control_config, product="vcenter"
            )
            assert compliance_check_response == mock_response
    else:
        with patch_auth_context and patch_compliance_check_exception:
            with pytest.raises(salt.exceptions.VMwareRuntimeError):
                compliance_control.control_config_compliance_check(
                    mock_control_config, product="vcenter"
                )


@pytest.mark.parametrize(
    "exception",
    [False, True],
)
def test_control_config_remediate(exception):
    # mock auth
    patch_auth_context = patch(
        "saltext.vmware.utils.compliance_control.create_auth_context",
        autospec=True,
        return_value={},
    )
    # mock successful remediation
    mock_response = {"status": "SUCCESS"}
    patch_remediate = patch(
        "config_modules_vmware.interfaces.controller_interface.ControllerInterface.remediate_with_desired_state",
        autospec=True,
        return_value=mock_response,
    )
    # mock exception in remediation
    patch_remediate_exception = patch(
        "config_modules_vmware.interfaces.controller_interface.ControllerInterface.remediate_with_desired_state",
        autospec=True,
        side_effect=Exception("Testing"),
    )
    # mock input
    mock_control_config = {
        "compliance_config": {
            "vcenter": {
                "ntp": {
                    "value": {"mode": "NTP", "servers": ["ntp server"]},
                    "metadata": {"configuration_id": "1246", "configuration_title": "time server"},
                }
            }
        }
    }
    if not exception:
        with patch_auth_context and patch_remediate:
            remediate_response = compliance_control.control_config_remediate(
                mock_control_config, product="vcenter"
            )
            assert remediate_response == mock_response

        # Error in remediation test with invalid fields
        mock_control_config.update({"invalid_field": "invalid"})
        error_response = compliance_control.control_config_remediate(
            mock_control_config, product="vcenter"
        )
        assert error_response["status"] == "ERROR"
    else:
        with patch_auth_context and patch_remediate_exception:
            with pytest.raises(salt.exceptions.VMwareRuntimeError):
                compliance_control.control_config_remediate(mock_control_config, product="vcenter")
