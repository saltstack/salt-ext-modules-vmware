"""
    Unit tests for vmc_security_groups state module
"""
from unittest.mock import create_autospec
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_security_groups as vmc_security_groups_exec
import saltext.vmware.states.vmc_security_groups as vmc_security_groups


@pytest.fixture
def configure_loader_modules():
    return {vmc_security_groups: {}}


@pytest.fixture
def mocked_ok_response():
    response = {
        "expression": [
            {
                "member_type": "VirtualMachine",
                "key": "OSName",
                "operator": "EQUALS",
                "value": "Centos",
                "resource_type": "Condition",
                "id": "306e22a9-0060-4c11-8557-2ed927887e40",
                "path": "/infra/domains/cgw/groups/TEST_GROUP/condition-expressions/306e22a9-0060-4c11-8557-2ed927887e40",
                "relative_path": "306e22a9-0060-4c11-8557-2ed927887e40",
                "parent_path": "/infra/domains/cgw/groups/TEST_GROUP",
                "marked_for_delete": False,
                "overridden": False,
                "_protection": "NOT_PROTECTED",
            }
        ],
        "extended_expression": [],
        "reference": False,
        "resource_type": "Group",
        "id": "security_group_id",
        "display_name": "security_group_id",
        "description": "TEST Secority group",
        "path": "/infra/domains/cgw/groups/TEST_GROUP",
        "relative_path": "TEST_GROUP",
        "parent_path": "/infra/domains/cgw",
        "unique_id": "a6722585-da81-4609-be25-25cd7f7a89f2",
        "marked_for_delete": False,
        "overridden": False,
        "_create_time": 1618809345031,
        "_create_user": "pnaval@vmware.com",
        "_last_modified_time": 1618809345041,
        "_last_modified_user": "pnaval@vmware.com",
        "_system_owned": False,
        "_protection": "NOT_PROTECTED",
        "_revision": 0,
    }
    return response


@pytest.fixture
def mocked_error_response():
    error_response = {
        "error": "The credentials were incorrect or the account specified has been locked."
    }
    return error_response


def test_present_state_when_error_from_get_by_id(mocked_ok_response, mocked_error_response):
    mock_get_by_id = create_autospec(
        vmc_security_groups_exec.get_by_id, return_value=mocked_error_response
    )

    with patch.dict(
        vmc_security_groups.__salt__, {"vmc_security_groups.get_by_id": mock_get_by_id}
    ):
        result = vmc_security_groups.present(
            name=mocked_ok_response["id"],
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_state_when_error_from_create(mocked_error_response):
    mock_get_by_id = create_autospec(vmc_security_groups_exec.get_by_id, return_value={})
    mock_create = create_autospec(
        vmc_security_groups_exec.create, return_value=mocked_error_response
    )

    with patch.dict(
        vmc_security_groups.__salt__,
        {
            "vmc_security_groups.get_by_id": mock_get_by_id,
            "vmc_security_groups.create": mock_create,
        },
    ):
        result = vmc_security_groups.present(
            name="security_group_id",
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_state_when_error_from_update(mocked_ok_response, mocked_error_response):
    mock_get_by_id = create_autospec(
        vmc_security_groups_exec.get_by_id, return_value=mocked_ok_response
    )
    mock_update = create_autospec(
        vmc_security_groups_exec.update, return_value=mocked_error_response
    )

    with patch.dict(
        vmc_security_groups.__salt__,
        {
            "vmc_security_groups.get_by_id": mock_get_by_id,
            "vmc_security_groups.update": mock_update,
        },
    ):
        result = vmc_security_groups.present(
            name=mocked_ok_response["id"],
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            display_name="updated security_group_id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_state_during_update_to_add_a_new_field(mocked_ok_response):
    mocked_updated_response = mocked_ok_response.copy()
    mocked_ok_response.pop("display_name")
    mock_get_by_id = create_autospec(
        vmc_security_groups_exec.get_by_id,
        side_effect=[mocked_ok_response, mocked_updated_response],
    )

    mocked_updated_response["display_name"] = "security_group_1"
    mock_update = create_autospec(
        vmc_security_groups_exec.update, return_value=mocked_updated_response
    )

    with patch.dict(
        vmc_security_groups.__salt__,
        {
            "vmc_security_groups.get_by_id": mock_get_by_id,
            "vmc_security_groups.update": mock_update,
        },
    ):
        result = vmc_security_groups.present(
            name=mocked_ok_response["id"],
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            display_name="security_group_1",
        )

    assert result is not None
    assert result["changes"]["old"] == mocked_ok_response
    assert result["changes"]["new"] == mocked_updated_response
    assert result["comment"] == "Updated security group security_group_id"
    assert result["result"]


def test_present_to_create_when_module_returns_success_response(mocked_ok_response):
    mock_get_by_id_response = create_autospec(vmc_security_groups_exec.get_by_id, return_value={})
    mock_create_response = create_autospec(
        vmc_security_groups_exec.create, return_value=mocked_ok_response
    )
    security_group_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_security_groups.__salt__,
        {
            "vmc_security_groups.get_by_id": mock_get_by_id_response,
            "vmc_security_groups.create": mock_create_response,
        },
    ):
        result = vmc_security_groups.present(
            name=security_group_id,
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
        )

    assert result is not None
    assert result["changes"]["new"] == mocked_ok_response
    assert result["changes"]["old"] is None
    assert result["comment"] == "Created security group {}".format(security_group_id)
    assert result["result"]


def test_present_to_update_when_module_returns_success_response(mocked_ok_response):
    mocked_updated_security_group = mocked_ok_response.copy()
    mocked_updated_security_group["display_name"] = "security_group_id"

    mock_get_by_id_response = create_autospec(
        vmc_security_groups_exec.get_by_id,
        side_effect=[mocked_ok_response, mocked_updated_security_group],
    )
    mock_update_response = create_autospec(
        vmc_security_groups_exec.update, return_value=mocked_updated_security_group
    )
    security_group_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_security_groups.__salt__,
        {
            "vmc_security_groups.get_by_id": mock_get_by_id_response,
            "vmc_security_groups.update": mock_update_response,
        },
    ):
        result = vmc_security_groups.present(
            name=security_group_id,
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            display_name="updated security_group_id",
        )

    assert result is not None
    assert result["changes"]["new"] == mocked_updated_security_group
    assert result["changes"]["old"] == mocked_ok_response
    assert result["comment"] == "Updated security group {}".format(security_group_id)
    assert result["result"]


def test_present_to_update_when_get_by_id_after_update_returns_error(
    mocked_ok_response, mocked_error_response
):
    mocked_updated_security_group = mocked_ok_response.copy()
    mocked_updated_security_group["display_name"] = "updated security_group_id"

    mock_get_by_id_response = create_autospec(
        vmc_security_groups_exec.get_by_id, side_effect=[mocked_ok_response, mocked_error_response]
    )
    mock_update_response = create_autospec(
        vmc_security_groups_exec.update, return_value=mocked_updated_security_group
    )
    security_group_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_security_groups.__salt__,
        {
            "vmc_security_groups.get_by_id": mock_get_by_id_response,
            "vmc_security_groups.update": mock_update_response,
        },
    ):
        result = vmc_security_groups.present(
            name=security_group_id,
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            display_name="updated security_group_id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_to_update_when_user_input_and_existing_security_group_has_identical_fields(
    mocked_ok_response,
):
    mock_get_by_id_response = create_autospec(
        vmc_security_groups_exec.get_by_id, return_value=mocked_ok_response
    )

    with patch.dict(
        vmc_security_groups.__salt__,
        {"vmc_security_groups.get_by_id": mock_get_by_id_response},
    ):
        result = vmc_security_groups.present(
            name=mocked_ok_response["id"],
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
        )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "Security group exists already, no action to perform"
    assert result["result"]


def test_present_state_for_create_when_opts_test_is_true(mocked_ok_response):
    mock_get_by_id_response = create_autospec(vmc_security_groups_exec.get_by_id, return_value={})
    security_group_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_security_groups.__salt__,
        {"vmc_security_groups.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_security_groups.__opts__, {"test": True}):
            result = vmc_security_groups.present(
                name=security_group_id,
                hostname="nsx-t.vmwarevmc.com",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                domain_id="domain_id",
            )

    assert result is not None
    assert not result["changes"]
    assert result["comment"] == "Security group {} will be created".format(security_group_id)
    assert result["result"] is None


@pytest.mark.parametrize(
    "actual_args",
    [
        # all actual args are None
        ({}),
        # allow none have values
        ({"tags": [{"tag": "tag1", "scope": "scope1"}]}),
        # all args have values
        (
            {
                "description": "VMs Security groups",
                "expression": [
                    {
                        "member_type": "VirtualMachine",
                        "key": "OSName",
                        "operator": "EQUALS",
                        "value": "Centos",
                        "resource_type": "Condition",
                    }
                ],
                "tags": [{"tag": "tag1", "scope": "scope1"}],
            }
        ),
    ],
)
def test_present_state_during_create_should_correctly_pass_args(mocked_ok_response, actual_args):
    mocked_updated_response = mocked_ok_response.copy()
    mock_get_by_id_response = create_autospec(vmc_security_groups_exec.get_by_id, return_value={})
    mock_create_response = create_autospec(
        vmc_security_groups_exec.create, return_value=mocked_ok_response
    )

    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "domain_id": "domain_id",
        "verify_ssl": False,
    }

    mocked_updated_response.update(actual_args)
    actual_args.update(common_actual_args)
    mock_create = create_autospec(
        vmc_security_groups_exec.create, return_value=mocked_updated_response
    )

    with patch.dict(
        vmc_security_groups.__salt__,
        {
            "vmc_security_groups.get_by_id": mock_get_by_id_response,
            "vmc_security_groups.create": mock_create,
        },
    ):
        result = vmc_security_groups.present(name=mocked_ok_response["id"], **actual_args)

    call_kwargs = mock_create.mock_calls[0][-1]

    subset = {k: v for k, v in call_kwargs.items() if k in actual_args}
    assert subset == actual_args

    assert result is not None
    assert result["changes"]["old"] is None
    assert result["changes"]["new"] == mocked_updated_response
    assert result["comment"] == "Created security group security_group_id"
    assert result["result"]


def test_present_state_for_update_when_opts_test_is_true(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_security_groups_exec.get_by_id, return_value=mocked_ok_response
    )
    security_group_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_security_groups.__salt__,
        {"vmc_security_groups.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_security_groups.__opts__, {"test": True}):
            result = vmc_security_groups.present(
                name=security_group_id,
                hostname="nsx-t.vmwarevmc.com",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                domain_id="domain_id",
            )

    assert result is not None
    assert not result["changes"]
    assert result["comment"] == "Security group {} will be updated".format(security_group_id)
    assert result["result"] is None


@pytest.mark.parametrize(
    "actual_args",
    [
        # all actual args are None
        ({"display_name": "updated_security_groups"}),
        # allow none have values
        ({"tags": [{"tag": "tag1", "scope": "scope1"}]}),
        # all args have values
        (
            {
                "display_name": "Updated_Security_Groups",
                "description": "VMs Security groups",
                "expression": [
                    {
                        "member_type": "VirtualMachine",
                        "key": "OSName",
                        "operator": "EQUALS",
                        "value": "Centos",
                        "resource_type": "Condition",
                    }
                ],
                "tags": [{"tag": "tag1", "scope": "scope1"}],
            }
        ),
    ],
)
def test_present_state_during_update_should_correctly_pass_args(mocked_ok_response, actual_args):
    mocked_updated_response = mocked_ok_response.copy()
    mocked_ok_response.pop("display_name")
    mock_get_by_id = create_autospec(
        vmc_security_groups_exec.get_by_id,
        side_effect=[mocked_ok_response, mocked_updated_response],
    )

    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "domain_id": "domain_id",
        "verify_ssl": False,
    }

    mocked_updated_response.update(actual_args)
    actual_args.update(common_actual_args)
    mock_update = create_autospec(
        vmc_security_groups_exec.update, return_value=mocked_updated_response
    )

    with patch.dict(
        vmc_security_groups.__salt__,
        {
            "vmc_security_groups.get_by_id": mock_get_by_id,
            "vmc_security_groups.update": mock_update,
        },
    ):
        result = vmc_security_groups.present(name=mocked_ok_response["id"], **actual_args)

    call_kwargs = mock_update.mock_calls[0][-1]

    subset = {k: v for k, v in call_kwargs.items() if k in actual_args}
    assert subset == actual_args

    assert result is not None
    assert result["changes"]["old"] == mocked_ok_response
    assert result["changes"]["new"] == mocked_updated_response
    assert result["comment"] == "Updated security group security_group_id"
    assert result["result"]


def test_absent_state_to_delete_when_module_returns_success_response(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_security_groups_exec.get_by_id, return_value=mocked_ok_response
    )
    mock_delete_response = create_autospec(
        vmc_security_groups_exec.delete, ok=True, return_value="Security group Deleted Successfully"
    )
    security_group_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_security_groups.__salt__,
        {
            "vmc_security_groups.get_by_id": mock_get_by_id_response,
            "vmc_security_groups.delete": mock_delete_response,
        },
    ):
        result = vmc_security_groups.absent(
            name=security_group_id,
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
        )

    assert result is not None
    assert result["changes"] == {"new": None, "old": mocked_ok_response}
    assert result["comment"] == "Deleted security group {}".format(security_group_id)
    assert result["result"]


def test_absent_state_when_object_to_delete_does_not_exists(mocked_ok_response):
    mock_get_by_id_response = create_autospec(vmc_security_groups_exec.get_by_id, return_value={})
    security_group_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_security_groups.__salt__,
        {"vmc_security_groups.get_by_id": mock_get_by_id_response},
    ):
        result = vmc_security_groups.absent(
            name=security_group_id,
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert result["comment"] == "No security group found with ID {}".format(security_group_id)
    assert result["result"]


def test_absent_state_to_delete_when_opts_test_mode_is_true(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_security_groups_exec.get_by_id, return_value={"results": [mocked_ok_response]}
    )
    security_group_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_security_groups.__salt__,
        {"vmc_security_groups.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_security_groups.__opts__, {"test": True}):
            result = vmc_security_groups.absent(
                name=security_group_id,
                hostname="nsx-t.vmwarevmc.com",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                domain_id="domain_id",
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "State absent will delete security group with ID {}".format(
        security_group_id
    )
    assert result["result"] is None


def test_absent_state_when_object_to_delete_doesn_not_exists_and_opts_test_mode_is_true(
    mocked_ok_response,
):
    mock_get_by_id_response = create_autospec(vmc_security_groups_exec.get_by_id, return_value={})
    security_group_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_security_groups.__salt__,
        {"vmc_security_groups.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_security_groups.__opts__, {"test": True}):
            result = vmc_security_groups.absent(
                name=security_group_id,
                hostname="nsx-t.vmwarevmc.com",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                domain_id="domain_id",
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result[
        "comment"
    ] == "State absent will do nothing as no security group found with ID {}".format(
        security_group_id
    )
    assert result["result"] is None


def test_absent_with_error_from_delete(mocked_ok_response, mocked_error_response):
    mock_get_by_id = create_autospec(
        vmc_security_groups_exec.get_by_id, return_value={"results": [mocked_ok_response]}
    )
    mock_delete = create_autospec(
        vmc_security_groups_exec.delete, return_value=mocked_error_response
    )

    with patch.dict(
        vmc_security_groups.__salt__,
        {
            "vmc_security_groups.get_by_id": mock_get_by_id,
            "vmc_security_groups.delete": mock_delete,
        },
    ):
        result = vmc_security_groups.absent(
            name="security_group_id",
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_absent_state_when_error_from_get_by_id(mocked_ok_response, mocked_error_response):
    mock_get_by_id = create_autospec(
        vmc_security_groups_exec.get_by_id, return_value=mocked_error_response
    )

    with patch.dict(
        vmc_security_groups.__salt__, {"vmc_security_groups.get_by_id": mock_get_by_id}
    ):
        result = vmc_security_groups.absent(
            name=mocked_ok_response["id"],
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_when_get_by_id_returns_not_found_error(mocked_ok_response):
    error_response = {"error": "security group could not be found"}
    mock_get_by_id_response = create_autospec(
        vmc_security_groups_exec.get_by_id, return_value=error_response
    )
    mock_create_response = create_autospec(
        vmc_security_groups_exec.create, return_value=mocked_ok_response
    )

    security_group_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_security_groups.__salt__,
        {
            "vmc_security_groups.get_by_id": mock_get_by_id_response,
            "vmc_security_groups.create": mock_create_response,
        },
    ):
        result = vmc_security_groups.present(
            name=security_group_id,
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
        )

    assert result is not None
    assert result["changes"]["new"] == mocked_ok_response
    assert result["changes"]["old"] is None
    assert result["comment"] == "Created security group {}".format(security_group_id)
    assert result["result"]
