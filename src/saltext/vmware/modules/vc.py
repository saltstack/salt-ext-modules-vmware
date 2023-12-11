# SPDX-License: Apache-2.0
import logging

import salt.exceptions
import saltext.vmware.utils.vc as utils_vc

log = logging.getLogger(__name__)

try:
    from config_modules_vmware.vcenter.vcenter_config import VcenterConfig

    HAS_CONFIG_MODULE = True
except ImportError:
    HAS_CONFIG_MODULE = False

__virtualname__ = "vmware_vc"


def __virtual__():
    if not HAS_CONFIG_MODULE:
        return False, "Unable to import unified config module."
    return __virtualname__


def control_config_compliance_check(control_config, vc_config=None, profile=None):
    """
    Checks compliance of vcenter control config. Control config can be ntp, dns, syslog, etc.
    Returns control compliance response object.

    control_config
        vc control config dict object.

    vc_config
        Optional vc_config object with vc connection.

    profile
        Optional auth profile to be used for vc connection.
    """

    log.info("Checking complaince %s", control_config)
    if not vc_config:
        config = __opts__
        vc_config = utils_vc.create_vc_config(config, profile)

    try:
        response_check_compliance = vc_config.check_compliance(desired_state_spec=control_config)
        log.debug("control_config_compliance_check response %s", response_check_compliance)
        return response_check_compliance
    except Exception as exc:
        log.error("control_config_compliance_check encountered an error: %s", str(exc))
        raise salt.exceptions.VMwareRuntimeError(str(exc))


def control_config_remediate(control_config, vc_config=None, profile=None):
    """
    Remediate given compliance control config. Control config can be ntp, dns, syslog, etc.
    Returns remediation response object.

    control_config
        vc control config dict object.

    vc_config
        Optional vc_config object with vc connection.

    profile
        Optional auth profile to be used for vc connection.
    """

    log.info("control_config_remediate: %s", control_config)

    if not vc_config:
        config = __opts__
        vc_config = utils_vc.create_vc_config(config, profile)

    try:
        response_remediate = vc_config.remediate_with_desired_state(
            desired_state_spec=control_config
        )
        log.debug("control_config_remediate response %s", response_remediate)
        return response_remediate

    except Exception as exc:
        # Handle exceptions by setting status as false and including exception details
        log.error("control_config_remediate encountered an error: %s", str(exc))
        raise salt.exceptions.VMwareRuntimeError(str(exc))
