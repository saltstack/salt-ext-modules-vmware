"""
    Unit tests for vmc_dns_forwarder execution module
"""

from __future__ import absolute_import
import saltext.vmware.modules.vmc_dns_forwarder as vmc_dns_forwarder
from saltext.vmware.utils import vmc_request
from unittest.mock import patch


_get_dns_forwarder_zone_data = {
    "results": [
        {
            "dns_domain_names": [],
            "upstream_servers": [
                "8.8.8.8",
                "8.8.4.4"
            ],
            "resource_type": "PolicyDnsForwarderZone",
            "id": "cgw-dns-zone",
            "display_name": "Compute Gateway Default Zone",
            "path": "/infra/dns-forwarder-zones/cgw-dns-zone",
            "relative_path": "cgw-dns-zone",
            "parent_path": "/infra",
            "unique_id": "82eff471-4e63-4b39-9afb-7265848c5f32",
            "marked_for_delete": False,
            "overridden": False,
            "_create_time": 1619461631122,
            "_create_user": "admin",
            "_last_modified_time": 1619461631133,
            "_last_modified_user": "admin",
            "_system_owned": False,
            "_protection": "NOT_PROTECTED",
            "_revision": 0
        }
    ],
    "result_count": 1,
    "sort_by": "display_name",
    "sort_ascending": True
}


_get_dns_forwarder_services_data = {
    "results": [
        {
            "listener_ip": "10.2.192.12",
            "unique_id": "51b93311-79c2-4158-9b20-eb9fc601848f",
            "_last_modified_user": "admin",
            "_revision": 0,
            "_system_owned": False,
            "log_level": "INFO",
            "resource_type": "PolicyDnsForwarder",
            "_protection": "NOT_PROTECTED",
            "_last_modified_time": 1619461631411,
            "overridden": False,
            "display_name": "Compute Gateway DNS Forwarder",
            "enabled": True,
            "_create_user": "admin",
            "default_forwarder_zone_path": "/infra/dns-forwarder-zones/cgw-dns-zone",
            "_create_time": 1619461631405,
            "path": "/infra/tier-1s/cgw/dns-forwarder",
            "marked_for_delete": False,
            "parent_path": "/infra/tier-1s/cgw",
            "id": "dns-forwarder",
            "relative_path": "dns-forwarder",
            "status": {
                "consolidated_status_per_enforcement_point": [
                    {
                        "consolidated_status": {
                            "consolidated_status": "SUCCESS"
                        },
                        "resource_type": "ConsolidatedStatusPerEnforcementPoint",
                        "enforcement_point_id": "vmc-enforcementpoint"
                    }
                ],
                "intent_version": "0",
                "consolidated_status": {
                    "consolidated_status": "SUCCESS"
                },
                "intent_path": "/infra/tier-1s/cgw/dns-forwarder",
                "publish_status": "REALIZED"
            }
        }
    ],
    "result_count": 1,
    "cursor": "1"
}


@patch.object(vmc_request, 'call_api')
def test_get_dns_zones_should_return_api_response(mock_call_api):
    mock_call_api.return_value = _get_dns_forwarder_zone_data
    assert vmc_dns_forwarder.get_dns_zones(hostname="hostname",
                                           refresh_key="refresh_key",
                                           authorization_host="authorization_host",
                                           org_id="org_id",
                                           sddc_id="sddc_id",
                                           verify_ssl=False) == _get_dns_forwarder_zone_data


@patch.object(vmc_request, 'call_api')
def test_get_dns_services_should_return_api_response(mock_call_api):
    mock_call_api.return_value = _get_dns_forwarder_services_data
    assert vmc_dns_forwarder.get_dns_services(hostname="hostname",
                                              refresh_key="refresh_key",
                                              authorization_host="authorization_host",
                                              org_id="org_id",
                                              sddc_id="sddc_id",
                                              verify_ssl=False) == _get_dns_forwarder_services_data
