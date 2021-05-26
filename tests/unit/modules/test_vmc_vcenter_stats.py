"""
    Unit tests for vmc_vcenter_stats execution module
"""

from __future__ import absolute_import
import saltext.vmware.modules.vmc_vcenter_stats as vmc_vcenter_stats
from saltext.vmware.utils import vmc_vcenter_request, vmc_constants
from unittest.mock import patch


_get_monitoring_list = [
    {
        "instance": "",
        "name": "com.vmware.applmgmt.mon.name.cpu.util",
        "description": "com.vmware.applmgmt.mon.descr.cpu.util",
        "id": "cpu.util",
        "units": "com.vmware.applmgmt.mon.unit.percent",
        "category": "com.vmware.applmgmt.mon.cat.cpu"
    },
    {
        "instance": "",
        "name": "com.vmware.applmgmt.mon.name.mem.util",
        "description": "com.vmware.applmgmt.mon.descr.mem.util",
        "id": "mem.util",
        "units": "com.vmware.applmgmt.mon.unit.kb",
        "category": "com.vmware.applmgmt.mon.cat.memory"
    }]


_get_cpu_util_data = {
    "start_time": "2021-05-06T22:13:05.651Z",
    "data": [
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "78",
        "120",
        "119",
        "120",
        "119",
        "120",
        "119",
        "120",
        "13"
    ],
    "function": "COUNT",
    "name": "cpu.util",
    "end_time": "2021-05-10T22:13:05.651Z",
    "interval": "HOURS2"
}


@patch.object(vmc_vcenter_request, 'call_api')
@patch.object(vmc_vcenter_request, 'get_headers')
def test_list_monitored_items_should_return_api_response(mock_get_headers, mock_call_api):
    mock_call_api.return_value = _get_monitoring_list
    mock_get_headers.return_value = {vmc_constants.VMWARE_API_SESSION_ID: "api-session-id"}
    assert vmc_vcenter_stats.list_monitored_items(hostname="hostname",
                                                  username="username",
                                                  password="password",
                                                  verify_ssl=False) == _get_monitoring_list


@patch.object(vmc_vcenter_request, 'call_api')
@patch.object(vmc_vcenter_request, 'get_headers')
def test_query_monitored_items_should_return_api_response(mock_get_headers, mock_call_api):
    mock_call_api.return_value = _get_cpu_util_data
    mock_get_headers.return_value = {vmc_constants.VMWARE_API_SESSION_ID: "api-session-id"}
    assert vmc_vcenter_stats.query_monitored_items(hostname="hostname",
                                                   username="username",
                                                   password="password",
                                                   start_time="start_time",
                                                   end_time="end_time",
                                                   interval="interval",
                                                   function="function",
                                                   monitored_items_ids="monitored_items_ids",
                                                   verify_ssl=False) == _get_cpu_util_data
