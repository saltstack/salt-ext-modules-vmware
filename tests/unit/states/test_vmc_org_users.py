from unittest.mock import create_autospec
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_org_users as vmc_org_users_exec
import saltext.vmware.states.vmc_org_users as vmc_org_users


@pytest.fixture
def mocked_ok_response():
    response = {
        "results": [
            {
                "user": {
                    "username": "aahammed@vmware.com",
                    "firstName": "Ajmal",
                    "lastName": "Ahammed",
                    "domain": "vmware.com",
                    "idpId": "vmware.com",
                    "accessible": True,
                    "acct": "aahammed@vmware.com",
                    "email": "aahammed@vmware.com",
                    "userId": "vmware.com:d3aac139-4043-416f-b13c-c69f058aa4fe",
                    "userProfile": None,
                },
                "orgId": "10e1092f-51d0-473a-80f8-137652fd0c39",
                "organizationRoles": [
                    {
                        "name": "org_member",
                        "membershipType": "DIRECT",
                        "displayName": "Organization Member",
                        "orgId": "10e1092f-51d0-473a-80f8-137652fd0c39",
                    }
                ],
                "serviceRoles": [
                    {
                        "serviceRoleNames": [
                            "vmc-user:full",
                        ],
                        "serviceRoles": [
                            {"name": "vmc-user:full", "membershipType": "DIRECT", "groupIds": []},
                        ],
                        "serviceDefinitionId": "tcq4LTfyZ_-UPdPAJIi2LhnvxmE_",
                    }
                ],
                "customRoles": [],
            }
        ]
    }
    return response


@pytest.fixture
def mocked_error_response():
    error_response = {
        "error": "The credentials were incorrect or the account specified has been locked."
    }
    return error_response


@pytest.fixture
def configure_loader_modules():
    return {vmc_org_users: {}}


def test_absent_state_to_remove_user_when_module_returns_success_response(mocked_ok_response):
    mock_users_list_response = create_autospec(
        vmc_org_users_exec.list_, return_value=mocked_ok_response
    )
    mock_delete_response = create_autospec(
        vmc_org_users_exec.remove,
        ok=True,
        return_value="User removed successfully",
    )
    user_name = mocked_ok_response["results"][0]["user"]["username"]

    with patch.dict(
        vmc_org_users.__salt__,
        {
            "vmc_org_users.list": mock_users_list_response,
            "vmc_org_users.remove": mock_delete_response,
        },
    ):
        result = vmc_org_users.absent(
            name=user_name,
            hostname="hostname",
            refresh_key="refresh_key",
            org_id="org_id",
            notify_users=False,
        )

    assert result is not None
    assert result["changes"] == {"new": None, "old": mocked_ok_response["results"][0]}
    assert result["comment"] == "Removed user {}".format(user_name)
    assert result["result"]


def test_absent_state_when_object_to_delete_does_not_exists(mocked_ok_response):
    mock_users_list_response = create_autospec(
        vmc_org_users_exec.list_, return_value={"results": []}
    )
    user_name = mocked_ok_response["results"][0]["user"]["username"]

    with patch.dict(
        vmc_org_users.__salt__,
        {"vmc_org_users.list": mock_users_list_response},
    ):
        result = vmc_org_users.absent(
            name=user_name,
            hostname="hostname",
            refresh_key="refresh_key",
            org_id="org_id",
            notify_users=False,
        )

    assert result is not None
    assert result["changes"] == {}
    assert result["comment"] == "No user found with username {}".format(user_name)
    assert result["result"]


def test_absent_state_to_delete_when_opts_test_mode_is_true(mocked_ok_response):
    mock_users_list_response = create_autospec(
        vmc_org_users_exec.list_, return_value=mocked_ok_response
    )
    user_name = mocked_ok_response["results"][0]["user"]["username"]

    with patch.dict(
        vmc_org_users.__salt__,
        {"vmc_org_users.list": mock_users_list_response},
    ):
        with patch.dict(vmc_org_users.__opts__, {"test": True}):
            result = vmc_org_users.absent(
                name=user_name,
                hostname="hostname",
                refresh_key="refresh_key",
                org_id="org_id",
                notify_users=False,
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "State absent will remove user with username {}".format(user_name)
    assert result["result"] is None


def test_absent_state_when_object_to_delete_does_not_exists_and_opts_test_mode_is_true(
    mocked_ok_response,
):
    mock_users_list_response = create_autospec(
        vmc_org_users_exec.list_, return_value={"results": []}
    )
    user_name = mocked_ok_response["results"][0]["user"]["username"]

    with patch.dict(
        vmc_org_users.__salt__,
        {"vmc_org_users.list": mock_users_list_response},
    ):
        with patch.dict(vmc_org_users.__opts__, {"test": True}):
            result = vmc_org_users.absent(
                name=user_name,
                hostname="hostname",
                refresh_key="refresh_key",
                org_id="org_id",
                notify_users=False,
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result[
        "comment"
    ] == "State absent will do nothing as no user found with username {}".format(user_name)
    assert result["result"] is None


def test_absent_with_error_from_delete(mocked_ok_response, mocked_error_response):
    mock_users_list_response = create_autospec(
        vmc_org_users_exec.list_, return_value=mocked_ok_response
    )
    mock_delete_response = create_autospec(
        vmc_org_users_exec.remove, return_value=mocked_error_response
    )
    user_name = mocked_ok_response["results"][0]["user"]["username"]

    with patch.dict(
        vmc_org_users.__salt__,
        {
            "vmc_org_users.list": mock_users_list_response,
            "vmc_org_users.remove": mock_delete_response,
        },
    ):
        result = vmc_org_users.absent(
            name=user_name,
            hostname="hostname",
            refresh_key="refresh_key",
            org_id="org_id",
            notify_users=False,
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_absent_state_when_error_from_getting_users_list(mocked_ok_response, mocked_error_response):
    mock_users_list_response = create_autospec(
        vmc_org_users_exec.list_, return_value=mocked_error_response
    )

    with patch.dict(
        vmc_org_users.__salt__,
        {"vmc_org_users.list": mock_users_list_response},
    ):
        result = vmc_org_users.absent(
            name="test-1",
            hostname="hostname",
            refresh_key="refresh_key",
            org_id="org_id",
            notify_users=False,
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "Failed to get users for given org : The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_state_when_error_from_getting_users_list(
    mocked_ok_response, mocked_error_response
):
    mock_users_list_response = create_autospec(
        vmc_org_users_exec.list_, return_value={"error": "The credentials were incorrect."}
    )

    with patch.dict(
        vmc_org_users.__salt__,
        {"vmc_org_users.list": mock_users_list_response},
    ):
        result = vmc_org_users.present(
            name="user_name",
            hostname="hostname",
            refresh_key="refresh_key",
            org_id="org_id",
            organization_roles=[
                {
                    "name": "org_member",
                    "membershipType": "DIRECT",
                    "displayName": "Organization Member",
                    "orgId": "org-id",
                }
            ],
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"] == "Failed to get users for given org : The credentials were incorrect."
    )
    assert not result["result"]


def test_present_state_when_error_from_create(mocked_error_response):
    mock_users_list_response = create_autospec(
        vmc_org_users_exec.list_, return_value={"results": []}
    )
    mock_invite = create_autospec(
        vmc_org_users_exec.invite, return_value={"error": "The credentials were incorrect."}
    )

    with patch.dict(
        vmc_org_users.__salt__,
        {
            "vmc_org_users.list": mock_users_list_response,
            "vmc_org_users.invite": mock_invite,
        },
    ):
        result = vmc_org_users.present(
            name="user_name",
            hostname="hostname",
            refresh_key="refresh_key",
            org_id="org_id",
            organization_roles=[
                {
                    "name": "org_member",
                    "membershipType": "DIRECT",
                    "displayName": "Organization Member",
                    "orgId": "org-id",
                }
            ],
        )

    assert result is not None
    assert result["changes"] == {}
    assert result["comment"] == "Failed to invite user : The credentials were incorrect."
    assert not result["result"]


def test_present_to_create_when_module_returns_success_response(mocked_ok_response):
    mock_users_list_response = create_autospec(
        vmc_org_users_exec.list_, return_value={"results": []}
    )
    mock_invite_response = create_autospec(
        vmc_org_users_exec.invite, return_value=mocked_ok_response
    )
    user_name = mocked_ok_response["results"][0]["user"]["username"]

    with patch.dict(
        vmc_org_users.__salt__,
        {
            "vmc_org_users.list": mock_users_list_response,
            "vmc_org_users.invite": mock_invite_response,
        },
    ):
        result = vmc_org_users.present(
            name=user_name,
            hostname="hostname",
            refresh_key="refresh_key",
            org_id="org_id",
            organization_roles=[
                {
                    "name": "org_member",
                    "membershipType": "DIRECT",
                    "displayName": "Organization Member",
                    "orgId": "org-id",
                }
            ],
        )

    assert result is not None
    assert result["changes"]["new"] == mocked_ok_response
    assert result["changes"]["old"] is None
    assert result["comment"] == "Invited user {} successfully".format(user_name)
    assert result["result"]


def test_present_state_for_create_when_opts_test_is_true(mocked_ok_response):
    mock_users_list_response = create_autospec(
        vmc_org_users_exec.list_, return_value={"results": []}
    )
    user_name = mocked_ok_response["results"][0]["user"]["username"]

    with patch.dict(
        vmc_org_users.__salt__,
        {"vmc_org_users.list": mock_users_list_response},
    ):
        with patch.dict(vmc_org_users.__opts__, {"test": True}):
            result = vmc_org_users.present(
                name=user_name,
                hostname="hostname",
                refresh_key="refresh_key",
                org_id="org_id",
                organization_roles=[
                    {
                        "name": "org_member",
                        "membershipType": "DIRECT",
                        "displayName": "Organization Member",
                        "orgId": "org-id",
                    }
                ],
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "User {} would have been invited".format(user_name)
    assert result["result"] is None


@pytest.mark.parametrize(
    "actual_args",
    [
        # all actual args are None
        ({}),
        # all args have values
        (
            {
                "skip_notify": False,
                "custom_roles": None,
                "service_roles": None,
                "skip_notify_registration": False,
                "invited_by": None,
                "custom_groups_ids": None,
            }
        ),
    ],
)
def test_present_state_during_create_should_correctly_pass_args(mocked_ok_response, actual_args):
    mock_users_list_response = create_autospec(
        vmc_org_users_exec.list_, return_value={"results": []}
    )
    mock_invite_response = mocked_ok_response.copy()
    user_name = mocked_ok_response["results"][0]["user"]["username"]
    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "org_id": "org_id",
        "organization_roles": [
            {
                "name": "org_member",
                "membershipType": "DIRECT",
                "displayName": "Organization Member",
                "orgId": "org-id",
            }
        ],
        "verify_ssl": False,
    }

    mock_invite_response.update(actual_args)
    actual_args.update(common_actual_args)
    mock_invite = create_autospec(vmc_org_users_exec.invite, return_value=mock_invite_response)

    with patch.dict(
        vmc_org_users.__salt__,
        {
            "vmc_org_users.list": mock_users_list_response,
            "vmc_org_users.invite": mock_invite,
        },
    ):
        result = vmc_org_users.present(name=user_name, **actual_args)

    call_kwargs = mock_invite.mock_calls[0][-1]

    subset = {k: v for k, v in call_kwargs.items() if k in actual_args}
    assert subset == actual_args

    assert result is not None
    assert result["changes"]["old"] is None
    assert result["changes"]["new"] == mock_invite_response
    assert result["comment"] == "Invited user {} successfully".format(user_name)
    assert result["result"]
