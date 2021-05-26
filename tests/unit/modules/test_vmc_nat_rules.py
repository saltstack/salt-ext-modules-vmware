"""
    Unit tests for vmc_nat_rules execution module
"""

# Import Python Libs
from __future__ import absolute_import, print_function, unicode_literals

from requests import Session

import saltext.vmware.modules.vmc_nat_rules as vmc_nat_rules
from saltext.vmware.utils import vmc_request
from unittest.mock import patch


_get_nat_rules_data = {
        'result_count': 1,
        'results': [ {'sequence_number': 0, 'action': 'REFLEXIVE', 'source_network': '192.168.1.1',
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
                      '_protection': 'NOT_PROTECTED', '_revision': 0}],
        'sort_by': 'display_name',
        'sort_ascending': True
    }

_get_nat_rule_data_by_id = {
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


@patch.object(vmc_request, 'call_api')
def test_get_nat_rules_should_return_api_response(mock_call_api):
    mock_call_api.return_value = _get_nat_rules_data
    assert vmc_nat_rules.get(hostname="hostname",
                                  refresh_key="refresh_key",
                                  authorization_host="authorization_host",
                                  org_id="org_id",
                                  sddc_id="sddc_id",
                                  tier1="tier1",
                                  nat="nat",
                                  verify_ssl=False) == _get_nat_rules_data


@patch.object(vmc_request, 'call_api')
def test_get_nat_rule_by_id_should_return_single_nat_rule(mock_call_api):
    mock_call_api.return_value = _get_nat_rule_data_by_id
    result = vmc_nat_rules.get_by_id(hostname="hostname",
                                          refresh_key="refresh_key",
                                          authorization_host="authorization_host",
                                          org_id="org_id", sddc_id="sddc_id",
                                          tier1="tier1",
                                          nat="nat",
                                          nat_rule="nat_rule",
                                          verify_ssl=False)
    assert result == _get_nat_rule_data_by_id


@patch.object(vmc_request, 'call_api')
def test_create_nat_rule_when_api_should_return_successfully_created_message(mock_call_api):
    expected_response = {'message': 'Nat rule created successfully'}
    mock_call_api.return_value = expected_response

    assert vmc_nat_rules.create(hostname="hostname",
                                     refresh_key="refresh_key",
                                     authorization_host="authorization_host",
                                     org_id="org_id",
                                     sddc_id="sddc_id",
                                     tier1="tier1",
                                     nat="nat",
                                     nat_rule="nat_rule",
                                     verify_ssl=False) == expected_response


@patch.object(vmc_request, 'call_api')
def test_delete_nat_rule_when_api_should_return_successfully_deleted_message(mock_call_api):
    expected_response = {'message': 'Nat rule deleted successfully'}
    mock_call_api.return_value = expected_response
    assert vmc_nat_rules.delete(hostname="hostname",
                                     refresh_key="refresh_key",
                                     authorization_host="authorization_host",
                                     org_id="org_id", sddc_id="sddc_id",
                                     tier1="tier1",
                                     nat="nat",
                                     nat_rule="nat_rule",
                                     verify_ssl=False) == expected_response


@patch.object(vmc_request, 'call_api')
def test_update_nat_rule_when_api_should_return_successfully_updated_message(mock_call_api):
    expected_response = {'message': 'Nat rule updated successfully'}
    mock_call_api.return_value = expected_response
    assert vmc_nat_rules.update(hostname="hostname",
                                     refresh_key="refresh_key",
                                     authorization_host="authorization_host",
                                     org_id="org_id", sddc_id="sddc_id",
                                     tier1="tier1",
                                     nat="nat",
                                     nat_rule="nat_rule",
                                     verify_ssl=False) == expected_response


@patch.object(vmc_request, 'call_api')
def test_update_nat_rule_when_api_returns_no_nat_rule_with_given_id(mock_call_api):
    expected_response = {'error': 'Given Nat rule does not exist'}
    mock_call_api.return_value = expected_response
    assert vmc_nat_rules.update(hostname="hostname",
                                     refresh_key="refresh_key",
                                     authorization_host="authorization_host",
                                     org_id="org_id", sddc_id="sddc_id",
                                     tier1="tier1",
                                     nat="nat",
                                     nat_rule="nat_rule",
                                     verify_ssl=False) == expected_response
