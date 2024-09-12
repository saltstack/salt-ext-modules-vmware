"""
    Integration Tests for vmc_sddc state module
"""

from datetime import datetime

import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def vmc_common_data(vmc_connect):
    data = vmc_connect.copy()
    data.pop("vcenter_hostname")
    data.pop("sddc_id")
    return data


@pytest.fixture
def request_headers(vmc_common_data):
    return vmc_request.get_headers(
        vmc_common_data["refresh_key"], vmc_common_data["authorization_host"]
    )


@pytest.fixture
def sddc_name():
    # now = datetime.now()
    # return "sddc_test-" + str(now)
    return "123-salt-sddc-it-test-2022"


@pytest.fixture
def sddc_list_url(vmc_common_data):
    url = "https://{hostname}/vmc/api/orgs/{org_id}/sddcs/"
    api_url = url.format(
        hostname=vmc_common_data["hostname"],
        org_id=vmc_common_data["org_id"],
    )
    return api_url


@pytest.fixture
def get_sddc_list(vmc_common_data, request_headers, sddc_list_url):
    session = requests.Session()
    response = session.get(
        url=sddc_list_url,
        verify=vmc_common_data["cert"] if vmc_common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    response.raise_for_status()
    return response.json()


@pytest.fixture
def delete_sddc(
    get_sddc_list,
    sddc_list_url,
    request_headers,
    vmc_common_data,
    sddc_name,
):
    """
    Sets up test requirements:
    Queries vmc api for SDDC list
    Deletes SDDCs if exists with the same sddc_name
    """

    for result in get_sddc_list:
        if result["name"] == sddc_name:
            session = requests.Session()
            response = session.delete(
                url=sddc_list_url + result["id"],
                verify=vmc_common_data["cert"] if vmc_common_data["verify_ssl"] else False,
                headers=request_headers,
            )
            # raise error if any
            response.raise_for_status()


def test_vmc_sddc_state_module(salt_call_cli, vmc_common_data, delete_sddc, sddc_name):
    # Invoke present state to create sddc
    response = salt_call_cli.run(
        "state.single",
        "vmc_sddc.present",
        name=sddc_name,
        num_hosts=1,
        provider="ZEROCLOUD",
        region="us-west-2",
        **vmc_common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    if result["result"]:
        result = list(response_json.values())[0]
        changes = result["changes"]
        assert changes["old"] is None
        assert changes["new"]["params"]["sddcConfig"]["name"] == sddc_name
        assert result["comment"] == f"Created SDDC {sddc_name}"

        # get the sddc_id of newly created SDDC
        sddc_id = result["changes"]["new"]["resource_id"]

        # Invoke present state where sddc already exist
        response = salt_call_cli.run(
            "state.single",
            "vmc_sddc.present",
            name=sddc_name,
            num_hosts=1,
            provider="ZEROCLOUD",
            region="us-west-2",
            **vmc_common_data,
        )
        response_json = response.json
        result = list(response_json.values())[0]
        changes = result["changes"]

        # assert no changes are done
        assert changes == {}
        assert result["comment"] == "SDDC is already present"

        # Get the SDDC data
        ret = salt_call_cli.run("vmc_sddc.get_by_id", sddc_id=sddc_id, **vmc_common_data)
        result_as_json = ret.json
        assert "error" not in result_as_json
        sddc = result_as_json

        # Invoke absent to delete the sddc
        response = salt_call_cli.run(
            "state.single", "vmc_sddc.absent", name=sddc_id, **vmc_common_data
        )
        response_json = response.json
        result = list(response_json.values())[0]
        changes = result["changes"]

        if sddc.get("sddc_state") in ("DEPLOYING", "DELETED", "DELETION_IN_PROGRESS"):
            assert changes == {}
            assert result[
                "comment"
            ] == "No SDDC found with ID {} or deletion is already in progress or SDDC is still deploying".format(
                sddc_id
            )
        else:
            assert changes["new"] is None
            assert changes["old"]["id"] == sddc_id
            assert result["comment"] == f"Deleted SDDC {sddc_id}"
    else:
        assert "Failed to add SDDC" in result["comment"]
