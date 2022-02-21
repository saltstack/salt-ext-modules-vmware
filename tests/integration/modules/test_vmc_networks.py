"""
    Integration Tests for vmc_networks execution module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def subnets():
    return [{"gateway_address": "30.1.1.1/16"}]


@pytest.fixture
def request_headers(common_data):
    return vmc_request.get_headers(common_data["refresh_key"], common_data["authorization_host"])


@pytest.fixture
def network_url(common_data):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/tier-1s/cgw/segments/{network_id}"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
        network_id=common_data["network_id"],
    )
    return api_url


@pytest.fixture
def network_list_url(common_data):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/tier-1s/cgw/segments"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
    )
    return api_url


@pytest.fixture
def common_data(vmc_nsx_connect):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    data = {
        "hostname": hostname,
        "refresh_key": refresh_key,
        "authorization_host": authorization_host,
        "org_id": org_id,
        "sddc_id": sddc_id,
        "network_id": "web-tier",
        "verify_ssl": verify_ssl,
        "cert": cert,
    }
    yield data


@pytest.fixture
def get_networks(common_data, network_list_url, request_headers):
    session = requests.Session()
    response = session.get(
        url=network_list_url,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    response.raise_for_status()
    return response.json()


@pytest.fixture
def delete_network(get_networks, network_url, common_data, request_headers):
    """
    Sets up test requirements:
    Queries vmc api for networks
    Deletes network if exists
    """
    for result in get_networks.get("results", []):
        if result["id"] == common_data["network_id"]:
            session = requests.Session()
            response = session.delete(
                url=network_url,
                verify=common_data["cert"] if common_data["verify_ssl"] else False,
                headers=request_headers,
            )
            # raise error if any
            response.raise_for_status()


@pytest.fixture
def create_network(get_networks, network_url, common_data, request_headers, subnets):
    for result in get_networks.get("results", []):
        if result["id"] == common_data["network_id"]:
            return

    data = {"display_name": "web-tier", "subnets": subnets}
    session = requests.Session()
    response = session.patch(
        url=network_url,
        json=data,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    # raise error if any
    response.raise_for_status()


def test_create_network_smoke_test(salt_call_cli, delete_network, common_data, subnets):
    expected_network_id = common_data["network_id"]
    ret = salt_call_cli.run(
        "vmc_networks.create",
        subnets=subnets,
        **common_data,
    )
    result_as_json = ret.json
    assert result_as_json["id"] == result_as_json["display_name"] == expected_network_id


def test_get_networks_smoke_test(salt_call_cli, get_networks, common_data):
    # No network ID here
    del common_data["network_id"]
    ret = salt_call_cli.run("vmc_networks.get", **common_data)
    result_as_json = ret.json
    assert result_as_json == get_networks


def test_delete_network_smoke_test(salt_call_cli, create_network, common_data):
    ret = salt_call_cli.run("vmc_networks.delete", **common_data)
    result_as_json = ret.json
    assert result_as_json["result"] == "success"


def test_update_network_smoke_test(salt_call_cli, create_network, common_data):
    ret = salt_call_cli.run("vmc_networks.update", **common_data, display_name="network1")
    result = ret.json
    assert result["result"] == "success"
