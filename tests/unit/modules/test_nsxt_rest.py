"""
    Tests for nsxt_rest module
"""
import logging
from unittest.mock import patch

from saltext.vmware.modules import nsxt_rest
from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)


@patch.object(nsxt_request, "call_api")
def test_call_post_api_should_return_response(mock_call_api):
    response = {"results": {"key": "value"}}
    mock_call_api.return_value = response

    assert (
        nsxt_rest.call_api(
            url="https://nsxt-vmware.local/api/to/call",
            method="post",
            username="user",
            password="pass",
            data={},
            verify_ssl=False,
        )
        == response
    )


@patch.object(nsxt_request, "call_api")
def test_call_delete_api_with_return_none(mock_call_api):
    mock_call_api.return_value = None
    method = "delete"

    assert (
        nsxt_rest.call_api(
            url="https://nsxt-vmware.local/api/to/call",
            method=method,
            username="user",
            password="pass",
            verify_ssl=False,
        )
        == "{} call is success".format(method.upper())
    )
