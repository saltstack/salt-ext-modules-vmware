"""
Unit Tests for compliance control utils.
"""

import pytest
import salt.exceptions
from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
from saltext.vmware.utils import compliance_control


def vcenter_pillar():
    return {
        "vcenter": {
            "host": "test.vcenter.local",
            "user": "vcenter-user",
            "password": "vcenter-password",
            "ssl_thumbprint": "vcenter-thumbprint",
        }
    }


def sddc_manager_pillar():
    return {
        "sddc_manager": {
            "host": "test.sddc-mgr.local",
            "user": "sddc-user",
            "password": "sddc-password",
            "verify_ssl": False,
        }
    }


@pytest.mark.parametrize(
    "product_type, mock_product_pillar",
    [
        ("vcenter", vcenter_pillar()),
        ("sddc_manager", sddc_manager_pillar()),
        ("esxi", vcenter_pillar()),
    ],
)
def test_create_auth_context(product_type, mock_product_pillar):
    result = compliance_control.create_auth_context(
        config=mock_product_pillar, product=product_type, ids=None
    )

    assert result is not None
    assert result._product_category == BaseContext.ProductEnum(product_type)
    if product_type == "esxi":
        product_type = "vcenter"
    assert result._hostname == mock_product_pillar.get(product_type).get("host")
    assert result._username == mock_product_pillar.get(product_type).get("user")
    assert result._password == mock_product_pillar.get(product_type).get("password")
    assert result._ssl_thumbprint == mock_product_pillar.get(product_type).get("ssl_thumbprint")
    assert result._verify_ssl == mock_product_pillar.get(product_type).get("verify_ssl", True)


@pytest.mark.parametrize(
    "product_type, mock_product_pillar",
    [
        ("nsxt_manager", {"nsxt_manager": {}}),
        ("nsxt_edge", {"nsxt_edge": {}}),
        ("vrslcm", {"vrslcm": {"grains": {"fqdn": "test.vrslcm.local"}}}),
    ],
)
def test_create_base_auth_context(product_type, mock_product_pillar):
    result = compliance_control.create_auth_context(
        config=mock_product_pillar, product=product_type, ids=None
    )

    assert result is not None
    assert result._hostname == mock_product_pillar.get(product_type).get("host")
    assert result._product_category == BaseContext.ProductEnum(product_type)


def test_unsupported_product_auth_context():
    with pytest.raises(salt.exceptions.VMwareApiError):
        compliance_control.create_auth_context(
            config={"saltext.vmware": {}}, product="unsupported_product", ids=None
        )
