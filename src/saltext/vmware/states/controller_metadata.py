# SPDX-License-Identifier: Apache-2.0
import json
import logging

log = logging.getLogger(__name__)

__virtualname__ = "vmware_controller_metadata"
__proxyenabled__ = ["vmware_controller_metadata"]


def __virtual__():
    return __virtualname__


def managed(name, controller_metadata, **kwargs):
    """
    Validates that the controller custom metadata is valid - has correct product/controls, format, and types.
    If valid, will then invoke the file.managed module to persist the controller custom metadata.

    name
        The location of the file to manage, as an absolute path.
    controller_metadata
        controller metadata dict to validate and persist
    kwargs
        Keyword arguments to pass to 'file.managed' state module
    """

    log.info("Starting controller_metadata.managed for %s", name)

    __salt__[
        "vmware_controller_metadata.validate"
    ](
        controller_metadata=controller_metadata,
    )

    log.info("Controller metadata successfully validated")

    log.info("Calling file.managed for controller metadata")
    return __states__['file.managed'](name, contents=json.dumps(controller_metadata), **kwargs)
