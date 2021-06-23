"""
    Integration Tests for vmc_dhcp_profiles state module
"""
import pytest
import requests
from saltext.vmware.modules import vmc_dhcp_profiles
from saltext.vmware.utils import vmc_request


@pytest.fixture()
def dhcp_test_data():
    dhcp_profile_type = "server"
    dhcp_profile_id = "dhcp-test"
    updated_display_name = "profile-1"
    updated_tags = [{"tag": "tag1", "scope": "scope1"}]

    return dhcp_profile_type, dhcp_profile_id, updated_display_name, updated_tags


@pytest.fixture
def delete_dhcp_profile(vmc_nsx_connect, dhcp_test_data):
    """
    Sets up test requirements:
    Queries vmc api for DHCP profiles
    Deletes DHCP profile if exists
    """
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    dhcp_profile_type, dhcp_profile_id, updated_display_name, updated_tags = dhcp_test_data

    profile_type = vmc_dhcp_profiles._get_profile_type(dhcp_profile_type)
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/{profile_type}"
    )

    api_url = url.format(
        hostname=hostname, org_id=org_id, sddc_id=sddc_id, profile_type=profile_type
    )

    session = requests.Session()
    headers = vmc_request.get_headers(refresh_key, authorization_host)

    response = session.get(url=api_url, verify=cert if verify_ssl else False, headers=headers)
    response.raise_for_status()
    dhcp_profiles_dict = response.json()
    if dhcp_profiles_dict["result_count"] != 0:
        results = dhcp_profiles_dict["results"]
        for result in results:
            if result["id"] == dhcp_profile_id:
                url = (
                    "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
                    "policy/api/v1/infra/{profile_type}/{profile_id}"
                )

                api_url = url.format(
                    hostname=hostname,
                    org_id=org_id,
                    sddc_id=sddc_id,
                    profile_type=profile_type,
                    profile_id=dhcp_profile_id,
                )

                response = session.delete(
                    url=api_url, verify=cert if verify_ssl else False, headers=headers
                )
                # raise error if any
                response.raise_for_status()


def test_vmc_dhcp_profiles_state_module(
    salt_call_cli, delete_dhcp_profile, vmc_nsx_connect, dhcp_test_data
):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    dhcp_profile_type, dhcp_profile_id, updated_display_name, updated_tags = dhcp_test_data

    # Invoke present state to create dhcp profile
    response = salt_call_cli.run(
        "state.single",
        "vmc_dhcp_profiles.present",
        name="present",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        dhcp_profile_type=dhcp_profile_type,
        dhcp_profile_id=dhcp_profile_id,
        verify_ssl=verify_ssl,
        cert=cert,
        server_addresses=["10.22.12.2/23"],
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"] is None
    assert changes["new"]["id"] == dhcp_profile_id
    assert result["comment"] == "Created DHCP Profile {}".format(dhcp_profile_id)

    # Invoke present state to update with identical fields
    response = salt_call_cli.run(
        "state.single",
        "vmc_dhcp_profiles.present",
        name="present",
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
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}
    assert result["comment"] == "DHCP Profile exists already, no action to perform"

    # Invoke present state to update DHCP Profile with new display_name
    response = salt_call_cli.run(
        "state.single",
        "vmc_dhcp_profiles.present",
        name="present",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        dhcp_profile_type=dhcp_profile_type,
        dhcp_profile_id=dhcp_profile_id,
        verify_ssl=verify_ssl,
        cert=cert,
        display_name=updated_display_name,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"]["display_name"] != changes["new"]["display_name"]
    assert changes["new"]["display_name"] == updated_display_name
    assert result["comment"] == "Updated DHCP Profile {}".format(dhcp_profile_id)

    # Invoke present state to update DHCP profile with tags field
    response = salt_call_cli.run(
        "state.single",
        "vmc_dhcp_profiles.present",
        name="present",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        dhcp_profile_type=dhcp_profile_type,
        dhcp_profile_id=dhcp_profile_id,
        verify_ssl=verify_ssl,
        cert=cert,
        tags=updated_tags,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["new"]["tags"] == updated_tags
    assert result["comment"] == "Updated DHCP Profile {}".format(dhcp_profile_id)

    # Invoke absent to delete the DHCP profile
    response = salt_call_cli.run(
        "state.single",
        "vmc_dhcp_profiles.absent",
        name="absent",
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
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["new"] is None
    assert changes["old"]["id"] == dhcp_profile_id
    assert result["comment"] == "Deleted DHCP Profile {}".format(dhcp_profile_id)

    # Invoke absent when DHCP profile is not present
    response = salt_call_cli.run(
        "state.single",
        "vmc_dhcp_profiles.absent",
        name="absent",
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
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}

    assert result["comment"] == "No DHCP Profile found with Id {}".format(dhcp_profile_id)
