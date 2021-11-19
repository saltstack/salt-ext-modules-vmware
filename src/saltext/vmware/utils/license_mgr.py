# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# pylint: disable=no-name-in-module
import logging

import salt.exceptions
import salt.modules.cmdmod
import salt.utils.path
import salt.utils.platform
import salt.utils.stringutils
from saltext.vmware.utils.common import get_license_mgr as get_license_mgr
from saltext.vmware.utils.common import get_license_mgrs as get_license_mgrs
from saltext.vmware.utils.common import list_license_mgrs as list_license_mgrs

## from saltext.vmware.utils.common import create_datacenter as create_datacenter
## from saltext.vmware.utils.common import delete_datacenter as delete_datacenter

try:
    from pyVmomi import vim, vmodl

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False

log = logging.getLogger(__name__)


def get_license_mgr(*, vm):
    """
    Return a license manager from vm
    """
    lic_mgr = None
    while True:
        if isinstance(vm, vim.LicenseAssignmentManager):
            lic_mgr = vm
            break
        try:
            vm = vm.parent
        except AttributeError:
            break
    return lic_mgr
