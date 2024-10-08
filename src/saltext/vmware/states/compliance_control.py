# SPDX-License-Identifier: Apache-2.0
import json
import logging

import saltext.vmware.utils.compliance_control as compliance_control_util
from config_modules_vmware.framework.models.output_models.compliance_response import (
    ComplianceStatus,
)
from config_modules_vmware.framework.models.output_models.remediate_response import RemediateStatus

log = logging.getLogger(__name__)

__virtualname__ = "vmware_compliance_control"
__proxyenabled__ = ["vmware_compliance_control"]


def __virtual__():
    return __virtualname__


def check_control(name, control_config, product, ids=None):
    """
    Check and apply vcenter control configs. Control config can be ntp, dns, syslog, etc.
    Return control compliance response if test=true. Otherwise, return remediate response.

    name
        Config name
    control_config
        vc control config dict object.
    product
        appliance name. vcenter, nsx, etc.
    ids
        List of product ids within the parent product.
    """

    log.info("Starting compliance check for %s", name)

    config = __opts__
    auth_context = compliance_control_util.create_auth_context(
        config=config, product=product, ids=ids
    )
    control_config = json.loads(json.dumps(control_config))
    log.debug("Opts: %s", __opts__)

    try:
        compliance_config = control_config.get("compliance_config")
        if not isinstance(compliance_config, dict) or not compliance_config:
            raise Exception(f"Desired spec is empty or not in correct format")
        else:
            product_control_config = control_config.get("compliance_config", {}).get(product)
            if product_control_config:
                control_config = {"compliance_config": {product: product_control_config}}
            else:
                err_msg = f"Desired spec is empty for {product}"
                log.error(err_msg)
                return {
                    "name": name,
                    "result": None,
                    "changes": {},
                    "comment": err_msg,
                }

        if __opts__["test"]:
            # If in test mode, perform audit
            log.info("Running in test mode. Performing check_control_compliance_response.")
            check_control_compliance_response = __salt__[
                "vmware_compliance_control.control_config_compliance_check"
            ](
                control_config=control_config,
                product=product,
                auth_context=auth_context,
            )

            if (
                check_control_compliance_response["status"] == ComplianceStatus.COMPLIANT
                or check_control_compliance_response["status"] == ComplianceStatus.SKIPPED
            ):
                ret = {
                    "name": name,
                    "result": True,
                    "comment": check_control_compliance_response["status"],
                    "changes": check_control_compliance_response.get("changes", {}),
                }
            elif (
                check_control_compliance_response["status"] == ComplianceStatus.NON_COMPLIANT
                or check_control_compliance_response["status"] == ComplianceStatus.FAILED
            ):
                ret = {
                    "name": name,
                    "result": (
                        None
                        if check_control_compliance_response["status"]
                        == ComplianceStatus.NON_COMPLIANT
                        else False
                    ),
                    "comment": check_control_compliance_response["status"],
                    "changes": check_control_compliance_response.get("changes", {}),
                }
            else:
                # Exception running compliance workflow
                ret = {
                    "name": name,
                    "result": False,
                    "comment": "Failed to run compliance check. Please check changes for more details.",
                    "changes": {
                        "message": check_control_compliance_response.get(
                            "message", "Exception running compliance."
                        )
                    },
                }
        else:
            # Not in test mode, proceed with pre-check and remediation
            log.debug("Performing remediation.")
            remediate_response = __salt__["vmware_compliance_control.control_config_remediate"](
                control_config=control_config,
                product=product,
                auth_context=auth_context,
            )

            if remediate_response["status"] == RemediateStatus.SUCCESS:
                log.debug("Remediation completed with success status.")
                # Update return data for successful remediation
                ret = {
                    "name": name,
                    "result": True,
                    "changes": remediate_response.get("changes", {}),
                    "comment": "Remediation completed successfully.",
                }
            elif remediate_response["status"] == RemediateStatus.SKIPPED:
                log.debug("Remediation completed with skipped status.")
                ret = {
                    "name": name,
                    "result": True,
                    "changes": remediate_response.get("changes", {}),
                    "comment": "Nothing to remediate.",
                }
            elif remediate_response["status"] == RemediateStatus.FAILED:
                log.debug("Remediation failed.")
                # Update return data for failed remediation
                ret = {
                    "name": name,
                    "result": False,
                    "comment": "Remediation failed.",
                    "changes": remediate_response.get("changes", {}),
                }
            elif remediate_response["status"] == RemediateStatus.PARTIAL:
                log.debug("Remediation completed partially.")
                ret = {
                    "name": name,
                    "result": False,
                    "comment": "Remediation completed with status partial.",
                    "changes": remediate_response.get("changes", {}),
                }
            else:
                # Exception running remediation workflow
                ret = {
                    "name": name,
                    "result": False,
                    "comment": remediate_response["status"],
                    "changes": {
                        "message": remediate_response.get(
                            "message", "Exception running remediation."
                        ),
                    },
                }

    except Exception as e:
        # Exception occurred
        log.error("An error occurred: %s", str(e))
        return {
            "name": name,
            "result": False,
            "changes": {},
            "comment": f"An error occurred: {str(e)}",
        }

    log.debug("Completed workflow for %s", name)
    return ret
