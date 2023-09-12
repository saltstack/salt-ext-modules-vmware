# SPDX-License-Identifier: Apache-2.0
import logging
from saltext.vmware.utils import vmc_state

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False

__virtualname__ = "vmware_vc"
__proxyenabled__ = ["vmware_vc"]


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def lockout_policy(
        current_config=None,
        failure_interval=None,
        failed_login_attempts=None,
        unlock_time=None,
        **kwargs
):
    """
    Manage Lockout Policy for VC

    failure_interval
        Failure interval.

    failed_login_attempts
        Max number failed login attempts

    unlock_time
        Unlock time.
    """
    if current_config is None:
        current_config = {}
    changes = []
    # ret = {"name": {}, "changes": {}, "result": True, "comment": ""}
    if current_config["failure_interval"] and current_config["failure_interval"] != failure_interval:
        changes.append(
            {"name": "failure_interval", "status": "NON_COMPLAINT", "current": current_config["failure_interval"],
             "desired": failure_interval})
    else:
        changes.append(
            {"name": "failure_interval", "status": "COMPLAINT", "current": current_config["failure_interval"],
             "desired": failure_interval})

    if current_config["failed_login_attempts"] and current_config["failed_login_attempts"] != failed_login_attempts:
        changes.append({"name": "failed_login_attempts", "status": "NON_COMPLAINT",
                        "current": current_config["failed_login_attempts"], "desired": failed_login_attempts})
    else:
        changes.append(
            {"name": "failed_login_attempts", "status": "COMPLAINT", "current": current_config["failed_login_attempts"],
             "desired": failed_login_attempts})

    if current_config["unlock_time"] and current_config["unlock_time"] != unlock_time:
        changes.append({"name": "unlock_time", "status": "NON_COMPLAINT", "current": current_config["unlock_time"],
                        "desired": unlock_time})
    else:
        changes.append(
            {"name": "unlock_time", "status": "COMPLAINT", "current": current_config["unlock_time"],
             "desired": unlock_time})
    logging.info("Returning: %s", changes)
    return {"name": kwargs["name"], "comment": "lockout_policy complaince", "result": True,
            "changes": {"all_policies": changes}}
