"""
Unit Tests for compliance control state module.
"""
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from saltext.vmware.states import compliance_control

NAME = "test"


@pytest.fixture
def configure_loader_modules():
    return {compliance_control: {"__opts__": {}, "__pillar__": {}}}


@pytest.fixture(autouse=True)
def patch_salt_loaded_objects():
    with patch(
        "saltext.vmware.states.compliance_control.__opts__",
        {
            "saltext.vmware": {"host": "test.vcenter.local", "user": "test", "password": "test"},
        },
        create=True,
    ), patch.object(compliance_control, "__pillar__", {}, create=True), patch.object(
        compliance_control, "__salt__", {}, create=True
    ):
        yield


def mock_valid_control_config():
    return {
        "compliance_config": {
            "vcenter": {
                "ntp": {
                    "value": {"mode": "NTP", "servers": ["ntp server"]},
                    "metadata": {"configuration_id": "1246", "configuration_title": "time server"},
                }
            }
        }
    }


def mock_missing_product_control_config():
    return {
        "compliance_config": {
            "invalid": {
                "ntp": {
                    "value": {"mode": "NTP", "servers": ["ntp server"]},
                    "metadata": {"configuration_id": "1246", "configuration_title": "time server"},
                }
            }
        }
    }


@pytest.mark.parametrize(
    "mock_input, expected_status, expected_comment, expected_result, test_mode",
    [
        (mock_valid_control_config(), {"status": "COMPLIANT"}, "COMPLIANT", True, True),
        (mock_valid_control_config(), {"status": "SKIPPED"}, "SKIPPED", True, True),
        (mock_valid_control_config(), {"status": "NON_COMPLIANT"}, "NON_COMPLIANT", None, True),
        (mock_valid_control_config(), {"status": "FAILED"}, "FAILED", False, True),
        (
            mock_valid_control_config(),
            {"status": "ERROR"},
            "Failed to run compliance check. Please check changes for more details.",
            False,
            True,
        ),
        (
            mock_missing_product_control_config(),
            {"status": "ERROR"},
            "Desired spec is empty for vcenter",
            None,
            True,
        ),
        (
            mock_valid_control_config(),
            {"status": "SUCCESS"},
            "Remediation completed successfully.",
            True,
            False,
        ),
        (mock_valid_control_config(), {"status": "SKIPPED"}, "Nothing to remediate.", True, False),
        (mock_valid_control_config(), {"status": "FAILED"}, "Remediation failed.", False, False),
        (
            mock_valid_control_config(),
            {"status": "PARTIAL"},
            "Remediation completed with status partial.",
            False,
            False,
        ),
        (mock_valid_control_config(), {"status": "ERROR"}, "ERROR", False, False),
        (
            {},
            None,
            "An error occurred: Desired spec is empty or not in correct format",
            False,
            False,
        ),
    ],
)
def test_check_control_config(
    mock_input, expected_status, expected_comment, expected_result, test_mode
):
    mock_check_control_compliance_config = MagicMock(return_value=expected_status)
    mock_check_control_remediate_config = MagicMock(return_value=expected_status)

    with patch.dict(
        compliance_control.__salt__,
        {
            "vmware_compliance_control.control_config_compliance_check": mock_check_control_compliance_config,
            "vmware_compliance_control.control_config_remediate": mock_check_control_remediate_config,
        },
    ):
        with patch.dict(compliance_control.__opts__, {"test": test_mode}):
            result = compliance_control.check_control(
                name=NAME, control_config=mock_input, product="vcenter"
            )

    assert result is not None
    assert result["comment"] == expected_comment
    assert result["result"] == expected_result
