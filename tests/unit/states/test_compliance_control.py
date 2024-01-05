"""
    Unit Tests for esxi state
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
    # This esxi needs to be the same as the module we're importing
    with patch(
        "saltext.vmware.states.compliance_control.__opts__",
        {
            "cachedir": ".",
            "saltext.vmware": {"host": "test.vcenter.local", "user": "test", "password": "test"},
        },
        create=True,
    ), patch.object(compliance_control, "__pillar__", {}, create=True), patch.object(
        compliance_control, "__salt__", {}, create=True
    ):
        yield


@pytest.mark.parametrize(
    "expected_status, expected_comment, expected_result, test_mode",
    [
        ({"status": "SUCCESS"}, "Remediation completed successfully.", True, False),
        ({"status": "FAILED"}, "Remediation failed.", False, False),
        ({"status": "ERROR"}, "ERROR", False, False),
        ({"status": "COMPLIANT"}, "COMPLIANT", True, True),
        ({"status": "NON_COMPLIANT"}, "NON_COMPLIANT", False, True),
        (
            {"status": "ERROR"},
            "Failed to run compliance check. Please check changes for more details.",
            False,
            True,
        ),
    ],
)
def test_check_control_config(expected_status, expected_comment, expected_result, test_mode):
    mock_check_control_compliance_config = MagicMock(return_value=expected_status)
    mock_check_control_remediate_config = MagicMock(return_value=expected_status)
    mock_conrtol_config = {
        "compliance_config": {
            "networking": {
                "ntp": {
                    "value": {"mode": "NTP", "servers": ["ntp server"]},
                    "metadata": {"configuration_id": "1246", "configuration_title": "time server"},
                }
            }
        }
    }

    with patch.dict(
        compliance_control.__salt__,
        {
            "vmware_compliance_control.control_config_compliance_check": mock_check_control_compliance_config,
            "vmware_compliance_control.control_config_remediate": mock_check_control_remediate_config,
        },
    ):
        with patch.dict(compliance_control.__opts__, {"test": test_mode}):
            result = compliance_control.check_control(
                name=NAME, control_config=mock_conrtol_config, product="vcenter"
            )

    assert result is not None
    assert result["comment"] == expected_comment
    assert result["result"] == expected_result
    # mock_check_control_remediate_config.assert_called()
