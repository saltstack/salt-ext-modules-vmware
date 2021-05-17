"""
    :codeauthor: VMware
"""
from unittest.mock import patch

from saltext.vmware.modules import nsxt_license
from saltext.vmware.utils import nsxt_request

_mock_response = {
    "result_count": 1,
    "results": [
        {
            "capacity_type": "CPU",
            "description": "NSX Data Center Enterprise Plus",
            "expiry": "1714435200000",
            "is_eval": False,
            "is_expired": False,
            "license_key": "ABCD-EFGH-IJKL-MNOP",
            "quantity": 16,
        }
    ],
}


@patch.object(nsxt_request, "call_api")
def test_get_licenses_should_return_response(mock_call_api):

    mock_call_api.return_value = _mock_response

    assert (
        nsxt_license.get_licenses(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
        )
        == _mock_response
    )


@patch.object(nsxt_request, "call_api")
def test_apply_license_should_return_response(mock_call_api):

    mock_call_api.return_value = _mock_response

    assert (
        nsxt_license.apply_license(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
            license_key="ABCD-EFGH-IJKL-MNOP",
        )
        == _mock_response
    )


@patch.object(nsxt_request, "call_api")
def test_delete_license_should_return_response(mock_call_api):

    mock_call_api.return_value = _mock_response

    assert (
        nsxt_license.delete_license(
            hostname="nsx-t.vmware.com",
            username="username",
            password="password",
            verify_ssl=False,
            license_key="ABCD-EFGH-IJKL-MNOP",
        )
        == _mock_response
    )
