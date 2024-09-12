"""
    Integration Tests for vmc_networks state module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def network_id():
    return "web-tier"


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


def test_vmc_networks_state_module(salt_call_cli, delete_network, common_data, network_id):
    # Invoke present state to create Network
    response = salt_call_cli.run(
        "state.single",
        "vmc_networks.present",
        name=network_id,
        subnets=[{"gateway_address": "30.1.1.1/16"}],
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"] is None
    assert changes["new"]["id"] == network_id
    assert result["comment"] == f"Created network {network_id}"

    # Test present to update with identical fields
    # Invoke state when network is already present
    response = salt_call_cli.run(
        "state.single",
        "vmc_networks.present",
        name=network_id,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}
    assert result["comment"] == "Network exists already, no action to perform"

    # Invoke present state to update Network with new display_name
    updated_display_name = "network-1"
    response = salt_call_cli.run(
        "state.single",
        "vmc_networks.present",
        name=network_id,
        display_name=updated_display_name,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"]["display_name"] != changes["new"]["display_name"]
    assert changes["new"]["display_name"] == updated_display_name
    assert result["comment"] == f"Updated network {network_id}"

    # Invoke present state to update Network with tags field
    updated_tags = [{"tag": "tag1", "scope": "scope1"}]
    response = salt_call_cli.run(
        "state.single",
        "vmc_networks.present",
        name=network_id,
        tags=updated_tags,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["new"]["tags"] == updated_tags
    assert result["comment"] == f"Updated network {network_id}"

    # Invoke absent to delete the network
    response = salt_call_cli.run(
        "state.single",
        "vmc_networks.absent",
        name=network_id,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["new"] is None
    assert changes["old"]["id"] == network_id
    assert result["comment"] == f"Deleted network {network_id}"

    # Invoke absent when network is not present
    response = salt_call_cli.run(
        "state.single",
        "vmc_networks.absent",
        name=network_id,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}

    assert result["comment"] == f"No network found with ID {network_id}"
