# SPDX-License: Apache-2.0
import logging

import salt.exceptions
import saltext.vmware.utils.compliance_control as compliance_control_util
from config_modules_vmware.control_module.control_config import ControlConfig

log = logging.getLogger(__name__)

__virtualname__ = "vmware_compliance_control"


def __virtual__():
    return __virtualname__


def control_config_compliance_check(control_config, product, auth_context=None):
    """
    Checks compliance of vcenter control config. Control config can be ntp, dns, syslog, etc.
    Returns control compliance response object.

    control_config
        vc control config dict object.
    product
        appliance name. vcenter, nsx, etc.
    auth_context
        Optional auth context to access product.
    """

    log.info("Checking complaince %s", control_config)
    if not auth_context:
        config = __opts__
        auth_context = compliance_control_util.create_auth_context(config=config, product=product)

    try:
        control_config_obj = ControlConfig(auth_context)
        response_check_compliance = control_config_obj.check_compliance(
            desired_state_spec=control_config
        )
        log.debug("control_config_compliance_check response %s", response_check_compliance)
        return response_check_compliance
    except Exception as exc:
        log.error("control_config_compliance_check encountered an error: %s", str(exc))
        raise salt.exceptions.VMwareRuntimeError(str(exc))


def control_config_remediate(control_config, product, auth_context=None):
    """
    Remediate given compliance control config. Control config can be ntp, dns, syslog, etc.
    Returns remediation response object.

    control_config
        vc control config dict object.
    product
        appliance name. vcenter, nsx, etc.
    auth_context
        Optional auth context to access product.
    """

    log.info("control_config_remediate: %s", control_config)

    if not auth_context:
        config = __opts__
        auth_context = compliance_control_util.create_auth_context(config=config, product=product)

    try:
        control_config_obj = ControlConfig(auth_context)
        response_remediate = control_config_obj.remediate_with_desired_state(
            desired_state_spec=control_config
        )
        log.debug("control_config_remediate response %s", response_remediate)
        return response_remediate

    except Exception as exc:
        # Handle exceptions by setting status as false and including exception details
        log.error("control_config_remediate encountered an error: %s", str(exc))
        raise salt.exceptions.VMwareRuntimeError(str(exc))
