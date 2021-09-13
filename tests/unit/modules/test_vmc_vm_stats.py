"""
    Unit tests for vmc_vm_stats execution module
"""
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_vm_stats as vmc_vm_stats


@pytest.fixture()
def cpu_setting_data(mock_vmc_vcenter_request_call_api):
    data = {
        "hot_remove_enabled": False,
        "count": 4,
        "hot_add_enabled": False,
        "cores_per_socket": 1,
    }
    mock_vmc_vcenter_request_call_api.return_value = data
    yield data


def test_get_should_return_api_response_with_cpu_settings(mock_vcenter_headers, cpu_setting_data):
    result = vmc_vm_stats.get(
        hostname="hostname",
        username="username",
        password="password",
        vm_id="vm_id",
        stats_type="cpu",
        verify_ssl=False,
    )
    assert result == cpu_setting_data


def test_get_called_with_url(mock_vcenter_headers):
    expected_url = "https://hostname/api/vcenter/vm/vm_id/hardware/memory"
    with patch("saltext.vmware.utils.vmc_vcenter_request.call_api", autospec=True) as vmc_call_api:
        vmc_vm_stats.get(
            hostname="hostname",
            username="username",
            password="password",
            vm_id="vm_id",
            stats_type="memory",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
