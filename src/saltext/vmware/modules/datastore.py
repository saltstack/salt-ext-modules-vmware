# Copyright 2021 VMware, Inc.
# SPDX-License: Apache-2.0
import logging

import salt.exceptions
import saltext.vmware.utils.common as utils_common
from saltext.vmware.utils.connect import get_service_instance

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_datastore"


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def maintenance_mode(datastore_name, dc_name=None, service_instance=None):
    """
    Put datastore in maintenance mode.

    datastore_name
        Name of datastore.
    
    dc_name
        Name of datacenter where folder will be created.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.
    """
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    dc_ref = None
    if dc_name:
        dc_ref = utils_common.get_datacenter(service_instance, dc_name)
    ds = utils_common.get_datastore(datastore_name, dc_ref, service_instance)
    ret = utils_common.datastore_enter_maintenance_mode(ds)
    if ret:
        return {"maintenanceMode": "inMaintenance"}
    return {"maintenanceMode": "failed to enter maintenance mode"}


def exit_maintenance_mode(datastore_name, dc_name=None, service_instance=None):
    """
    Take datastore out of maintenance mode.

    datastore_name
        Name of datastore.
    
    dc_name
        Name of datacenter where folder will be created.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.
    """
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    dc_ref = None
    if dc_name:
        dc_ref = utils_common.get_datacenter(service_instance, dc_name)
    ds = utils_common.get_datastore(datastore_name, dc_ref, service_instance)
    ret = utils_common.datastore_exit_maintenance_mode(ds)
    if ret:
        return {"maintenanceMode": "normal"}
    return {"maintenanceMode": "failed to exit maintenance mode"}