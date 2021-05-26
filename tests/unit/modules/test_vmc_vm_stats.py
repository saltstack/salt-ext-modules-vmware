"""
    Unit tests for vmc_vm_stats execution module
"""

from __future__ import absolute_import
import saltext.vmware.modules.vmc_vm_stats as vmc_vm_stats
from saltext.vmware.utils import vmc_vcenter_request, vmc_constants
from unittest.mock import patch


_get_stat_data = {
    "hot_remove_enabled": False,
    "count": 4,
    "hot_add_enabled": False,
    "cores_per_socket": 1
}


@patch.object(vmc_vcenter_request, 'call_api')
@patch.object(vmc_vcenter_request, 'get_headers')
def test_get_should_return_api_response_with_cpu_settings(mock_get_headers, mock_call_api):
    mock_call_api.return_value = _get_stat_data
    mock_get_headers.return_value = {vmc_constants.VMWARE_API_SESSION_ID: "api-session-id"}
    assert vmc_vm_stats.get(hostname="hostname",
                            username="username",
                            password="password",
                            vm_id="vm_id",
                            stats_type="cpu",
                            verify_ssl=False) == _get_stat_data
