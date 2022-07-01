"""
    Integration Tests for vmc_sddc state module
"""
import json
import os
import time

import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def vmc_common_data(vmc_connect):
    data = vmc_connect.copy()
    data.pop("vcenter_hostname")
    return data


@pytest.fixture
def request_headers(common_data):
    return vmc_request.get_headers(common_data["refresh_key"], common_data["authorization_host"])


@pytest.fixture
def sddc_name():
    return "sddc_test-1"


@pytest.fixture
def sddc_url(vmc_common_data):
    url = "https://{hostname}/vmc/api/orgs/{org_id}/sddcs/{sddc_id}"
    api_url = url.format(
        hostname=vmc_common_data["hostname"],
        org_id=vmc_common_data["org_id"],
        sddc_id=vmc_common_data["sddc_id"],
    )
    return api_url


@pytest.fixture
def get_sddc(vmc_common_data, request_headers, sddc_url):
    session = requests.Session()
    response = session.get(
        url=sddc_url,
        verify=vmc_common_data["cert"] if vmc_common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    response.raise_for_status()
    return response.json()


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
    Deletes SDDC if exists
    """

    for result in get_sddc_list.get("results", []):
        if result["name"] == sddc_name:
            session = requests.Session()
            response = session.delete(
                url=sddc_list_url + result["id"],
                verify=vmc_common_data["cert"] if vmc_common_data["verify_ssl"] else False,
                headers=request_headers,
            )
            # raise error if any
            response.raise_for_status()


def test_vmc_sddc_state_module(salt_call_cli, vmc_common_data, delete_sddc, get_sddc, sddc_name):
    # Invoke present state to create sddc
    response = salt_call_cli.run(
        "state.single",
        "vmc_sddc.present",
        name=sddc_name,
        **vmc_common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"] is None
    assert changes["new"]["id"] == sddc_name
    assert result["comment"] == "Created SDDC {}".format(sddc_name)

    # Invoke present state where sddc already exist
    response = salt_call_cli.run(
        "state.single",
        "vmc_sddc.present",
        name=sddc_name,
        **vmc_common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"] is None
    assert changes["new"] is None
    assert result["comment"] == "SDDC is already present"

    # Invoke absent to delete the sddc
    response = salt_call_cli.run(
        "state.single", "vmc_sddc.absent", name=vmc_common_data["sddc_id"], **vmc_common_data
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    if created_sddc.get("sddc_state") in ("DEPLOYING", "DELETED", "DELETION_IN_PROGRESS"):
        assert changes == {}
        assert result[
            "comment"
        ] == "No SDDC found with ID {} or deletion is already in progress or SDDC is still deploying".format(
            sddc_id
        )
    else:
        assert changes["new"] is None
        assert changes["old"]["id"] == vmc_common_data["sddc_id"]
        assert result["comment"] == "Deleted SDDC {}".format(vmc_common_data["sddc_id"])

    # # Invoke absent when sddc is not present or deletion is already in progress
    # response = salt_call_cli.run(
    #     "state.single",
    #     "vmc_sddc.absent",
    #     name=vmc_common_data["sddc_id"],
    #     **vmc_common_data,
    # )
    # response_json = response.json
    # result = list(response_json.values())[0]
    # changes = result["changes"]
    # # assert no changes are done
    # assert changes == {}
    # assert result["comment"] == "No SDDC found with ID %s or deletion is already in progress.".format(vmc_common_data["sddc_id"])


# @pytest.fixture
# def get_sddc_list():
#     url = 'https://{hostname}/vmc/api/orgs/{org_id}/sddcs'
#
#     api_url = url.format(hostname=_hostname, org_id=_org_id)
#     auth_token = get_auth_token(_authorization_host, _refresh_key)
#     session = requests.Session()
#     headers = dict({'Accept': 'application/json', 'Content-Type': 'application/json', 'csp-auth-token': auth_token})
#     response = session.get(
#         url=api_url,
#         verify=_cert if _verify_ssl else False,
#         headers=headers
#     )
#     response.raise_for_status()
#     return response.json()
#
#
# @pytest.fixture
# def create_sddc(get_sddc_list):
#
#     for sddc in get_sddc_list:
#         if sddc['id'] == _sddc_id:
#             return _sddc_id
#     url = 'https://{hostname}/api/inventory/{org_Id}/vmc-aws/operations'
#     api_url = url.format(hostname=_hostname, org_Id=_org_id)
#     auth_token = get_auth_token(_authorization_host, _refresh_key)
#     session = requests.Session()
#     headers = dict({'Accept': 'application/json', 'Content-Type': 'application/json', 'csp-auth-token': auth_token})
#     response = session.post(
#         url=api_url,
#         data=json.dumps(_data),
#         verify=_cert if _verify_ssl else False,
#         headers=headers
#     )
#     # raise error if any
#     time.sleep(50)
#     response.raise_for_status()
#     json_response = response.json()
#     sddc_id = json_response['resource_id'] if "resource_id" in json_response.keys() else json_response['id']
#     return sddc_id
#
#
# @pytest.fixture
# def delete_sddc(get_sddc_list):
#     """
#         Sets up test requirements:
#         Queries vmc api for SDDCs list
#         Deletes SDDC if already exists
#     """
#     for sddc in get_sddc_list:
#         if sddc['id'] == _sddc_id:
#             url = 'https://{hostname}/vmc/api/orgs/{org_id}/sddcs/{sddc_id}'
#             api_url = url.format(hostname=_hostname, org_id=_org_id, sddc_id=_sddc_id)
#             auth_token = get_auth_token(_authorization_host, _refresh_key)
#             session = requests.Session()
#             headers = dict(
#                 {'Accept': 'application/json', 'Content-Type': 'application/json', 'csp-auth-token': auth_token})
#
#             response = session.delete(
#                 url=api_url,
#                 verify=_cert if _verify_ssl else False,
#                 headers=headers
#             )
#             # raise error if any
#             response.raise_for_status()

# @pytest.fixture
# def get_sddc_by_id(salt_call_cli, vmc_common_data):
#     ret = salt_call_cli.run("vmc_sddc.get_by_id", **vmc_common_data)
#     result_as_json = ret.json
#     assert "error" not in result_as_json
#     assert result_as_json["id"] == vmc_common_data["sddc_id"]


# def get_auth_token(authorization_host, refresh_key):
#     url = "https://{hostname}/csp/gateway/am/api/auth/api-tokens/authorize".format(hostname=authorization_host)
#     params = {'refresh_token': refresh_key}
#     headers = {'Content-Type': 'application/json'}
#     response = requests.post(url, params=params, headers=headers)
#     json_response = response.json()
#     access_token = json_response['access_token']
#     return access_token
#
#
# def get_sddc_name():
#     script_dir_path = os.path.dirname(__file__)  # <-- absolute dir the script is in
#     rel_path = "json_templates/vmc_sddc_create.json"
#     abs_file_path = os.path.join(script_dir_path, rel_path)
#     with open(abs_file_path, 'r', encoding='utf-8') as fp:
#         template_data = json.load(fp)
#
#     sddc_name = template_data['config']['name']
#     return sddc_name

#
# def test_vmc_sddc_present_state(salt_call_cli, get_sddc_list):
#     # Invoking present state when sddc is not present
#     response = salt_call_cli.run("state.single",
#                                  "vmc_sddc.present",
#                                  name="present",
#                                  hostname=_hostname,
#                                  refresh_key=_refresh_key,
#                                  authorization_host=_authorization_host,
#                                  org_id=_org_id,
#                                  sddc_name=_sddc_name,
#                                  verify_ssl=_verify_ssl,
#                                  cert=_cert
#                                  )
#     response_json = response.json
#     result = dict(list(response_json.values())[0])
#     changes = result["changes"]
#     # assert old array doesn't contain the sddc to be added
#     for sddc in changes['old']:
#         assert sddc['name'] != _sddc_name
#     assert result['comment'] == "SDDC added successfully"
#
#     time.sleep(50)
#
#     # Invoke present when sddc is already present
#     response = salt_call_cli.run("state.single",
#                                  "vmc_sddc.present",
#                                  name="present",
#                                  hostname=_hostname,
#                                  refresh_key=_refresh_key,
#                                  authorization_host=_authorization_host,
#                                  org_id=_org_id,
#                                  sddc_name=_sddc_name,
#                                  verify_ssl=_verify_ssl,
#                                  cert=_cert
#                                  )
#     response_json = response.json
#     result = dict(list(response_json.values())[0])
#     changes = result["changes"]
#     # assert no changes are done
#     assert changes == {}
#     assert result['comment'] == "SDDC is already present"
#
#
# def test_vmc_sddc_absent_state(salt_call_cli, get_sddc_list, create_sddc):
#     # Invoke absent to delete the sddc
#     response = salt_call_cli.run("state.single",
#                                  "vmc_sddc.absent",
#                                  name="absent",
#                                  hostname=_hostname,
#                                  refresh_key=_refresh_key,
#                                  authorization_host=_authorization_host,
#                                  org_id=_org_id,
#                                  sddc_id=create_sddc,
#                                  verify_ssl=_verify_ssl,
#                                  cert=_cert
#                                  )
#     response_json = response.json
#     result = dict(list(response_json.values())[0])
#     changes = result["changes"]
#
#     # assert old array contains the sddc to be removed
#     sddc_present = False
#     for sddc in changes['old']:
#         if sddc['id'] == create_sddc:
#             sddc_present = True
#             break
#     assert sddc_present is True
#
#
#     # assert new array doesn't contains the sddc to be removed
#     # time.sleep(20)
#     # for sddc in changes['new']:
#     #     assert sddc['id'] != create_sddc
#
#     sddc_absent = True
#     for sddc in changes['new']:
#         if sddc['id'] == create_sddc:
#             sddc_absent = False
#             break
#     assert sddc_absent is True
#
#     # Invoke absent when sddc is not present
#     response = salt_call_cli.run("state.single",
#                                  "vmc_sddc.absent",
#                                  name="absent",
#                                  hostname=_hostname,
#                                  refresh_key=_refresh_key,
#                                  authorization_host=_authorization_host,
#                                  org_id=_org_id,
#                                  sddc_id=create_sddc,
#                                  verify_ssl=_verify_ssl,
#                                  cert=_cert
#                                  )
#     response_json = response.json
#     result = dict(list(response_json.values())[0])
#     changes = result["changes"]
#     # assert no changes are done
#     assert changes == {}
#     assert result['comment'] == "SDDC is already absent"
