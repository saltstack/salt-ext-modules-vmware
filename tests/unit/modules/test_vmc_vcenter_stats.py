"""
    Unit tests for vmc_vcenter_stats execution module
"""
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_vcenter_stats as vmc_vcenter_stats


@pytest.fixture()
def monitoring_list_data(mock_vmc_vcenter_request_call_api):
    data = [
        {
            "instance": "",
            "name": "com.vmware.applmgmt.mon.name.cpu.util",
            "description": "com.vmware.applmgmt.mon.descr.cpu.util",
            "id": "cpu.util",
            "units": "com.vmware.applmgmt.mon.unit.percent",
            "category": "com.vmware.applmgmt.mon.cat.cpu",
        },
        {
            "instance": "",
            "name": "com.vmware.applmgmt.mon.name.mem.util",
            "description": "com.vmware.applmgmt.mon.descr.mem.util",
            "id": "mem.util",
            "units": "com.vmware.applmgmt.mon.unit.kb",
            "category": "com.vmware.applmgmt.mon.cat.memory",
        },
    ]
    mock_vmc_vcenter_request_call_api.return_value = data
    yield data


@pytest.fixture()
def cpu_util_data(mock_vmc_vcenter_request_call_api):
    data = {
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
            "13",
        ],
        "function": "COUNT",
        "name": "cpu.util",
        "end_time": "2021-05-10T22:13:05.651Z",
        "interval": "HOURS2",
    }
    mock_vmc_vcenter_request_call_api.return_value = data
    yield data


def test_list_monitored_items_should_return_api_response(
    mock_request_post_api, monitoring_list_data
):
    assert (
        vmc_vcenter_stats.list_monitored_items(
            hostname="hostname", username="username", password="password", verify_ssl=False
        )
        == monitoring_list_data
    )


def test_list_monitored_items_with_url(mock_request_post_api):
    expected_url = "https://hostname/api/appliance/monitoring"
    with patch("saltext.vmware.utils.vmc_vcenter_request.call_api", autospec=True) as vmc_call_api:
        vmc_vcenter_stats.list_monitored_items(
            hostname="hostname", username="username", password="password", verify_ssl=False
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url


def test_query_monitored_items_should_return_api_response(mock_request_post_api, cpu_util_data):
    assert (
        vmc_vcenter_stats.query_monitored_items(
            hostname="hostname",
            username="username",
            password="password",
            start_time="start_time",
            end_time="end_time",
            interval="interval",
            aggregate_function="aggregate_function",
            monitored_items="monitored_items",
            verify_ssl=False,
        )
        == cpu_util_data
    )


def test_query_monitored_items_with_url(mock_request_post_api):
    expected_url = "https://hostname/api/appliance/monitoring/query"
    with patch("saltext.vmware.utils.vmc_vcenter_request.call_api", autospec=True) as vmc_call_api:
        vmc_vcenter_stats.query_monitored_items(
            hostname="hostname",
            username="username",
            password="password",
            start_time="start_time",
            end_time="end_time",
            interval="interval",
            aggregate_function="aggregate_function",
            monitored_items="monitored_items",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
