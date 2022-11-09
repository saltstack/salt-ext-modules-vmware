"""
    Integration Tests for vmc_org_user state module
"""
import pytest


@pytest.fixture
def vmc_common_data(vmc_connect):
    data = vmc_connect.copy()
    data.pop("vcenter_hostname")
    data.pop("sddc_id")
    data["hostname"] = data.pop("authorization_host")
    return data


@pytest.fixture
def user_name():
    return "test@vmware.com"


def test_vmc_org_user_state_module(salt_call_cli, vmc_common_data, user_name):
    # Invoke invited state to invite the user
    response = salt_call_cli.run(
        "state.single",
        "vmc_org_user.invited",
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
    assert result["comment"] == "Invited {} successfully".format(user_name)

    # Invoke absent to remove the user
    response = salt_call_cli.run(
        "state.single", "vmc_org_user.absent", name=user_name, **vmc_common_data
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes == {}
    assert result["comment"] == "No user found with username {}".format(user_name)
