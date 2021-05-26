"""
    Unit tests for vmc_security_rules execution module
"""

# Import Python Libs
from __future__ import absolute_import, print_function, unicode_literals


import saltext.vmware.modules.vmc_security_rules as vmc_security_rules
from saltext.vmware.utils import vmc_request
from unittest.mock import patch


_get_security_rules_data = {
        'result_count': 1,
        'results': [{'action': 'ALLOW', 'resource_type': 'Rule', 'display_name': 'vCenter Inbound Rule',
                     'id': 'rule_id', 'is_default': False, '_system_owned': False, '_revision': 0,
                     '_protection': 'NOT_PROTECTED', '_create_user': 'abc@vmware.com',
                     '_create_time': 1616589005202, '_last_modified_user': 'abc@vmware.com',
                     '_last_modified_time': 1616589005206, 'ip_protocol': 'IPV4_IPV6',
                     'path': '/infra/domains/mgw/gateway-policies/default/rules/vCenter_Inbound_Rule',
                     'relative_path': 'vCenter_Inbound_Rule',
                     'parent_path': '/infra/domains/mgw/gateway-policies/default',
                     'unique_id': '1015', 'marked_for_delete': False, 'overridden': False,
                     'rule_id': 1015, 'sequence_number': 10, 'sources_excluded': False, 'destinations_excluded': False,
                     'source_groups': ['ANY'], 'destination_groups': ['/infra/domains/mgw/groups/VCENTER'],
                     'services': ['/infra/services/HTTPS'], 'profiles': ['ANY'], 'logged': False,
                     'scope': ['/infra/labels/mgw"'], 'disabled': False, 'notes': '',
                     'direction': 'IN_OUT', 'tag': ''}]
}

_get_security_rules_data_by_id = {
    'action': 'ALLOW', 'resource_type': 'Rule', 'display_name': 'vCenter Inbound Rule',
    'id': 'rule_id', 'is_default': False, '_system_owned': False, '_revision': 0,
    '_protection': 'NOT_PROTECTED', '_create_user': 'abc@vmware.com',
    '_create_time': 1616589005202, '_last_modified_user': 'abc@vmware.com',
    '_last_modified_time': 1616589005206, 'ip_protocol': 'IPV4_IPV6',
    'path': '/infra/domains/mgw/gateway-policies/default/rules/vCenter_Inbound_Rule',
    'relative_path': 'vCenter_Inbound_Rule',
    'parent_path': '/infra/domains/mgw/gateway-policies/default',
    'unique_id': '1015', 'marked_for_delete': False, 'overridden': False,
    'rule_id': 1015, 'sequence_number': 10, 'sources_excluded': False, 'destinations_excluded': False,
    'source_groups': ['ANY'], 'destination_groups': ['/infra/domains/mgw/groups/VCENTER'],
    'services': ['/infra/services/HTTPS'], 'profiles': ['ANY'], 'logged': False,
    'scope': ['/infra/labels/mgw"'], 'disabled': False, 'notes': '',
    'direction': 'IN_OUT', 'tag': ''
}


@patch.object(vmc_request, 'call_api')
def test_get_security_rules_should_return_api_response(mock_call_api):
    mock_call_api.return_value = _get_security_rules_data
    assert vmc_security_rules.get(hostname="hostname",
                                  refresh_key="refresh_key",
                                  authorization_host="authorization_host",
                                  org_id="org_id",
                                  sddc_id="sddc_id",
                                  domain_id="domain_id",
                                  verify_ssl=False) == _get_security_rules_data


@patch.object(vmc_request, 'call_api')
def test_get_security_rule_by_id_should_return_single_security_rule(mock_call_api):
    mock_call_api.return_value = _get_security_rules_data_by_id
    result = vmc_security_rules.get_by_id(hostname="hostname",
                                          refresh_key="refresh_key",
                                          authorization_host="authorization_host",
                                          org_id="org_id", sddc_id="sddc_id", domain_id="domain_id",
                                          rule_id="rule-id", verify_ssl=False)
    assert result == _get_security_rules_data_by_id


@patch.object(vmc_request, 'call_api')
def test_create_security_rule_when_api_should_return_successfully_created_message(mock_call_api):
    expected_response = {'message': 'Security rule created successfully'}
    mock_call_api.return_value = expected_response

    assert vmc_security_rules.create(hostname="hostname",
                                     refresh_key="refresh_key",
                                     authorization_host="authorization_host",
                                     org_id="org_id",
                                     sddc_id="sddc_id", domain_id="domain_id", rule_id="rule_id",
                                     verify_ssl=False) == expected_response


@patch.object(vmc_request, 'call_api')
def test_delete_security_rule_when_api_should_return_successfully_deleted_message(mock_call_api):
    expected_response = {'message': 'Security rule deleted successfully'}
    mock_call_api.return_value = expected_response
    assert vmc_security_rules.delete(hostname="hostname",
                                     refresh_key="refresh_key",
                                     authorization_host="authorization_host",
                                     org_id="org_id", sddc_id="sddc_id", domain_id="domain_id",
                                     rule_id="rule_id", verify_ssl=False) == expected_response


@patch.object(vmc_request, 'call_api')
def test_update_security_rule_when_api_should_return_successfully_updated_message(mock_call_api):
    expected_response = {'message': 'Security rule updated successfully'}
    mock_call_api.return_value = expected_response
    assert vmc_security_rules.update(hostname="hostname",
                                     refresh_key="refresh_key",
                                     authorization_host="authorization_host",
                                     org_id="org_id", sddc_id="sddc_id", domain_id="domain_id",
                                     rule_id="rule_id", verify_ssl=False) == expected_response


@patch.object(vmc_request, 'call_api')
def test_update_security_rule_when_api_returns_no_security_rule_with_given_id(mock_call_api):
    expected_response = {'error': 'Given Security rule does not exist'}
    mock_call_api.return_value = expected_response
    assert vmc_security_rules.update(hostname="hostname",
                                     refresh_key="refresh_key",
                                     authorization_host="authorization_host",
                                     org_id="org_id", sddc_id="sddc_id", domain_id="domain_id",
                                     rule_id="rule_id", verify_ssl=False) == expected_response
