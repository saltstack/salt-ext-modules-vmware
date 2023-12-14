# SPDX-License-Identifier: Apache-2.0
import json
import logging

import saltext.vmware.utils.vc as utils_vc

log = logging.getLogger(__name__)

__virtualname__ = "vmware_compliance_control"
__proxyenabled__ = ["vmware_compliance_control"]


def __virtual__():
    return __virtualname__


def check_control(name, control_config, product, profile=None):
    """
    Check and apply vcenter control configs. Control config can be ntp, dns, syslog, etc.
    Return control compliance response if test=true. Otherwise, return remediate response.

    name
        Config name
    control_config
        vc control config dict object.
    product
        appliance name. vcenter, nsx, etc.
    profile
        Optional auth profile to be used for vc connection.
    """

    ret = {"name": name, "result": None, "changes": {}, "comment": None}

    log.info("starting compliance check for %s", name)

    # Create ESXi configuration
    config = __opts__
    config_obj = utils_vc.create_control_config(config, profile)

    control_config = json.loads(json.dumps(control_config))
    log.debug("Opts: %s", __opts__)

    try:
        if __opts__["test"]:
            # If in test mode, perform audit
            log.info("Running in test mode. Performing check_control_compliance_response.")
            check_control_compliance_response = __salt__[
                "vmware_compliance_control.control_config_compliance_check"
            ](
                control_config=control_config,
                product=product,
                config_obj=config_obj,
            )

            if check_control_compliance_response["status"] == "COMPLIANT":
                log.debug("Pre-check completed successfully. You can continue with remediation.")
                # Update return data
                ret = {"name": name, "result": True, "comment": "COMPLIANT", "changes": {}}
            elif check_control_compliance_response["status"] == "NON_COMPLIANT":
                ret = {
                    "name": name,
                    "result": False,
                    "comment": "NON_COMPLIANT",
                    "changes": check_control_compliance_response.get(
                        "changes", "No details available"
                    ),
                }
            else:
                # Pre-check failed in test mode
                ret = {
                    "name": name,
                    "result": False,
                    "comment": "Failed to run compliance check. Please check changes for more details.",
                    "changes": check_control_compliance_response.get(
                        "changes", "No details available"
                    ),
                }
        else:
            # Not in test mode, proceed with pre-check and remediation
            log.debug("Performing remediation.")
            # Execute remediation
            remediate_response = __salt__["vmware_compliance_control.control_config_remediate"](
                control_config=control_config,
                product=product,
                config_obj=config_obj,
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
