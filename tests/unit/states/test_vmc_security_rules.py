"""
    Unit tests for vmc_security_rules state module
"""
from unittest.mock import create_autospec
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_security_rules as vmc_security_rules_exec
import saltext.vmware.states.vmc_security_rules as vmc_security_rules


@pytest.fixture
def configure_loader_modules():
    return {vmc_security_rules: {}}


@pytest.fixture
def get_mocked_data():
    mocked_ok_response = {
        "action": "ALLOW",
        "resource_type": "Rule",
        "display_name": "vCenter Inbound Rule",
        "id": "rule_id",
        "is_default": False,
        "_system_owned": False,
        "_revision": 0,
        "_protection": "NOT_PROTECTED",
        "_create_user": "abc@vmware.com",
        "_create_time": 1616589005202,
        "_last_modified_user": "abc@vmware.com",
        "_last_modified_time": 1616589005206,
        "ip_protocol": "IPV4_IPV6",
        "path": "/infra/domains/mgw/gateway-policies/default/rules/vCenter_Inbound_Rule",
        "relative_path": "vCenter_Inbound_Rule",
        "parent_path": "/infra/domains/mgw/gateway-policies/default",
        "unique_id": "1015",
        "marked_for_delete": False,
        "overridden": False,
        "rule_id": 1015,
        "sequence_number": 10,
        "sources_excluded": False,
        "destinations_excluded": False,
        "source_groups": ["ANY"],
        "destination_groups": ["/infra/domains/mgw/groups/VCENTER"],
        "services": ["/infra/services/HTTPS"],
        "profiles": ["ANY"],
        "logged": False,
        "scope": ['/infra/labels/mgw"'],
        "disabled": False,
        "notes": "",
        "direction": "IN_OUT",
        "tag": "",
    }

    mocked_error_response = {
        "error": "The credentials were incorrect or the account specified has been locked."
    }
    mocked_hostname = "nsx-t.vmwarevmc.com"
    return mocked_hostname, mocked_ok_response, mocked_error_response


def test_present_state_when_error_from_get_by_id(get_mocked_data):
    mocked_hostname, mocked_ok_response, mocked_error_response = get_mocked_data
    mock_get_by_id = create_autospec(
        vmc_security_rules_exec.get_by_id, return_value=mocked_error_response
    )

    with patch.dict(vmc_security_rules.__salt__, {"vmc_security_rules.get_by_id": mock_get_by_id}):
        result = vmc_security_rules.present(
            name="test_present",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            rule_id=mocked_ok_response["id"],
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_state_when_error_from_create(get_mocked_data):
    mocked_hostname, mocked_ok_response, mocked_error_response = get_mocked_data
    mock_get_by_id = create_autospec(vmc_security_rules_exec.get_by_id, return_value={})
    mock_create = create_autospec(
        vmc_security_rules_exec.create, return_value=mocked_error_response
    )

    with patch.dict(
        vmc_security_rules.__salt__,
        {
            "vmc_security_rules.get_by_id": mock_get_by_id,
            "vmc_security_rules.create": mock_create,
        },
    ):
        result = vmc_security_rules.present(
            name="test_present",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            rule_id="rule-id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_state_when_error_from_update(get_mocked_data):
    mocked_hostname, mocked_ok_response, mocked_error_response = get_mocked_data
    mock_get_by_id = create_autospec(
        vmc_security_rules_exec.get_by_id, return_value=mocked_ok_response
    )
    mock_update = create_autospec(
        vmc_security_rules_exec.update, return_value=mocked_error_response
    )

    with patch.dict(
        vmc_security_rules.__salt__,
        {
            "vmc_security_rules.get_by_id": mock_get_by_id,
            "vmc_security_rules.update": mock_update,
        },
    ):
        result = vmc_security_rules.present(
            name="test_present",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
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


def test_present_state_during_update_to_add_a_new_field(get_mocked_data):
    mocked_hostname, mocked_ok_response, mocked_error_response = get_mocked_data
    mocked_updated_response = mocked_ok_response.copy()
    mocked_ok_response.pop("display_name")
    mock_get_by_id = create_autospec(
        vmc_security_rules_exec.get_by_id, side_effect=[mocked_ok_response, mocked_updated_response]
    )

    mocked_updated_response["display_name"] = "rule-1"
    mock_update = create_autospec(
        vmc_security_rules_exec.update, return_value=mocked_updated_response
    )

    with patch.dict(
        vmc_security_rules.__salt__,
        {
            "vmc_security_rules.get_by_id": mock_get_by_id,
            "vmc_security_rules.update": mock_update,
        },
    ):
        result = vmc_security_rules.present(
            name="test_present",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            rule_id=mocked_ok_response["id"],
            display_name="rule-1",
        )

    assert result is not None
    assert result["changes"]["old"] == mocked_ok_response
    assert result["changes"]["new"] == mocked_updated_response
    assert result["comment"] == "Updated Security rule rule_id"
    assert result["result"]


def test_present_to_create_when_module_returns_success_response(get_mocked_data):
    mocked_hostname, mocked_ok_response, mocked_error_response = get_mocked_data

    mock_get_by_id_response = create_autospec(vmc_security_rules_exec.get_by_id, return_value={})
    mock_create_response = create_autospec(
        vmc_security_rules_exec.create, return_value=mocked_ok_response
    )
    rule_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_security_rules.__salt__,
        {
            "vmc_security_rules.get_by_id": mock_get_by_id_response,
            "vmc_security_rules.create": mock_create_response,
        },
    ):
        result = vmc_security_rules.present(
            name="test_present",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            rule_id=rule_id,
        )

    assert result is not None
    assert result["changes"]["new"] == mocked_ok_response
    assert result["changes"]["old"] is None
    assert result["comment"] == "Created Security rule {}".format(rule_id)
    assert result["result"]


def test_present_to_update_when_module_returns_success_response(get_mocked_data):
    mocked_hostname, mocked_ok_response, mocked_error_response = get_mocked_data
    mocked_updated_security_rule = mocked_ok_response.copy()
    mocked_updated_security_rule["display_name"] = "rule-1"

    mock_get_by_id_response = create_autospec(
        vmc_security_rules_exec.get_by_id,
        side_effect=[mocked_ok_response, mocked_updated_security_rule],
    )
    mock_update_response = create_autospec(
        vmc_security_rules_exec.update, return_value=mocked_updated_security_rule
    )
    rule_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_security_rules.__salt__,
        {
            "vmc_security_rules.get_by_id": mock_get_by_id_response,
            "vmc_security_rules.update": mock_update_response,
        },
    ):
        result = vmc_security_rules.present(
            name="test_present",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            rule_id=rule_id,
            display_name="rule-1",
        )

    assert result is not None
    assert result["changes"]["new"] == mocked_updated_security_rule
    assert result["changes"]["old"] == mocked_ok_response
    assert result["comment"] == "Updated Security rule {}".format(rule_id)
    assert result["result"]


def test_present_to_update_when_get_by_id_after_update_returns_error(get_mocked_data):
    mocked_hostname, mocked_ok_response, mocked_error_response = get_mocked_data
    mocked_updated_security_rule = mocked_ok_response.copy()
    mocked_updated_security_rule["display_name"] = "rule-1"

    mock_get_by_id_response = create_autospec(
        vmc_security_rules_exec.get_by_id, side_effect=[mocked_ok_response, mocked_error_response]
    )
    mock_update_response = create_autospec(
        vmc_security_rules_exec.update, return_value=mocked_updated_security_rule
    )
    rule_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_security_rules.__salt__,
        {
            "vmc_security_rules.get_by_id": mock_get_by_id_response,
            "vmc_security_rules.update": mock_update_response,
        },
    ):
        result = vmc_security_rules.present(
            name="test_present",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
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


def test_present_to_update_when_user_input_and_existing_security_rule_has_identical_fields(
    get_mocked_data,
):
    mocked_hostname, mocked_ok_response, mocked_error_response = get_mocked_data

    mock_get_by_id_response = create_autospec(
        vmc_security_rules_exec.get_by_id, return_value=mocked_ok_response
    )

    with patch.dict(
        vmc_security_rules.__salt__,
        {"vmc_security_rules.get_by_id": mock_get_by_id_response},
    ):
        result = vmc_security_rules.present(
            name="test_present",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            rule_id=mocked_ok_response["id"],
        )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "Security rule exists already, no action to perform"
    assert result["result"]


def test_present_state_for_create_when_opts_test_is_true(get_mocked_data):
    mocked_hostname, mocked_ok_response, mocked_error_response = get_mocked_data

    mock_get_by_id_response = create_autospec(vmc_security_rules_exec.get_by_id, return_value={})
    rule_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_security_rules.__salt__,
        {"vmc_security_rules.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_security_rules.__opts__, {"test": True}):
            result = vmc_security_rules.present(
                name="test_present",
                hostname=mocked_hostname,
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                domain_id="domain_id",
                rule_id=rule_id,
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "State present will create Security rule {}".format(rule_id)
    assert result["result"] is None


def test_present_state_for_update_when_opts_test_is_true(get_mocked_data):
    mocked_hostname, mocked_ok_response, mocked_error_response = get_mocked_data

    mock_get_by_id_response = create_autospec(
        vmc_security_rules_exec.get_by_id, return_value=mocked_ok_response
    )
    rule_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_security_rules.__salt__,
        {"vmc_security_rules.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_security_rules.__opts__, {"test": True}):
            result = vmc_security_rules.present(
                name="test_present",
                hostname=mocked_hostname,
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                domain_id="domain_id",
                rule_id=rule_id,
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "State present will update Security rule {}".format(rule_id)
    assert result["result"] is None


def test_absent_state_to_delete_when_module_returns_success_response(get_mocked_data):
    mocked_hostname, mocked_ok_response, mocked_error_response = get_mocked_data

    mock_get_by_id_response = create_autospec(
        vmc_security_rules_exec.get_by_id, return_value=mocked_ok_response
    )
    mock_delete_response = create_autospec(
        vmc_security_rules_exec.delete, ok=True, return_value="Security rule Deleted Successfully"
    )
    rule_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_security_rules.__salt__,
        {
            "vmc_security_rules.get_by_id": mock_get_by_id_response,
            "vmc_security_rules.delete": mock_delete_response,
        },
    ):
        result = vmc_security_rules.absent(
            name="test_absent",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            rule_id=rule_id,
        )

    assert result is not None
    assert result["changes"] == {"new": None, "old": mocked_ok_response}
    assert result["comment"] == "Deleted Security rule {}".format(rule_id)
    assert result["result"]


def test_absent_state_when_object_to_delete_does_not_exists(get_mocked_data):
    mocked_hostname, mocked_ok_response, mocked_error_response = get_mocked_data

    mock_get_by_id_response = create_autospec(vmc_security_rules_exec.get_by_id, return_value={})
    rule_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_security_rules.__salt__,
        {"vmc_security_rules.get_by_id": mock_get_by_id_response},
    ):
        result = vmc_security_rules.absent(
            name="test_absent",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            rule_id=rule_id,
        )

    assert result is not None
    assert result["changes"] == {}
    assert result["comment"] == "No Security rule found with Id {}".format(rule_id)
    assert result["result"]


def test_absent_state_to_delete_when_opts_test_mode_is_true(get_mocked_data):
    mocked_hostname, mocked_ok_response, mocked_error_response = get_mocked_data

    mock_get_by_id_response = create_autospec(
        vmc_security_rules_exec.get_by_id, return_value={"results": [mocked_ok_response]}
    )
    rule_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_security_rules.__salt__,
        {"vmc_security_rules.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_security_rules.__opts__, {"test": True}):
            result = vmc_security_rules.absent(
                name="test_absent",
                hostname=mocked_hostname,
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                domain_id="domain_id",
                rule_id=rule_id,
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "State absent will delete Security rule with Id {}".format(rule_id)
    assert result["result"] is None


def test_absent_state_when_object_to_delete_doesn_not_exists_and_opts_test_mode_is_true(
    get_mocked_data,
):
    mocked_hostname, mocked_ok_response, mocked_error_response = get_mocked_data

    mock_get_by_id_response = create_autospec(vmc_security_rules_exec.get_by_id, return_value={})
    rule_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_security_rules.__salt__,
        {"vmc_security_rules.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_security_rules.__opts__, {"test": True}):
            result = vmc_security_rules.absent(
                name="test_absent",
                hostname=mocked_hostname,
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                domain_id="domain_id",
                rule_id=rule_id,
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result[
        "comment"
    ] == "State absent will do nothing as no Security rule found with Id {}".format(rule_id)
    assert result["result"] is None


def test_absent_with_error_from_delete(get_mocked_data):
    mocked_hostname, mocked_ok_response, mocked_error_response = get_mocked_data

    mock_get_by_id = create_autospec(
        vmc_security_rules_exec.get_by_id, return_value={"results": [mocked_ok_response]}
    )
    mock_delete = create_autospec(
        vmc_security_rules_exec.delete, return_value=mocked_error_response
    )

    with patch.dict(
        vmc_security_rules.__salt__,
        {
            "vmc_security_rules.get_by_id": mock_get_by_id,
            "vmc_security_rules.delete": mock_delete,
        },
    ):
        result = vmc_security_rules.absent(
            name="test_absent",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            rule_id="rule_id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_absent_state_when_error_from_get_by_id(get_mocked_data):
    mocked_hostname, mocked_ok_response, mocked_error_response = get_mocked_data
    mock_get_by_id = create_autospec(
        vmc_security_rules_exec.get_by_id, return_value=mocked_error_response
    )

    with patch.dict(vmc_security_rules.__salt__, {"vmc_security_rules.get_by_id": mock_get_by_id}):
        result = vmc_security_rules.absent(
            name="test_absent",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            rule_id=mocked_ok_response["id"],
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]
