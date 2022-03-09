"""
    Integration Tests for vmc_dhcp_profiles execution module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request


@pytest.fixture
def profile_id():
    return "sample-dhcp"


@pytest.fixture
def server_addresses():
    return ["10.1.1.1"]


@pytest.fixture
def request_headers(common_data):
    return vmc_request.get_headers(common_data["refresh_key"], common_data["authorization_host"])


@pytest.fixture
def profile_type(common_data):
    return vmc_constants.DHCP_CONFIGS.format(common_data["type"])


@pytest.fixture
def profile_url(common_data, profile_type, profile_id):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/{profile_type}/{profile_id}"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
        profile_type=profile_type,
        profile_id=profile_id,
    )
    return api_url


@pytest.fixture
def profile_list_url(common_data, profile_type):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/{profile_type}"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
        profile_type=profile_type,
    )
    return api_url


@pytest.fixture
def common_data(vmc_config):
    common_data = vmc_config["vmc_nsx_connect"]
    common_data["type"] = "relay"
    return common_data


@pytest.fixture
def get_dhcp_profiles(common_data, profile_list_url, request_headers):
    session = requests.Session()
    response = session.get(
        url=profile_list_url,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    response.raise_for_status()
    return response.json()


@pytest.fixture
def delete_dhcp_profile(get_dhcp_profiles, profile_url, request_headers, common_data, profile_id):
    """
    Sets up test requirements:
    Queries vmc api for DHCP profiles
    Deletes DHCP profile if exists
    """

    for result in get_dhcp_profiles.get("results", []):
        if result["id"] == profile_id:
            session = requests.Session()
            response = session.delete(
                url=profile_url,
                verify=common_data["cert"] if common_data["verify_ssl"] else False,
                headers=request_headers,
            )
            # raise error if any
            response.raise_for_status()


def test_vmc_dhcp_profile_execution_module(
    salt_call_cli, delete_dhcp_profile, server_addresses, common_data, profile_id
):
    # create dhcp profile
    response = salt_call_cli.run(
        "vmc_dhcp_profiles.create",
        dhcp_profile_id=profile_id,
        server_addresses=server_addresses,
        **common_data,
    )
    response_as_json = response.json
    assert "error" not in response_as_json
    assert response_as_json["id"] == response_as_json["display_name"] == profile_id

    # update dhcp profile
    response = salt_call_cli.run(
        "vmc_dhcp_profiles.update",
        dhcp_profile_id=profile_id,
        display_name="profile1",
        **common_data,
    )
    response_as_json = response.json
    assert "error" not in response_as_json
    assert response_as_json["result"] == "success"

    # delete dhcp profile
    response = salt_call_cli.run(
        "vmc_dhcp_profiles.delete", dhcp_profile_id=profile_id, **common_data
    )
    response_as_json = response.json
    assert "error" not in response_as_json
    assert response_as_json["result"] == "success"

    # get dhcp profiles
    response = salt_call_cli.run("vmc_dhcp_profiles.get", **common_data)
    response_as_json = response.json
    assert "error" not in response_as_json
