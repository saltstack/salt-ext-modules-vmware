# SPDX-License-Identifier: Apache-2.0
import logging

from saltext.vmware.utils.connect import get_config

# pylint: disable=no-name-in-module
try:
    from config_modules_vmware.lib.common.credentials import SddcCredentials
    from config_modules_vmware.lib.common.credentials import VcenterCredentials
    from config_modules_vmware.vcenter.vc_context import VcenterContext
    from config_modules_vmware.control_module.control_config import ControlConfig

    HAS_CONFIG_MODULE = True
except ImportError:
    HAS_CONFIG_MODULE = False

log = logging.getLogger(__name__)


def _get_vc_credential(config, profile=None):
    conf = get_config(config, profile)
    return VcenterCredentials(
        hostname=conf["host"],
        username=conf["user"],
        password=conf["password"],
        ssl_thumbprint=conf["ssl_thumbprint"],
    )


def create_vc_context(config, profile=None):
    return VcenterContext(SddcCredentials(vc_creds=_get_vc_credential(config, profile)))


def create_vc_config(config, profile=None, vc_context=None):
    if vc_context:
        return ControlConfig(vc_context)
    return ControlConfig(create_vc_context(config, profile))
