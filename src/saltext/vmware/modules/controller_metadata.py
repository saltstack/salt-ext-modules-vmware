# SPDX-License: Apache-2.0
import logging

import salt.exceptions
from config_modules_vmware.interfaces.metadata_interface import ControllerMetadataInterface

log = logging.getLogger(__name__)

__virtualname__ = "vmware_controller_metadata"


def __virtual__():
    return __virtualname__


def validate(controller_metadata):
    """
    Validates that the controller custom metadata is valid - has correct product/controls, format, and types.

    controller_metadata
        controller metadata dict to validate
    """

    log.info("Validating controller metadata: %s", controller_metadata)

    try:
        ControllerMetadataInterface.validate_custom_metadata(controller_metadata)
    except Exception as exc:
        log.error("Error when validating controller metadata: %s", str(exc))
        raise salt.exceptions.VMwareRuntimeError(str(exc))
