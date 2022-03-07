"""
    Integration Tests for vmc_dhcp_profiles state module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request


@pytest.fixture
def request_headers(common_data):
    return vmc_request.get_headers(common_data["refresh_key"], common_data["authorization_host"])


@pytest.fixture
def profile_type(common_data):
    return vmc_constants.DHCP_CONFIGS.format(common_data["type"])


@pytest.fixture
def profile_url(common_data, profile_type):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/{profile_type}/{profile_id}"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
        profile_type=profile_type,
        profile_id=common_data["dhcp_profile_id"],
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
def common_data(vmc_nsx_connect):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    data = {
        "hostname": hostname,
        "refresh_key": refresh_key,
        "authorization_host": authorization_host,
        "org_id": org_id,
        "sddc_id": sddc_id,
        "type": "server",
        "dhcp_profile_id": "dhcp-test",
        "verify_ssl": verify_ssl,
        "cert": cert,
    }
    yield data


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
def delete_dhcp_profile(get_dhcp_profiles, profile_url, request_headers, common_data):
    """
    Sets up test requirements:
    Queries vmc api for DHCP profiles
    Deletes DHCP profile if exists
    """

    for result in get_dhcp_profiles.get("results", []):
        if result["id"] == common_data["dhcp_profile_id"]:
            session = requests.Session()
            response = session.delete(
                url=profile_url,
                verify=common_data["cert"] if common_data["verify_ssl"] else False,
                headers=request_headers,
            )
            # raise error if any
            response.raise_for_status()


def test_vmc_dhcp_profiles_state_module(salt_call_cli, delete_dhcp_profile, common_data):

    # Invoke present state to create dhcp profile
    response = salt_call_cli.run(
        "state.single",
        "vmc_dhcp_profiles.present",
        name="present",
        server_addresses=["10.22.12.2/23"],
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"] is None
    assert changes["new"]["id"] == common_data["dhcp_profile_id"]
    assert result["comment"] == "Created DHCP Profile {}".format(common_data["dhcp_profile_id"])

    # Invoke present state to update with identical fields
    response = salt_call_cli.run(
        "state.single",
        "vmc_dhcp_profiles.present",
        name="present",
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}
    assert result["comment"] == "DHCP Profile exists already, no action to perform"

    # Invoke present state to update DHCP Profile with new display_name
    updated_display_name = "profile-1"
    response = salt_call_cli.run(
        "state.single",
        "vmc_dhcp_profiles.present",
        name="present",
        display_name=updated_display_name,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"]["display_name"] != changes["new"]["display_name"]
    assert changes["new"]["display_name"] == updated_display_name
    assert result["comment"] == "Updated DHCP Profile {}".format(common_data["dhcp_profile_id"])

    # Invoke present state to update DHCP profile with tags field
    updated_tags = [{"tag": "tag1", "scope": "scope1"}]
    response = salt_call_cli.run(
        "state.single",
        "vmc_dhcp_profiles.present",
        name="present",
        tags=updated_tags,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["new"]["tags"] == updated_tags
    assert result["comment"] == "Updated DHCP Profile {}".format(common_data["dhcp_profile_id"])

    # Invoke absent to delete the DHCP profile
    response = salt_call_cli.run(
        "state.single",
        "vmc_dhcp_profiles.absent",
        name="absent",
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["new"] is None
    assert changes["old"]["id"] == common_data["dhcp_profile_id"]
    assert result["comment"] == "Deleted DHCP Profile {}".format(common_data["dhcp_profile_id"])

    # Invoke absent when DHCP profile is not present
    response = salt_call_cli.run(
        "state.single",
        "vmc_dhcp_profiles.absent",
        name="absent",
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}

    assert result["comment"] == "No DHCP Profile found with Id {}".format(
        common_data["dhcp_profile_id"]
    )
