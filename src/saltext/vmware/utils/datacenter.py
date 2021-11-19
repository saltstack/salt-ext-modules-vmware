# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# pylint: disable=no-name-in-module
import logging

import salt.exceptions
import salt.modules.cmdmod
import salt.utils.path
import salt.utils.platform
import salt.utils.stringutils
from saltext.vmware.utils.common import create_datacenter as create_datacenter
from saltext.vmware.utils.common import delete_datacenter as delete_datacenter
from saltext.vmware.utils.common import get_datacenter as get_datacenter
from saltext.vmware.utils.common import get_datacenters as get_datacenters
from saltext.vmware.utils.common import list_datacenters as list_datacenters

try:
    from pyVmomi import vim, vmodl

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False

log = logging.getLogger(__name__)


def get_vm_datacenter(*, vm):
    """
    Return a datacenter from vm
    """
    datacenter = None
    while True:
        if isinstance(vm, vim.Datacenter):
            datacenter = vm
            break
        try:
            vm = vm.parent
        except AttributeError:
            break
    return datacenter
