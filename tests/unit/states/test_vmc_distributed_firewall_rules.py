"""
    Unit tests for vmc_distributed_firewall_rules state module
"""
from unittest.mock import create_autospec
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_distributed_firewall_rules as vmc_distributed_firewall_rules_exec
import saltext.vmware.states.vmc_distributed_firewall_rules as vmc_distributed_firewall_rules


@pytest.fixture
def configure_loader_modules():
    return {vmc_distributed_firewall_rules: {}}


@pytest.fixture
def mocked_ok_response():
    response = {
        "action": "DROP",
        "resource_type": "Rule",
        "id": "rule_id",
        "display_name": "DFR_001",
        "description": " comm entry",
        "path": "/infra/domains/cgw/security-policies/SP_1/rules/DFR_001",
        "relative_path": "DFR_001",
        "parent_path": "/infra/domains/cgw/security-policies/SP_1",
        "unique_id": "1026",
        "marked_for_delete": False,
        "overridden": False,
        "rule_id": 1026,
        "sequence_number": 1,
        "sources_excluded": False,
        "destinations_excluded": False,
        "source_groups": ["/infra/domains/cgw/groups/SG_CGW_001"],
        "destination_groups": ["ANY"],
        "services": ["ANY"],
        "profiles": ["ANY"],
        "logged": False,
        "scope": ["ANY"],
        "disabled": False,
        "direction": "IN_OUT",
        "ip_protocol": "IPV4_IPV6",
        "is_default": False,
        "_create_time": 1619101829635,
        "_create_user": "pnaval@vmware.com",
        "_last_modified_time": 1619101829641,
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
        vmc_distributed_firewall_rules_exec.get_by_id, return_value=mocked_error_response
    )

    with patch.dict(
        vmc_distributed_firewall_rules.__salt__,
        {"vmc_distributed_firewall_rules.get_by_id": mock_get_by_id},
    ):
        result = vmc_distributed_firewall_rules.present(
            name="test_present",
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            rule_id=mocked_ok_response["id"],
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_state_when_error_from_create(mocked_error_response):
    mock_get_by_id = create_autospec(vmc_distributed_firewall_rules_exec.get_by_id, return_value={})
    mock_create = create_autospec(
        vmc_distributed_firewall_rules_exec.create, return_value=mocked_error_response
    )

    with patch.dict(
        vmc_distributed_firewall_rules.__salt__,
        {
            "vmc_distributed_firewall_rules.get_by_id": mock_get_by_id,
            "vmc_distributed_firewall_rules.create": mock_create,
        },
    ):
        result = vmc_distributed_firewall_rules.present(
            name="test_present",
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            rule_id="rule-id",
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
        vmc_distributed_firewall_rules_exec.get_by_id, return_value=mocked_ok_response
    )
    mock_update = create_autospec(
        vmc_distributed_firewall_rules_exec.update, return_value=mocked_error_response
    )

    with patch.dict(
        vmc_distributed_firewall_rules.__salt__,
        {
            "vmc_distributed_firewall_rules.get_by_id": mock_get_by_id,
            "vmc_distributed_firewall_rules.update": mock_update,
        },
    ):
        result = vmc_distributed_firewall_rules.present(
            name="test_present",
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            rule_id=mocked_ok_response["id"],
            display_name="rule-1",
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
        vmc_distributed_firewall_rules_exec.get_by_id,
        side_effect=[mocked_ok_response, mocked_updated_response],
    )

    mocked_updated_response["display_name"] = "rule-1"
    mock_update = create_autospec(
        vmc_distributed_firewall_rules_exec.update, return_value=mocked_updated_response
    )

    with patch.dict(
        vmc_distributed_firewall_rules.__salt__,
        {
            "vmc_distributed_firewall_rules.get_by_id": mock_get_by_id,
            "vmc_distributed_firewall_rules.update": mock_update,
        },
    ):
        result = vmc_distributed_firewall_rules.present(
            name="test_present",
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            rule_id=mocked_ok_response["id"],
            display_name="rule-1",
        )

    assert result is not None
    assert result["changes"]["old"] == mocked_ok_response
    assert result["changes"]["new"] == mocked_updated_response
    assert result["comment"] == "Updated Distributed firewall rule rule_id"
    assert result["result"]


def test_present_to_create_when_module_returns_success_response(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_distributed_firewall_rules_exec.get_by_id, return_value={}
    )
    mock_create_response = create_autospec(
        vmc_distributed_firewall_rules_exec.create, return_value=mocked_ok_response
    )
    rule_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_distributed_firewall_rules.__salt__,
        {
            "vmc_distributed_firewall_rules.get_by_id": mock_get_by_id_response,
            "vmc_distributed_firewall_rules.create": mock_create_response,
        },
    ):
        result = vmc_distributed_firewall_rules.present(
            name="test_present",
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            rule_id=rule_id,
        )

    assert result is not None
    assert result["changes"]["new"] == mocked_ok_response
    assert result["changes"]["old"] is None
    assert result["comment"] == "Created Distributed firewall rule {}".format(rule_id)
    assert result["result"]


def test_present_to_update_when_module_returns_success_response(mocked_ok_response):
    mocked_updated_distributed_firewall_rule = mocked_ok_response.copy()
    mocked_updated_distributed_firewall_rule["display_name"] = "rule-1"

    mock_get_by_id_response = create_autospec(
        vmc_distributed_firewall_rules_exec.get_by_id,
        side_effect=[mocked_ok_response, mocked_updated_distributed_firewall_rule],
    )
    mock_update_response = create_autospec(
        vmc_distributed_firewall_rules_exec.update,
        return_value=mocked_updated_distributed_firewall_rule,
    )
    rule_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_distributed_firewall_rules.__salt__,
        {
            "vmc_distributed_firewall_rules.get_by_id": mock_get_by_id_response,
            "vmc_distributed_firewall_rules.update": mock_update_response,
        },
    ):
        result = vmc_distributed_firewall_rules.present(
            name="test_present",
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            rule_id=rule_id,
            security_policy_id="security_policy_id",
            display_name="rule-1",
        )

    assert result is not None
    assert result["changes"]["new"] == mocked_updated_distributed_firewall_rule
    assert result["changes"]["old"] == mocked_ok_response
    assert result["comment"] == "Updated Distributed firewall rule {}".format(rule_id)
    assert result["result"]


def test_present_to_update_when_get_by_id_after_update_returns_error(
    mocked_ok_response, mocked_error_response
):
    mocked_updated_distributed_firewall_rule = mocked_ok_response.copy()
    mocked_updated_distributed_firewall_rule["display_name"] = "rule-1"

    mock_get_by_id_response = create_autospec(
        vmc_distributed_firewall_rules_exec.get_by_id,
        side_effect=[mocked_ok_response, mocked_error_response],
    )
    mock_update_response = create_autospec(
        vmc_distributed_firewall_rules_exec.update,
        return_value=mocked_updated_distributed_firewall_rule,
    )
    rule_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_distributed_firewall_rules.__salt__,
        {
            "vmc_distributed_firewall_rules.get_by_id": mock_get_by_id_response,
            "vmc_distributed_firewall_rules.update": mock_update_response,
        },
    ):
        result = vmc_distributed_firewall_rules.present(
            name="test_present",
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            rule_id=rule_id,
            display_name="rule-1",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_to_update_when_user_input_and_existing_distributed_firewall_rule_has_identical_fields(
    mocked_ok_response,
):
    mock_get_by_id_response = create_autospec(
        vmc_distributed_firewall_rules_exec.get_by_id, return_value=mocked_ok_response
    )

    with patch.dict(
        vmc_distributed_firewall_rules.__salt__,
        {"vmc_distributed_firewall_rules.get_by_id": mock_get_by_id_response},
    ):
        result = vmc_distributed_firewall_rules.present(
            name="test_present",
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            rule_id=mocked_ok_response["id"],
        )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "Distributed firewall rule exists already, no action to perform"
    assert result["result"]


def test_present_state_for_create_when_opts_test_is_true(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_distributed_firewall_rules_exec.get_by_id, return_value={}
    )
    rule_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_distributed_firewall_rules.__salt__,
        {"vmc_distributed_firewall_rules.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_distributed_firewall_rules.__opts__, {"test": True}):
            result = vmc_distributed_firewall_rules.present(
                name="test_present",
                hostname="nsx-t.vmwarevmc.com",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                domain_id="domain_id",
                security_policy_id="security_policy_id",
                rule_id=rule_id,
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "State present will create Distributed firewall rule {}".format(
        rule_id
    )
    assert result["result"] is None


def test_present_state_for_update_when_opts_test_is_true(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_distributed_firewall_rules_exec.get_by_id, return_value=mocked_ok_response
    )
    rule_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_distributed_firewall_rules.__salt__,
        {"vmc_distributed_firewall_rules.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_distributed_firewall_rules.__opts__, {"test": True}):
            result = vmc_distributed_firewall_rules.present(
                name="test_present",
                hostname="nsx-t.vmwarevmc.com",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                domain_id="domain_id",
                security_policy_id="security_policy_id",
                rule_id=rule_id,
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "State present will update Distributed firewall rule {}".format(
        rule_id
    )
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
                "source_groups": ["ANY"],
                "destination_groups": ["ANY"],
                "services": ["HTTPS"],
                "scope": ["ANY"],
                "action": "DROP",
                "sequence_number": 0,
                "disabled": False,
                "logged": False,
                "description": "description",
                "direction": "IN_OUT",
                "notes": "notes",
                "tag": "tag",
                "tags": [{"tag": "tag1", "scope": "scope1"}],
            }
        ),
    ],
)
def test_present_state_during_create_should_correctly_pass_args(mocked_ok_response, actual_args):
    mocked_updated_response = mocked_ok_response.copy()
    mock_get_by_id_response = create_autospec(
        vmc_distributed_firewall_rules_exec.get_by_id, return_value={}
    )
    mock_create_response = create_autospec(
        vmc_distributed_firewall_rules_exec.create, return_value=mocked_ok_response
    )

    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "domain_id": "domain_id",
        "security_policy_id": "security_policy_id",
        "rule_id": mocked_ok_response["id"],
        "verify_ssl": False,
    }

    mocked_updated_response.update(actual_args)
    actual_args.update(common_actual_args)
    mock_create = create_autospec(
        vmc_distributed_firewall_rules_exec.create, return_value=mocked_updated_response
    )

    with patch.dict(
        vmc_distributed_firewall_rules.__salt__,
        {
            "vmc_distributed_firewall_rules.get_by_id": mock_get_by_id_response,
            "vmc_distributed_firewall_rules.create": mock_create,
        },
    ):
        result = vmc_distributed_firewall_rules.present(
            name="distributed firewall rule create", **actual_args
        )

    call_kwargs = mock_create.mock_calls[0][-1]

    subset = {k: v for k, v in call_kwargs.items() if k in actual_args}
    assert subset == actual_args

    assert result is not None
    assert result["changes"]["old"] is None
    assert result["changes"]["new"] == mocked_updated_response
    assert result["comment"] == "Created Distributed firewall rule rule_id"
    assert result["result"]


@pytest.mark.parametrize(
    "actual_args",
    [  # Only one value in update
        ({"display_name": "Updated distributed firewall rule"}),
        # allow none have values
        ({"tags": [{"tag": "tag1", "scope": "scope1"}]}),
        # all args have values
        (
            {
                "source_groups": ["ANY"],
                "destination_groups": ["ANY"],
                "services": ["HTTPS"],
                "scope": ["ANY"],
                "action": "DROP",
                "sequence_number": 0,
                "disabled": False,
                "logged": False,
                "description": "description",
                "direction": "IN_OUT",
                "notes": "notes",
                "tag": "tag",
                "tags": [{"tag": "tag1", "scope": "scope1"}],
            }
        ),
    ],
)
def test_present_state_during_update_should_correctly_pass_args(mocked_ok_response, actual_args):
    mocked_updated_response = mocked_ok_response.copy()
    mocked_ok_response.pop("display_name")
    mock_get_by_id = create_autospec(
        vmc_distributed_firewall_rules_exec.get_by_id,
        side_effect=[mocked_ok_response, mocked_updated_response],
    )

    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "domain_id": "domain_id",
        "security_policy_id": "security_policy_id",
        "rule_id": mocked_ok_response["id"],
        "verify_ssl": False,
    }

    mocked_updated_response.update(actual_args)
    actual_args.update(common_actual_args)
    mock_update = create_autospec(
        vmc_distributed_firewall_rules_exec.update, return_value=mocked_updated_response
    )

    with patch.dict(
        vmc_distributed_firewall_rules.__salt__,
        {
            "vmc_distributed_firewall_rules.get_by_id": mock_get_by_id,
            "vmc_distributed_firewall_rules.update": mock_update,
        },
    ):
        result = vmc_distributed_firewall_rules.present(
            name="distributed firewall rule update", **actual_args
        )

    call_kwargs = mock_update.mock_calls[0][-1]

    subset = {k: v for k, v in call_kwargs.items() if k in actual_args}
    assert subset == actual_args

    assert result is not None
    assert result["changes"]["old"] == mocked_ok_response
    assert result["changes"]["new"] == mocked_updated_response
    assert result["comment"] == "Updated Distributed firewall rule rule_id"
    assert result["result"]


def test_absent_state_to_delete_when_module_returns_success_response(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_distributed_firewall_rules_exec.get_by_id, return_value=mocked_ok_response
    )
    mock_delete_response = create_autospec(
        vmc_distributed_firewall_rules_exec.delete,
        ok=True,
        return_value="Distributed firewall rule Deleted Successfully",
    )
    rule_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_distributed_firewall_rules.__salt__,
        {
            "vmc_distributed_firewall_rules.get_by_id": mock_get_by_id_response,
            "vmc_distributed_firewall_rules.delete": mock_delete_response,
        },
    ):
        result = vmc_distributed_firewall_rules.absent(
            name="test_absent",
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            rule_id=rule_id,
        )

    assert result is not None
    assert result["changes"] == {"new": None, "old": mocked_ok_response}
    assert result["comment"] == "Deleted Distributed firewall rule {}".format(rule_id)
    assert result["result"]


def test_absent_state_when_object_to_delete_does_not_exists(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_distributed_firewall_rules_exec.get_by_id, return_value={}
    )
    rule_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_distributed_firewall_rules.__salt__,
        {"vmc_distributed_firewall_rules.get_by_id": mock_get_by_id_response},
    ):
        result = vmc_distributed_firewall_rules.absent(
            name="test_absent",
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            rule_id=rule_id,
        )

    assert result is not None
    assert result["changes"] == {}
    assert result["comment"] == "No Distributed firewall rule found with Id {}".format(rule_id)
    assert result["result"]


def test_absent_state_to_delete_when_opts_test_mode_is_true(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_distributed_firewall_rules_exec.get_by_id,
        return_value={"results": [mocked_ok_response]},
    )
    rule_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_distributed_firewall_rules.__salt__,
        {"vmc_distributed_firewall_rules.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_distributed_firewall_rules.__opts__, {"test": True}):
            result = vmc_distributed_firewall_rules.absent(
                name="test_absent",
                hostname="nsx-t.vmwarevmc.com",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                domain_id="domain_id",
                security_policy_id="security_policy_id",
                rule_id=rule_id,
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result[
        "comment"
    ] == "State absent will delete Distributed firewall rule with Id {}".format(rule_id)
    assert result["result"] is None


def test_absent_state_when_object_to_delete_doesn_not_exists_and_opts_test_mode_is_true(
    mocked_ok_response,
):
    mock_get_by_id_response = create_autospec(
        vmc_distributed_firewall_rules_exec.get_by_id, return_value={}
    )
    rule_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_distributed_firewall_rules.__salt__,
        {"vmc_distributed_firewall_rules.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_distributed_firewall_rules.__opts__, {"test": True}):
            result = vmc_distributed_firewall_rules.absent(
                name="test_absent",
                hostname="nsx-t.vmwarevmc.com",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                domain_id="domain_id",
                security_policy_id="security_policy_id",
                rule_id=rule_id,
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result[
        "comment"
    ] == "State absent will do nothing as no Distributed firewall rule found with Id {}".format(
        rule_id
    )
    assert result["result"] is None


def test_absent_with_error_from_delete(mocked_ok_response, mocked_error_response):
    mock_get_by_id = create_autospec(
        vmc_distributed_firewall_rules_exec.get_by_id,
        return_value={"results": [mocked_ok_response]},
    )
    mock_delete = create_autospec(
        vmc_distributed_firewall_rules_exec.get_by_id, return_value=mocked_error_response
    )

    with patch.dict(
        vmc_distributed_firewall_rules.__salt__,
        {
            "vmc_distributed_firewall_rules.get_by_id": mock_get_by_id,
            "vmc_distributed_firewall_rules.delete": mock_delete,
        },
    ):
        result = vmc_distributed_firewall_rules.absent(
            name="test_absent",
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            rule_id="rule_id",
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
        vmc_distributed_firewall_rules_exec.get_by_id, return_value=mocked_error_response
    )

    with patch.dict(
        vmc_distributed_firewall_rules.__salt__,
        {"vmc_distributed_firewall_rules.get_by_id": mock_get_by_id},
    ):
        result = vmc_distributed_firewall_rules.absent(
            name="test_absent",
            hostname="nsx-t.vmwarevmc.com",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            rule_id=mocked_ok_response["id"],
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]
