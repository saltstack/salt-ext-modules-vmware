"""
    Integration Tests for vmc_org_users execution module
"""
import json

import pytest


@pytest.fixture
def vmc_common_data(vmc_connect):
    data = vmc_connect.copy()
    data.pop("sddc_id")
    data.pop("vcenter_hostname")
    data["hostname"] = vmc_connect["authorization_host"]
    data.pop("authorization_host")
    return data


def test_sddc_smoke_test(salt_call_cli, vmc_common_data):
    # get the org users list
    ret = salt_call_cli.run("vmc_org_users.list", **vmc_common_data)
    result_as_json = ret.json
    assert "error" not in result_as_json
    existing_org_users = len(result_as_json["results"])

    # Add a new user to the org
    user_names = ["test@vmware.com"]
    organization_roles = [
        {"name": "org_member"},
        {"name": "developer"},
    ]
    ret = salt_call_cli.run(
        "vmc_org_users.add",
        user_names=user_names,
        organization_roles=organization_roles,
        **vmc_common_data,
    )
    result_as_json = ret.json
    assert "error" not in result_as_json

    # remove the user from org
    user_ids = ["test@vmware.com"]
    ret = salt_call_cli.run("vmc_org_users.remove", user_ids=user_ids, **vmc_common_data)
    result_as_json = ret.json
    assert "error" in result_as_json
    assert "Failed to get user" in result_as_json["message"]
