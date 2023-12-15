"""
    :codeauthor: VMware
"""
import logging
from unittest.mock import patch

import pytest
import salt.exceptions
import saltext.vmware.modules.compliance_control as compliance_control

log = logging.getLogger(__name__)


@pytest.fixture
def tgz_file(session_temp_dir):
    tgz = session_temp_dir / "vmware.tgz"
    tgz.write_bytes(b"1")
    yield tgz


@pytest.fixture
def configure_loader_modules():
    return {compliance_control: {"__opts__": {}, "__pillar__": {}}}


@pytest.fixture(autouse=True)
def patch_salt_loaded_objects():
    # This esxi needs to be the same as the module we're importing
    with patch(
        "saltext.vmware.modules.compliance_control.__opts__",
        {
            "cachedir": ".",
            "saltext.vmware": {"host": "fnord.example.com", "user": "fnord", "password": "fnord"},
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
    mock_response = {"status": "COMPLIANT"}

    patch_compliance_check = patch(
        "config_modules_vmware.control_module.control_config.ControlConfig.check_compliance",
        autospec=True,
        return_value=mock_response,
    )
    patch_control_config_obj = patch(
        "saltext.vmware.utils.vc.create_control_config", autospec=True, return_value={}
    )
    patch_compliance_check_exception = patch(
        "config_modules_vmware.control_module.control_config.ControlConfig.check_compliance",
        autospec=True,
        side_effect=Exception("Testing"),
    )
    mock_conrtol_config = {
        "compliance_config": {
            "network_policy": {
                "ntp": {
                    "value": {"mode": "NTP", "servers": ["ntp server"]},
                    "metadata": {"configuration_id": "1246", "configuration_title": "time server"},
                }
            }
        }
    }
    if exception:
        with patch_control_config_obj:
            with patch_compliance_check_exception:
                with pytest.raises(salt.exceptions.VMwareRuntimeError):
                    compliance_control.control_config_compliance_check(
                        mock_conrtol_config, product="vcenter"
                    )
    else:
        with patch_compliance_check:
            control_config_check_response = compliance_control.control_config_compliance_check(
                mock_conrtol_config, product="vcenter"
            )
            assert control_config_check_response == mock_response


@pytest.mark.parametrize(
    "exception",
    [False, True],
)
def test_control_config_remediate(exception):
    mock_response = {"status": "SUCCESS"}

    patch_remediate = patch(
        "config_modules_vmware.control_module.control_config.ControlConfig.remediate_with_desired_state",
        autospec=True,
        return_value=mock_response,
    )
    mock_conrtol_config = {
        "compliance_config": {
            "network_policy": {
                "ntp": {
                    "value": {"mode": "NTP", "servers": ["ntp server"]},
                    "metadata": {"configuration_id": "1246", "configuration_title": "time server"},
                }
            }
        }
    }
    if exception:
        with pytest.raises(salt.exceptions.VMwareRuntimeError):
            compliance_control.control_config_remediate(mock_conrtol_config, product="vcenter")
    else:
        with patch_remediate:
            control_config_remediate_response = compliance_control.control_config_remediate(
                mock_conrtol_config, product="vcenter"
            )
            assert control_config_remediate_response == mock_response
