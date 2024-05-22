# SPDX-License-Identifier: Apache-2.0
import logging

import salt.exceptions

# pylint: disable=no-name-in-module
try:

    from config_modules_vmware.interfaces.controller_interface import ControllerInterface
    from config_modules_vmware.framework.auth.contexts.vc_context import VcenterContext
    from config_modules_vmware.framework.auth.contexts.sddc_manager_context import (
        SDDCManagerContext,
    )
    from config_modules_vmware.framework.auth.contexts.base_context import BaseContext
    from config_modules_vmware.framework.auth.contexts.esxi_context import EsxiContext
    from config_modules_vmware.framework.auth.contexts.vrslcm_context import VrslcmContext

    HAS_CONFIG_MODULE = True
except ImportError:
    HAS_CONFIG_MODULE = False

log = logging.getLogger(__name__)


def _create_vcenter_context(conf, fqdn):
    return VcenterContext(
        hostname=fqdn,
        username=conf["user"],
        password=conf["password"],
        ssl_thumbprint=conf.get("ssl_thumbprint", None),
        verify_ssl=conf.get("verify_ssl", True)
    )


def _create_sddc_manager_context(conf, fqdn):
    return SDDCManagerContext(
        hostname=fqdn,
        username=conf["user"],
        password=conf["password"],
        ssl_thumbprint=conf.get("ssl_thumbprint", None),
        verify_ssl=conf.get("verify_ssl", True)
    )


def _create_esxi_context(vcenter_conf, fqdn=None, ids=None):
    return EsxiContext(
        vc_hostname=fqdn,
        vc_username=vcenter_conf["user"],
        vc_password=vcenter_conf["password"],
        vc_ssl_thumbprint=vcenter_conf.get("ssl_thumbprint", None),
        vc_saml_token=vcenter_conf.get("saml_token", None),
        esxi_host_names=ids,
    )


def _get_parent(product):
    if product == BaseContext.ProductEnum.ESXI.value:
        return BaseContext.ProductEnum.VCENTER.value
    else:
        return None


def _create_product_context(config, product, ids=None):
    parent_product = _get_parent(product)
    if parent_product:
        conf = (
            config.get("saltext.vmware")
            or config.get("grains", {}).get("saltext.vmware")
            or config.get("pillar", {}).get("saltext.vmware")
            or config.get(parent_product)
            or config.get("pillar", {}).get(parent_product)
            or config.get("grains", {}).get(parent_product)
            or {}
        )
    else:
        conf = (
            config.get("saltext.vmware")
            or config.get("grains", {}).get("saltext.vmware")
            or config.get("pillar", {}).get("saltext.vmware")
            or config.get(product)
            or config.get("pillar", {}).get(product)
            or config.get("grains", {}).get(product)
            or {}
        )
    fqdn = config.get("grains", {}).get("fqdn")
    if not fqdn:
        fqdn = conf.get("host")
    if product == BaseContext.ProductEnum.VCENTER.value:
        return _create_vcenter_context(conf, fqdn)
    elif product == BaseContext.ProductEnum.SDDC_MANAGER.value:
        return _create_sddc_manager_context(conf, fqdn)
    elif product == BaseContext.ProductEnum.NSXT_MANAGER.value:
        return BaseContext(BaseContext.ProductEnum.NSXT_MANAGER)
    elif product == BaseContext.ProductEnum.NSXT_EDGE.value:
        return BaseContext(BaseContext.ProductEnum.NSXT_EDGE)
    elif product == BaseContext.ProductEnum.ESXI.value:
        return _create_esxi_context(vcenter_conf=conf, fqdn=fqdn, ids=ids)
    elif product == BaseContext.ProductEnum.VRSLCM.value:
        return VrslcmContext(fqdn)
    else:
        raise salt.exceptions.VMwareApiError({f"Unsupported product {product}"})


def create_auth_context(config, product, ids=None):
    return _create_product_context(config=config, product=product, ids=ids)
