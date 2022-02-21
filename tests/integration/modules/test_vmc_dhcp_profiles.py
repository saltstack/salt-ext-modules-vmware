"""
    Integration Tests for vmc_dhcp_profiles execution module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request


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
        "type": "relay",
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


@pytest.fixture
def create_dhcp_profile(
    get_dhcp_profiles, profile_url, server_addresses, request_headers, common_data
):
    for result in get_dhcp_profiles.get("results", []):
        if result["id"] == common_data["dhcp_profile_id"]:
            return

    data = {"display_name": "dhcp-test", "server_addresses": server_addresses}
    session = requests.Session()
    response = session.patch(
        url=profile_url,
        json=data,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    # raise error if any
    response.raise_for_status()


def test_create_dhcp_profile_smoke_test(
    salt_call_cli, delete_dhcp_profile, common_data, server_addresses
):
    expected_profile_id = common_data["dhcp_profile_id"]
    ret = salt_call_cli.run(
        "vmc_dhcp_profiles.create",
        server_addresses=server_addresses,
        **common_data,
    )
    result_as_json = ret.json
    assert result_as_json["id"] == result_as_json["display_name"] == expected_profile_id


def test_get_dhcp_profiles_smoke_test(salt_call_cli, get_dhcp_profiles, common_data):
    # No profile ID here
    del common_data["dhcp_profile_id"]
    ret = salt_call_cli.run("vmc_dhcp_profiles.get", **common_data)
    result_as_json = ret.json
    assert result_as_json == get_dhcp_profiles


def test_update_dhcp_profile_smoke_test(salt_call_cli, common_data, create_dhcp_profile):
    ret = salt_call_cli.run("vmc_dhcp_profiles.update", **common_data, display_name="fnord")
    result = ret.json
    assert result["result"] == "success"


def test_delete_dhcp_profile_smoke_test(salt_call_cli, create_dhcp_profile, common_data):
    ret = salt_call_cli.run("vmc_dhcp_profiles.delete", **common_data)
    result_as_json = ret.json
    assert result_as_json["result"] == "success"
