"""
    Integration Tests for vmc_networks execution module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def network_id():
    return "sample-network"


@pytest.fixture
def subnets():
    return [{"gateway_address": "40.1.1.1/16"}]


@pytest.fixture
def request_headers(common_data):
    return vmc_request.get_headers(common_data["refresh_key"], common_data["authorization_host"])


@pytest.fixture
def network_url(common_data, network_id):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/tier-1s/cgw/segments/{network_id}"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
        network_id=network_id,
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
def common_data(vmc_config):
    return vmc_config["vmc_nsx_connect"]


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
def delete_network(get_networks, network_url, common_data, request_headers, network_id):
    """
    Sets up test requirements:
    Queries vmc api for networks
    Deletes network if exists
    """
    for result in get_networks.get("results", []):
        if result["id"] == network_id:
            session = requests.Session()
            response = session.delete(
                url=network_url,
                verify=common_data["cert"] if common_data["verify_ssl"] else False,
                headers=request_headers,
            )
            # raise error if any
            response.raise_for_status()


def test_vmc_networks_smoke_test(salt_call_cli, delete_network, subnets, common_data, network_id):
    # create network
    response = salt_call_cli.run(
        "vmc_networks.create", network_id=network_id, subnets=subnets, **common_data
    )
    response_as_json = response.json
    assert "error" not in response_as_json
    assert response_as_json["id"] == response_as_json["display_name"] == network_id

    # update network
    response = salt_call_cli.run(
        "vmc_networks.update", network_id=network_id, display_name="network1", **common_data
    )
    response_as_json = response.json
    assert "error" not in response_as_json
    assert response_as_json["result"] == "success"

    # delete network
    response = salt_call_cli.run("vmc_networks.delete", network_id=network_id, **common_data)
    response_as_json = response.json
    assert "error" not in response_as_json
    assert response_as_json["result"] == "success"

    # get networks
    response = salt_call_cli.run("vmc_networks.get", **common_data)
    response_as_json = response.json
    assert "error" not in response_as_json
