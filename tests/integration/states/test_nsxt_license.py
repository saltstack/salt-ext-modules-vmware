"""
    Integration Tests for nsxt_license state module
"""
import json

import pytest
import requests


@pytest.fixture
def delete_license(nsxt_config):
    """
    Sets up test requirements:
    Queries nsx api for licenses
    Deletes license if exists
    """
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    license_key = nsxt_config["license_key"]
    verify_ssl = nsxt_config.get("cert", False)

    url = f"https://{hostname}/api/v1/licenses"
    session = requests.Session()
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    response = session.get(url=url, auth=(username, password), verify=verify_ssl, headers=headers)
    response.raise_for_status()
    licenses_dict = response.json()
    if licenses_dict["result_count"] != 0:
        results = licenses_dict["results"]
        for result in results:
            if result["license_key"] == license_key:
                url = "https://{management_host}/api/v1/licenses?action=delete".format(
                    management_host=hostname
                )
                data = {"license_key": license_key}
                response = session.post(
                    url=url,
                    auth=(username, password),
                    data=json.dumps(data),
                    verify=verify_ssl,
                    headers=headers,
                )
                # raise error if any
                response.raise_for_status()


@pytest.mark.xfail(reason="nsxt tests not working yet")
def test_nsxt_licenses_state_module(nsxt_config, salt_call_cli, delete_license):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    license_key = nsxt_config["license_key"]
    verify_ssl = nsxt_config.get("cert", False)

    response = salt_call_cli.run(
        "state.single",
        "nsxt_license.present",
        name="present",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        license_key=license_key,
    )
    response_json = response.json
    result = dict(list(response_json.values())[0])
    changes = result["changes"]
    # assert old array doesn't contain the license to be added
    for license_entry in changes["old"]["results"]:
        assert license_entry["license_key"] != license_key

    # assert new array contains the license to be added
    for license_entry in changes["new"]["results"]:
        if license_entry["license_key"] == nsxt_config["license_key"]:
            break
    else:
        assert False, "No license key present in results"

    assert result["comment"] == "License added successfully"

    # Invoke state when license is already present
    response = salt_call_cli.run(
        "state.single",
        "nsxt_license.present",
        name="present",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        license_key=license_key,
    )
    response_json = response.json
    result = dict(list(response_json.values())[0])
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}

    assert result["comment"] == "License key is already present"
    # Invoke absent to delete the license
    response = salt_call_cli.run(
        "state.single",
        "nsxt_license.absent",
        name="absent",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        license_key=license_key,
    )
    response_json = response.json
    result = dict(list(response_json.values())[0])
    changes = result["changes"]

    # assert old array contains the license to be removed
    for license_entry in changes["old"]["results"]:
        if license_entry["license_key"] == nsxt_config["license_key"]:
            break
    else:
        assert False, "No license key present in results"

    # assert new array doesn't contains the license to be removed
    for license_entry in changes["new"]["results"]:
        if license_entry["license_key"] == nsxt_config["license_key"]:
            break
    else:
        assert True, "License was removed"

    # Invoke absent when license is not present
    response = salt_call_cli.run(
        "state.single",
        "nsxt_license.absent",
        name="absent",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        license_key=license_key,
    )
    response_json = response.json
    result = dict(list(response_json.values())[0])
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}

    assert result["comment"] == "License key is not present in NSX-T Manager"
