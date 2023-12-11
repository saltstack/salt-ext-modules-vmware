# SPDX-License-Identifier: Apache-2.0
import json
import logging

import saltext.vmware.utils.vc as utils_vc

log = logging.getLogger(__name__)

try:
    from config_modules_vmware.vcenter.vc_config import VcenterConfig

    HAS_CONFIG_MODULE = True
except ImportError:
    HAS_CONFIG_MODULE = False

__virtualname__ = "vmware_vc"
__proxyenabled__ = ["vmware_vc"]


def __virtual__():
    if not HAS_CONFIG_MODULE:
        return False, "Unable to import unified config module."
    return __virtualname__


def check_control(name, control_config, profile=None):
    """
    Check and apply vcenter control configs. Control config can be ntp, dns, syslog, etc.
    Return control compliance response if test=true. Otherwise, return remediate response.

    name
        Config name

    control_config
        vc control config dict object.

    profile
        Optional auth profile to be used for vc connection.
    """

    ret = {"name": name, "result": None, "changes": {}, "comment": None}

    log.info("starting compliance check for %s", name)

    # Create ESXi configuration
    config = __opts__
    vc_config = utils_vc.create_vc_config(config, profile)

    control_config = json.loads(json.dumps(control_config))
    log.debug("Opts: %s", __opts__)

    try:
        if __opts__["test"]:
            # If in test mode, perform audit
            log.info("Running in test mode. Performing check_control_compliance_response.")
            check_control_compliance_response = __salt__[
                "vmware_vc.control_config_compliance_check"
            ](
                control_config=control_config,
                vc_config=vc_config,
            )

            if check_control_compliance_response["status"] == "COMPLIANT":
                log.debug("Pre-check completed successfully. You can continue with remediation.")
                # Update return data
                ret = {"name": name, "result": True, "comment": "COMPLIANT", "changes": {}}
            else:
                # Pre-check failed in test mode
                ret = {
                    "name": name,
                    "result": False,
                    "comment": "NON_COMPLIANT",
                    "changes": check_control_compliance_response.get(
                        "changes", "No details available"
                    ),
                }
        else:
            # Not in test mode, proceed with pre-check and remediation
            log.debug("Performing remediation.")
            # Execute remediation
            remediate_response = __salt__["vmware_vc.control_config_remediate"](
                control_config=control_config,
                vc_config=vc_config,
            )

            if remediate_response["status"] == "SUCCESS":
                log.debug("Remediation completed successfully.")
                # Update return data for successful remediation
                ret = {
                    "name": name,
                    "result": True,
                    "comment": "Configuration remediated successfully",
                    "changes": {
                        "remediate": remediate_response.get("changes", "Nothing to remediate"),
                    },
                }
            else:
                # Remediation failed
                ret = {
                    "name": name,
                    "result": False,
                    "comment": "Remediation failed.",
                    "changes": {
                        "remediate": remediate_response.get("changes", "No details available"),
                    },
                }

    except Exception as e:
        # Exception occurred during remediation
        log.error("An error occurred during remediation: %s", str(e))
        ret = {
            "name": name,
            "result": False,
            "comment": f"An error occurred during remediation: {str(e)}",
        }

    log.debug("Completed remediation for %s", name)
    return ret
