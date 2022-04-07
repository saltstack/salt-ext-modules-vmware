"""
    Integration Tests for vmc_public_ip state module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def common_data(vmc_config):
    data = vmc_config["vmc_nsx_connect"].copy()
    data["public_ip_id"] = "TEST_INTEGRATION_PUBLIC_IP"
    return data


@pytest.fixture
def request_headers(common_data):
    return vmc_request.get_headers(common_data["refresh_key"], common_data["authorization_host"])


@pytest.fixture
def public_ip_url(common_data):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "cloud-service/api/v1/infra/public-ips/{public_ip_id}"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
        public_ip_id=common_data["public_ip_id"],
    )
    return api_url


@pytest.fixture
def public_ips_list_url(common_data):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "cloud-service/api/v1/infra/public-ips"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
    )
    return api_url


@pytest.fixture
def get_public_ips(common_data, public_ips_list_url, request_headers):
    session = requests.Session()
    response = session.get(
        url=public_ips_list_url,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    response.raise_for_status()
    return response.json()


@pytest.fixture
def delete_public_ip(get_public_ips, public_ip_url, request_headers, common_data):
    for result in get_public_ips.get("results", []):
        if result["id"] == common_data["public_ip_id"]:
            session = requests.Session()
            response = session.delete(
                url=public_ip_url,
                verify=common_data["cert"] if common_data["verify_ssl"] else False,
                headers=request_headers,
            )
            # raise error if any
            response.raise_for_status()


def test_vmc_public_ip_state_module(salt_call_cli, delete_public_ip, common_data):
    public_ip_id = common_data.pop("public_ip_id")

    # Invoke present state to create public IP
    response = salt_call_cli.run(
        "state.single",
        "vmc_public_ip.present",
        name=public_ip_id,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"] is None
    assert changes["new"]["id"] == public_ip_id
    assert result["comment"] == "Created public IP {}".format(public_ip_id)

    # Test present to update public IP with identical fields
    response = salt_call_cli.run(
        "state.single",
        "vmc_public_ip.present",
        name=public_ip_id,
        display_name=public_ip_id,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}
    assert result["comment"] == "Public IP exists already, no action to perform"

    updated_display_name = "updated_public_ip"

    # Invoke present state to update public IP with new display_name
    response = salt_call_cli.run(
        "state.single",
        "vmc_public_ip.present",
        display_name=updated_display_name,
        name=public_ip_id,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"]["display_name"] != changes["new"]["display_name"]
    assert changes["new"]["display_name"] == updated_display_name
    assert result["comment"] == "Updated public IP {}".format(public_ip_id)

    # Invoke absent to delete the public IP
    response = salt_call_cli.run(
        "state.single",
        "vmc_public_ip.absent",
        name=public_ip_id,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["new"] is None
    assert changes["old"]["id"] == public_ip_id
    assert result["comment"] == "Deleted public IP {}".format(public_ip_id)

    # Invoke absent when public IP is not present
    response = salt_call_cli.run(
        "state.single",
        "vmc_public_ip.absent",
        name=public_ip_id,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}
    assert result["comment"] == "No public IP found with ID {}".format(public_ip_id)
