"""
    Integration Tests for vmc_sddc_host execution module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def request_headers(common_data):
    return vmc_request.get_headers(common_data["refresh_key"], common_data["authorization_host"])


@pytest.fixture
def common_data(vmc_connect):
    (
        hostname,
        refresh_key,
        authorization_host,
        org_id,
        sddc_id,
        verify_ssl,
        cert,
        vcenter_hostname,
    ) = vmc_connect
    data = {
        "hostname": hostname,
        "refresh_key": refresh_key,
        "authorization_host": authorization_host,
        "org_id": org_id,
        "sddc_id": sddc_id,
        "verify_ssl": verify_ssl,
        "cert": cert,
    }
    yield data


@pytest.fixture
def sddc_host_list_url(common_data):
    url = "https://{hostname}/vmc/api/orgs/{org_id}/sddcs/{sddc_id}"
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
    )
    return api_url


@pytest.fixture
def get_sddc_hosts(common_data, sddc_host_list_url, request_headers):
    session = requests.Session()
    response = session.get(
        url=sddc_host_list_url,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    response.raise_for_status()
    return response.json()


def test_get_sddc_hosts_smoke_test(salt_call_cli, get_sddc_hosts, common_data):
    # No nat rule here
    del common_data["nat_rule"]
    ret = salt_call_cli.run("vmc_sddc_host.get", **common_data)
    result_as_json = ret.json
    assert result_as_json == get_sddc_hosts
