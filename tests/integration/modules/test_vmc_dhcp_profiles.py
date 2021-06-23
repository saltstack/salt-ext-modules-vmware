"""
    Integration Tests for vmc_dhcp_profiles execution module
"""
import pytest
import requests
from saltext.vmware.modules import vmc_dhcp_profiles
from saltext.vmware.utils import vmc_request


@pytest.fixture(scope="module")
def dhcp_test_data():
    dhcp_profile_type = "relay"
    dhcp_profile_id = "dhcp-test"
    return dhcp_profile_type, dhcp_profile_id


@pytest.fixture
def get_dhcp_profiles(vmc_nsx_connect, dhcp_test_data):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    dhcp_profile_type, dhcp_profile_id = dhcp_test_data

    profile_type = vmc_dhcp_profiles._get_profile_type(dhcp_profile_type)
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/{profile_type}"
    )

    api_url = url.format(
        hostname=hostname, org_id=org_id, sddc_id=sddc_id, profile_type=profile_type
    )
    session = requests.Session()
    response = session.get(
        url=api_url,
        verify=cert if verify_ssl else False,
        headers=vmc_request.get_headers(refresh_key, authorization_host),
    )
    response.raise_for_status()
    return response.json()


@pytest.fixture
def delete_dhcp_profile(get_dhcp_profiles, vmc_nsx_connect, dhcp_test_data):
    """
    Sets up test requirements:
    Queries vmc api for DHCP profiles
    Deletes DHCP profile if exists
    """
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    dhcp_profile_type, dhcp_profile_id = dhcp_test_data

    dhcp_profiles_dict = get_dhcp_profiles
    if dhcp_profiles_dict["result_count"] != 0:
        results = dhcp_profiles_dict["results"]
        for result in results:
            if result["id"] == dhcp_profile_id:
                url = (
                    "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
                    "policy/api/v1/infra/{profile_type}/{profile_id}"
                )
                profile_type = vmc_dhcp_profiles._get_profile_type(dhcp_profile_type)
                api_url = url.format(
                    hostname=hostname,
                    org_id=org_id,
                    sddc_id=sddc_id,
                    profile_type=profile_type,
                    profile_id=dhcp_profile_id,
                )
                session = requests.Session()
                response = session.delete(
                    url=api_url,
                    verify=cert if verify_ssl else False,
                    headers=vmc_request.get_headers(refresh_key, authorization_host),
                )
                # raise error if any
                response.raise_for_status()


@pytest.fixture
def create_dhcp_profile(get_dhcp_profiles, vmc_nsx_connect, dhcp_test_data):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    dhcp_profile_type, dhcp_profile_id = dhcp_test_data

    dhcp_profiles_dict = get_dhcp_profiles
    if dhcp_profiles_dict["result_count"] != 0:
        results = dhcp_profiles_dict["results"]
        for result in results:
            if result["id"] == dhcp_profile_id:
                return

    profile_type = vmc_dhcp_profiles._get_profile_type(dhcp_profile_type)
    url = "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/policy/api/v1/infra/{profile_type}/{profile_id}"

    api_url = url.format(
        hostname=hostname,
        org_id=org_id,
        sddc_id=sddc_id,
        profile_type=profile_type,
        profile_id=dhcp_profile_id,
    )
    data = {"display_name": "dhcp-test", "server_addresses": ["10.1.1.1"]}
    session = requests.Session()
    response = session.patch(
        url=api_url,
        json=data,
        verify=cert if verify_ssl else False,
        headers=vmc_request.get_headers(refresh_key, authorization_host),
    )
    # raise error if any
    response.raise_for_status()


def test_create_dhcp_profile(salt_call_cli, delete_dhcp_profile, vmc_nsx_connect, dhcp_test_data):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    dhcp_profile_type, dhcp_profile_id = dhcp_test_data

    ret = salt_call_cli.run(
        "vmc_dhcp_profiles.create",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        dhcp_profile_type=dhcp_profile_type,
        dhcp_profile_id=dhcp_profile_id,
        verify_ssl=verify_ssl,
        cert=cert,
        server_addresses=["10.1.1.1"],
    )
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json["id"] == result_as_json["display_name"] == dhcp_profile_id


def test_get_dhcp_profiles(salt_call_cli, get_dhcp_profiles, vmc_nsx_connect, dhcp_test_data):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    dhcp_profile_type, dhcp_profile_id = dhcp_test_data

    ret = salt_call_cli.run(
        "vmc_dhcp_profiles.get",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        dhcp_profile_type=dhcp_profile_type,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json == get_dhcp_profiles


def test_delete_dhcp_profile(salt_call_cli, create_dhcp_profile, vmc_nsx_connect, dhcp_test_data):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    dhcp_profile_type, dhcp_profile_id = dhcp_test_data

    ret = salt_call_cli.run(
        "vmc_dhcp_profiles.delete",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        dhcp_profile_type=dhcp_profile_type,
        dhcp_profile_id=dhcp_profile_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json["result"] == "success"


def test_update_dhcp_profile(salt_call_cli, create_dhcp_profile, vmc_nsx_connect, dhcp_test_data):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    dhcp_profile_type, dhcp_profile_id = dhcp_test_data

    ret = salt_call_cli.run(
        "vmc_dhcp_profiles.update",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        dhcp_profile_type=dhcp_profile_type,
        dhcp_profile_id=dhcp_profile_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json["result"] == "success"
