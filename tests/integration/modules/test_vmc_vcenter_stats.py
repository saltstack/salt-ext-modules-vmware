"""
    Integration Tests for vmc_vcenter_stats execution module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_vcenter_request


@pytest.fixture
def common_data(vmc_vcenter_admin_connect):
    hostname, username, password, verify_ssl, cert = vmc_vcenter_admin_connect
    data = {
        "hostname": hostname,
        "username": username,
        "password": password,
        "verify_ssl": verify_ssl,
        "cert": cert,
    }
    yield data


@pytest.fixture
def request_headers(common_data):
    return vmc_vcenter_request.get_headers(
        common_data["hostname"], common_data["username"], common_data["password"]
    )


@pytest.fixture
def vmc_vcenter_monitoring_spec():
    monitoring_spec = {
        "start_time": "2022-02-20T22:13:05.651Z",
        "end_time": "2022-02-21T22:13:05.651Z",
        "interval": "HOURS2",
        "function": "COUNT",
        "monitored_items_ids": "cpu.util,mem.util".split(","),
    }
    return monitoring_spec


@pytest.fixture
def query_params(vmc_vcenter_monitoring_spec):
    query_params = {
        "start_time": vmc_vcenter_monitoring_spec["start_time"],
        "end_time": vmc_vcenter_monitoring_spec["end_time"],
        "function": vmc_vcenter_monitoring_spec["function"],
        "interval": vmc_vcenter_monitoring_spec["interval"],
        "names": vmc_vcenter_monitoring_spec["monitored_items_ids"],
    }
    yield query_params


@pytest.fixture
def query_monitoring_params(common_data, vmc_vcenter_monitoring_spec):
    query_monitoring_params = common_data.copy()
    query_monitoring_params.update(vmc_vcenter_monitoring_spec)
    yield query_monitoring_params


@pytest.fixture
def list_monitoring(common_data, request_headers):
    url = "https://{hostname}/api/appliance/monitoring"
    api_url = url.format(hostname=common_data["hostname"])
    session = requests.Session()
    response = session.get(
        url=api_url,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    response.raise_for_status()
    return response.json()


@pytest.fixture
def query_monitoring(common_data, query_params, request_headers):
    url = "https://{hostname}/api/appliance/monitoring/query"
    api_url = url.format(hostname=common_data["hostname"])
    session = requests.Session()
    response = session.get(
        url=api_url,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
        params=query_params,
    )
    response.raise_for_status()
    return response.json()


def test_list_monitored_items_smoke_test(salt_call_cli, list_monitoring, common_data):
    ret = salt_call_cli.run("vmc_vcenter_stats.list_monitored_items", **common_data)
    result = ret.json
    assert result == list_monitoring


def test_query_monitored_items_smoke_test(salt_call_cli, query_monitoring, query_monitoring_params):
    ret = salt_call_cli.run("vmc_vcenter_stats.query_monitored_items", **query_monitoring_params)
    result_as_json = ret.json
    assert result_as_json == query_monitoring
