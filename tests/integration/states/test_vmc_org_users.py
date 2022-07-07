"""
    Integration Tests for vmc_org_users state module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def vmc_common_data(vmc_connect):
    data = vmc_connect.copy()
    data.pop("vcenter_hostname")
    data.pop("sddc_id")
    data["hostname"] = data["authorization_host"]
    data.pop("authorization_host")
    return data


@pytest.fixture
def request_headers(vmc_common_data):
    return vmc_request.get_headers(vmc_common_data["refresh_key"])


@pytest.fixture
def user_name():
    return "test@vmware.com"


def test_vmc_org_users_state_module(salt_call_cli, vmc_common_data, user_name):
    # Invoke present state to invite the user
    response = salt_call_cli.run(
        "state.single",
        "vmc_org_users.present",
        name=user_name,
        organization_roles=[
            {
                "name": "org_member",
                "membershipType": "DIRECT",
                "displayName": "Organization Member",
                "orgId": "org-id",
            }
        ],
        **vmc_common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"] is None
    assert result["comment"] == "Invited user {} successfully".format(user_name)

    # # Invoke present state where user already exist
    # response = salt_call_cli.run(
    #     "state.single",
    #     "vmc_org_users.present",
    #     name=user_name,
    #     organization_roles=[
    #         {
    #             "name": "org_member",
    #             "membershipType": "DIRECT",
    #             "displayName": "Organization Member",
    #             "orgId": "org-id",
    #         }
    #     ],
    #     **vmc_common_data,
    # )
    # response_json = response.json
    # result = list(response_json.values())[0]
    # changes = result["changes"]
    #
    # # assert no changes are done
    # assert changes == {}
    # assert result["comment"] == "User is already present"

    # Invoke absent to remove the user
    response = salt_call_cli.run(
        "state.single", "vmc_org_users.absent", name=user_name, **vmc_common_data
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes == {}
    assert result["comment"] == "No user found with username {}".format(user_name)
