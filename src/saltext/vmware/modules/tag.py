# Copyright 2021 VMware, Inc.
# SPDX-License: Apache-2.0
import logging

import salt.exceptions
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.connect as connect

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_tag"


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def create(token=None):
    """
    """
    response = connect.request('/rest/com/vmware/cis/tagging/tag', 'POST', body={
        "create_spec": {
            "category_id": "string",
            "description": "string",
            "name": "string"
        }},
        opts=__opts__, pillar=__pillar__)
    breakpoint()

