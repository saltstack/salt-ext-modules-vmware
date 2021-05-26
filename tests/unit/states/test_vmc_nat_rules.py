"""
    Unit tests for vmc_nat_rules state module
"""
from __future__ import absolute_import, print_function, unicode_literals
import pytest

import saltext.vmware.states.vmc_nat_rules as vmc_nat_rules

from unittest.mock import patch, MagicMock

@pytest.fixture
def configure_loader_modules():
    return {vmc_nat_rules: {}}


def _get_mocked_data():
    mocked_ok_response = {
        'sequence_number': 0, 'action': 'REFLEXIVE', 'source_network': '192.168.1.1',
        'service': '', 'translated_network': '10.182.171.36',
        'scope': ['/infra/labels/cgw-public'], 'enabled': False,
        'logging': False, 'firewall_match': 'MATCH_INTERNAL_ADDRESS',
        'resource_type': 'PolicyNatRule', 'id': 'nat_rule',
        'display_name': 'nat_rule',
        'path': '/infra/tier-1s/cgw/nat/USER/nat-rules/NAT_RULE9',
        'relative_path': 'NAT_RULE9', 'parent_path': '/infra/tier-1s/cgw/nat/USER',
        'unique_id': '7039a170-6f18-43b0-9ae0-a172c48fae8a',
        'marked_for_delete': False, 'overridden': False, '_create_time': 1617867323573,
        '_create_user': 'pnaval@vmware.com', '_last_modified_time': 1617867323577,
        '_last_modified_user': 'pnaval@vmware.com', '_system_owned': False,
        '_protection': 'NOT_PROTECTED', '_revision': 0
    }

    mocked_error_response = {
        "error": "The credentials were incorrect or the account specified has been locked."
    }
    mocked_hostname = "nsx-t.vmwarevmc.com"
    return mocked_hostname, mocked_ok_response, mocked_error_response


def test_present_state_when_error_from_get_by_id():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()
    mock_get_by_id = MagicMock(return_value=mocked_error_response)

    with patch.dict(
        vmc_nat_rules.__salt__, {"vmc_nat_rules.get_by_id": mock_get_by_id}
    ):
        result = vmc_nat_rules.present(
            name="test_present",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            nat_rule=mocked_ok_response["id"]
        )

    assert result is not None
    assert result["changes"] == {}
    assert result["comment"] == "The credentials were incorrect or the account specified has been locked."
    assert not result["result"]


def test_present_state_when_error_from_create():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()
    mock_get_by_id = MagicMock(return_value={})
    mock_create = MagicMock(return_value=mocked_error_response)

    with patch.dict(
        vmc_nat_rules.__salt__,
        {
            "vmc_nat_rules.get_by_id": mock_get_by_id,
            "vmc_nat_rules.create": mock_create,
        },
    ):
        result = vmc_nat_rules.present(
            name="test_present",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            nat_rule="nat_rule"
        )

    assert result is not None
    assert result["changes"] == {}
    assert result["comment"] == "The credentials were incorrect or the account specified has been locked."
    assert not result["result"]


def test_present_state_when_error_from_update():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()
    mock_get_by_id = MagicMock(return_value=mocked_ok_response)
    mock_update = MagicMock(return_value=mocked_error_response)

    with patch.dict(
        vmc_nat_rules.__salt__,
        {
            "vmc_nat_rules.get_by_id": mock_get_by_id,
            "vmc_nat_rules.update": mock_update,
        },
    ):
        result = vmc_nat_rules.present(
            name="test_present",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            nat_rule=mocked_ok_response["id"],
            display_name="rule-1"
        )

    assert result is not None
    assert result["changes"] == {}
    assert result["comment"] == "The credentials were incorrect or the account specified has been locked."
    assert not result["result"]


def test_present_state_during_update_to_add_a_new_field():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()
    mocked_updated_response = mocked_ok_response.copy()
    mocked_ok_response.pop("display_name")
    mock_get_by_id = MagicMock(side_effect=[mocked_ok_response, mocked_updated_response])

    mocked_updated_response["display_name"] = "rule-1"
    mock_update = MagicMock(return_value=mocked_updated_response)

    with patch.dict(
        vmc_nat_rules.__salt__,
        {
            "vmc_nat_rules.get_by_id": mock_get_by_id,
            "vmc_nat_rules.update": mock_update,
        },
    ):
        result = vmc_nat_rules.present(
            name="test_present",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            nat_rule=mocked_ok_response["id"],
            display_name="rule-1"
        )

    assert result is not None
    assert result["changes"]["old"] == mocked_ok_response
    assert result["changes"]["new"] == mocked_updated_response
    assert result["comment"] == "Updated Nat rule nat_rule"
    assert result["result"]


def test_present_to_create_when_module_returns_success_response():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_by_id_response = MagicMock(return_value={})
    mock_create_response = MagicMock(return_value=mocked_ok_response)
    nat_rule = mocked_ok_response["id"]

    with patch.dict(
        vmc_nat_rules.__salt__,
        {
            "vmc_nat_rules.get_by_id": mock_get_by_id_response,
            "vmc_nat_rules.create": mock_create_response,
        },
    ):
        result = vmc_nat_rules.present(
            name="test_present",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            nat_rule=nat_rule
        )

    assert result is not None
    assert result["changes"]["new"] == mocked_ok_response
    assert result["changes"]["old"] is None
    assert result["comment"] == "Created Nat rule {}".format(nat_rule)
    assert result["result"]


def test_present_to_update_when_module_returns_success_response():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()
    mocked_updated_nat_rule = mocked_ok_response.copy()
    mocked_updated_nat_rule["display_name"] = "rule-1"

    mock_get_by_id_response = MagicMock(side_effect=[mocked_ok_response, mocked_updated_nat_rule])
    mock_update_response = MagicMock(return_value=mocked_updated_nat_rule)
    nat_rule = mocked_ok_response["id"]

    with patch.dict(
        vmc_nat_rules.__salt__,
        {
            "vmc_nat_rules.get_by_id": mock_get_by_id_response,
            "vmc_nat_rules.update": mock_update_response,
        },
    ):
        result = vmc_nat_rules.present(
            name="test_present",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            nat_rule=nat_rule,
            display_name="rule-1"
        )

    assert result is not None
    assert result["changes"]["new"] == mocked_updated_nat_rule
    assert result["changes"]["old"] == mocked_ok_response
    assert result["comment"] == "Updated Nat rule {}".format(nat_rule)
    assert result["result"]


def test_present_to_update_when_get_by_id_after_update_returns_error():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()
    mocked_updated_nat_rule = mocked_ok_response.copy()
    mocked_updated_nat_rule["display_name"] = "rule-1"

    mock_get_by_id_response = MagicMock(side_effect=[mocked_ok_response, mocked_error_response])
    mock_update_response = MagicMock(return_value=mocked_updated_nat_rule)
    nat_rule = mocked_ok_response["id"]

    with patch.dict(
        vmc_nat_rules.__salt__,
        {
            "vmc_nat_rules.get_by_id": mock_get_by_id_response,
            "vmc_nat_rules.update": mock_update_response,
        },
    ):
        result = vmc_nat_rules.present(
            name="test_present",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            nat_rule=nat_rule,
            display_name="rule-1"
        )

    assert result is not None
    assert result["changes"] == {}
    assert result["comment"] == "The credentials were incorrect or the account specified has been locked."
    assert not result["result"]


def test_present_to_update_when_user_input_and_existing_nat_rule_has_identical_fields():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_by_id_response = MagicMock(return_value=mocked_ok_response)

    with patch.dict(
        vmc_nat_rules.__salt__,
        {"vmc_nat_rules.get_by_id": mock_get_by_id_response},
    ):
        result = vmc_nat_rules.present(
            name="test_present",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            nat_rule=mocked_ok_response["id"]
        )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "Nat rule exists already, no action to perform"
    assert result["result"]


def test_present_state_for_create_when_opts_test_is_true():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_by_id_response = MagicMock(return_value={})
    nat_rule = mocked_ok_response["id"]

    with patch.dict(
        vmc_nat_rules.__salt__,
        {"vmc_nat_rules.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_nat_rules.__opts__, {"test": True}):
            result = vmc_nat_rules.present(
                name="test_present",
                hostname=mocked_hostname,
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                tier1="tier1",
                nat="nat",
                nat_rule=nat_rule
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "State present will create Nat rule {}".format(nat_rule)
    assert result["result"] is None


def test_present_state_for_update_when_opts_test_is_true():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_by_id_response = MagicMock(return_value=mocked_ok_response)
    nat_rule = mocked_ok_response["id"]

    with patch.dict(
        vmc_nat_rules.__salt__,
        {"vmc_nat_rules.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_nat_rules.__opts__, {"test": True}):
            result = vmc_nat_rules.present(
                name="test_present",
                hostname=mocked_hostname,
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                tier1="tier1",
                nat="nat",
                nat_rule=nat_rule
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "State present will update Nat rule {}".format(nat_rule)
    assert result["result"] is None


def test_absent_state_to_delete_when_module_returns_success_response():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_by_id_response = MagicMock(return_value=mocked_ok_response)
    mock_delete_response = MagicMock(ok=True, return_value="Nat rule Deleted Successfully")
    nat_rule = mocked_ok_response["id"]

    with patch.dict(
        vmc_nat_rules.__salt__,
        {
            "vmc_nat_rules.get_by_id": mock_get_by_id_response,
            "vmc_nat_rules.delete": mock_delete_response,
        },
    ):
        result = vmc_nat_rules.absent(
            name="test_absent",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            nat_rule=nat_rule
        )

    assert result is not None
    assert result["changes"] == {"new": None, "old": mocked_ok_response}
    assert result["comment"] == "Deleted Nat rule {}".format(nat_rule)
    assert result["result"]


def test_absent_state_when_object_to_delete_does_not_exists():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_by_id_response = MagicMock(return_value={})
    nat_rule = mocked_ok_response["id"]

    with patch.dict(
        vmc_nat_rules.__salt__,
        {"vmc_nat_rules.get_by_id": mock_get_by_id_response},
    ):
        result = vmc_nat_rules.absent(
            name="test_absent",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            nat_rule=nat_rule
        )

    assert result is not None
    assert result["changes"] == {}
    assert result["comment"] == "No Nat rule found with Id {}".format(nat_rule)
    assert result["result"]


def test_absent_state_to_delete_when_opts_test_mode_is_true():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_by_id_response = MagicMock(return_value={"results": [mocked_ok_response]})
    nat_rule = mocked_ok_response["id"]

    with patch.dict(
        vmc_nat_rules.__salt__,
        {"vmc_nat_rules.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_nat_rules.__opts__, {"test": True}):
            result = vmc_nat_rules.absent(
                name="test_absent",
                hostname=mocked_hostname,
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                tier1="tier1",
                nat="nat",
                nat_rule=nat_rule
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "State absent will delete Nat rule with Id {}".format(nat_rule)
    assert result["result"] is None


def test_absent_state_when_object_to_delete_doesn_not_exists_and_opts_test_mode_is_true():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_by_id_response = MagicMock(return_value={})
    nat_rule = mocked_ok_response["id"]

    with patch.dict(
        vmc_nat_rules.__salt__,
        {"vmc_nat_rules.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_nat_rules.__opts__, {"test": True}):
            result = vmc_nat_rules.absent(
                name="test_absent",
                hostname=mocked_hostname,
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                tier1="tier1",
                nat="nat",
                nat_rule=nat_rule
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "State absent will do nothing as no Nat rule found with Id {}".format(nat_rule)
    assert result["result"] is None


def test_absent_with_error_from_delete():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()

    mock_get_by_id = MagicMock(return_value={"results": [mocked_ok_response]})
    mock_delete = MagicMock(return_value=mocked_error_response)

    with patch.dict(
        vmc_nat_rules.__salt__,
        {
            "vmc_nat_rules.get_by_id": mock_get_by_id,
            "vmc_nat_rules.delete": mock_delete,
        },
    ):
        result = vmc_nat_rules.absent(
            name="test_absent",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            nat_rule="nat_rule"
        )

    assert result is not None
    assert result["changes"] == {}
    assert result["comment"] == "The credentials were incorrect or the account specified has been locked."
    assert not result["result"]


def test_absent_state_when_error_from_get_by_id():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()
    mock_get_by_id = MagicMock(return_value=mocked_error_response)

    with patch.dict(
        vmc_nat_rules.__salt__, {"vmc_nat_rules.get_by_id": mock_get_by_id}
    ):
        result = vmc_nat_rules.absent(
            name="test_absent",
            hostname=mocked_hostname,
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            nat_rule=mocked_ok_response["id"]
        )

    assert result is not None
    assert result["changes"] == {}
    assert result["comment"] == "The credentials were incorrect or the account specified has been locked."
    assert not result["result"]

