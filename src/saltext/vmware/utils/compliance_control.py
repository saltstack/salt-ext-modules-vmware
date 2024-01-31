# SPDX-License-Identifier: Apache-2.0
import logging

import salt.exceptions

# pylint: disable=no-name-in-module
try:
    from config_modules_vmware.control_module.control_config import ControlConfig
    from config_modules_vmware.control_module.auth.vc_context import VcenterContext
    from config_modules_vmware.control_module.auth.sddc_manager_context import SDDCManagerContext
    from config_modules_vmware.control_module.auth.base_context import BaseContext

    HAS_CONFIG_MODULE = True
except ImportError:
    HAS_CONFIG_MODULE = False

log = logging.getLogger(__name__)


def _create_product_context(config, product):
    conf = (
        config.get("saltext.vmware")
        or config.get("grains", {}).get("saltext.vmware")
        or config.get("pillar", {}).get("saltext.vmware")
        or {}
    )
    if not conf:
        conf = (
            config.get(product)
            or config.get("pillar", {}).get(product)
            or config.get("grains", {}).get(product)
            or {}
        )
    if product == BaseContext.ProductEnum.VCENTER.value:
        return VcenterContext(
            hostname=conf["host"],
            username=conf["user"],
            password=conf["password"],
            ssl_thumbprint=conf.get("ssl_thumbprint", None),
        )
    elif product == BaseContext.ProductEnum.SDDC_MANAGER.value:
        return SDDCManagerContext(
            hostname=conf["host"],
            username=conf["user"],
            password=conf["password"],
            ssl_thumbprint=conf.get("ssl_thumbprint", None),
        )
    elif product == BaseContext.ProductEnum.NSX.value:
        return BaseContext(BaseContext.ProductEnum.NSX)
    else:
        raise salt.exceptions.VMwareApiError({f"Unsupported product {product}"})


def create_auth_context(config, product):
    return _create_product_context(config=config, product=product)
