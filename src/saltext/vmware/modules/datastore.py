# Copyright 2021 VMware, Inc.
# SPDX-License: Apache-2.0
import logging

import saltext.vmware.utils.datastore as utils_datastore
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


def maintenance_mode(datastore_name, datacenter_name=None, service_instance=None):
    """
    Put datastore in maintenance mode.

    datastore_name
        Name of datastore.

    datacenter_name
        (optional) Name of datacenter where datastore exists.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.
    """
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    assert isinstance(datastore_name, str)
    datastores = utils_datastore.get_datastores(
        service_instance, datastore_name=datastore_name, datacenter_name=datacenter_name
    )
    ds = datastores[0] if datastores else None
    ret = utils_datastore.enter_maintenance_mode(ds)
    if ret:
        return {"maintenanceMode": "inMaintenance"}
    return {"maintenanceMode": "failed to enter maintenance mode"}


def exit_maintenance_mode(datastore_name, datacenter_name=None, service_instance=None):
    """
    Take datastore out of maintenance mode.

    datastore_name
        Name of datastore.

    datacenter_name
        (optional) Name of datacenter where datastore exists.

    service_instance
        (optional) The Service Instance from which to obtain managed object references.
    """
    if service_instance is None:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    assert isinstance(datastore_name, str)
    datastores = utils_datastore.get_datastores(
        service_instance, datastore_name=datastore_name, datacenter_name=datacenter_name
    )
    ds = datastores[0] if datastores else None
    ret = utils_datastore.exit_maintenance_mode(ds)
    if ret:
        return {"maintenanceMode": "normal"}
    return {"maintenanceMode": "failed to exit maintenance mode"}


def get(
    datastore_name=None,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
):
    """
    Return info about datastores.

    datacenter_name
        Filter by this datacenter name (required when cluster is not specified)

    datacenter_name
        Filter by this datacenter name (required when cluster is not specified)

    cluster_name
        Filter by this cluster name (required when datacenter is not specified)

    host_name
        Filter by this ESXi hostname (optional).

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    """
    log.debug(f"Running {__virtualname__}.get")
    ret = []
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    datastores = utils_datastore.get_datastores(
        service_instance,
        datastore_name=datastore_name,
        datacenter_name=datacenter_name,
        cluster_name=cluster_name,
        host_name=host_name,
    )

    for datastore in datastores:
        summary = datastore.summary
        info = {
            "accessible": summary.accessible,
            "capacity": summary.capacity,
            "freeSpace": summary.freeSpace,
            "maintenanceMode": summary.maintenanceMode,
            "multipleHostAccess": summary.multipleHostAccess,
            "name": summary.name,
            "type": summary.type,
            "url": summary.url,
            "uncommitted": summary.uncommitted if summary.uncommitted else 0,
        }
        ret.append(info)

    return ret
