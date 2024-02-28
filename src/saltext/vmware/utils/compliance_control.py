# SPDX-License-Identifier: Apache-2.0
import logging

import salt.exceptions

# pylint: disable=no-name-in-module
try:
    from config_modules_vmware.control_module.control_config import ControlConfig
    from config_modules_vmware.control_module.auth.vc_context import VcenterContext
    from config_modules_vmware.control_module.auth.sddc_manager_context import SDDCManagerContext
    from config_modules_vmware.control_module.auth.base_context import BaseContext
    from config_modules_vmware.control_module.auth.esxi_context import EsxiContext
    from config_modules_vmware.control_module.auth.vrslcm_context import VrslcmContext

    HAS_CONFIG_MODULE = True
except ImportError:
    HAS_CONFIG_MODULE = False

log = logging.getLogger(__name__)


def _create_vcenter_context(conf):
    return VcenterContext(
        hostname=conf["host"],
        username=conf["user"],
        password=conf["password"],
        ssl_thumbprint=conf.get("ssl_thumbprint", None),
    )


def _create_sddc_manager_context(conf):
    return SDDCManagerContext(
        hostname=conf["host"],
        username=conf["user"],
        password=conf["password"],
        ssl_thumbprint=conf.get("ssl_thumbprint", None),
    )


def _create_esxi_context(vcenter_conf, ids=None):
    return EsxiContext(
        vc_hostname=vcenter_conf["host"],
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

    if product == BaseContext.ProductEnum.VCENTER.value:
        return _create_vcenter_context(conf)
    elif product == BaseContext.ProductEnum.SDDC_MANAGER.value:
        return _create_sddc_manager_context(conf)
    elif product == BaseContext.ProductEnum.NSXT_MANAGER.value:
        return BaseContext(BaseContext.ProductEnum.NSXT_MANAGER)
    elif product == BaseContext.ProductEnum.NSXT_EDGE.value:
        return BaseContext(BaseContext.ProductEnum.NSXT_EDGE)
    elif product == BaseContext.ProductEnum.ESXI.value:
        return _create_esxi_context(vcenter_conf=conf, ids=ids)
    elif product == BaseContext.ProductEnum.VRSLCM.value:
        return VrslcmContext(conf["host"])
    else:
        raise salt.exceptions.VMwareApiError({f"Unsupported product {product}"})


def create_auth_context(config, product, ids=None):
    return _create_product_context(config=config, product=product, ids=ids)
