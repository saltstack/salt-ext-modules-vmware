# Copyright 2021 VMware, Inc.
# SPDX-License: Apache-2.0
import logging

import salt.exceptions
import saltext.vmware.utils.cluster as utils_cluster
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.esxi as utils_esxi
import saltext.vmware.utils.vmware as utils_vmware
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
    dc_ref = None
    if datacenter_name:
        dc_ref = utils_common.get_datacenter(service_instance, datacenter_name)
    ds = utils_common.get_datastore(datastore_name, dc_ref, service_instance)
    ret = utils_common.datastore_enter_maintenance_mode(ds)
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
    dc_ref = None
    if datacenter_name:
        dc_ref = utils_common.get_datacenter(service_instance, datacenter_name)
    ds = utils_common.get_datastore(datastore_name, dc_ref, service_instance)
    ret = utils_common.datastore_exit_maintenance_mode(ds)
    if ret:
        return {"maintenanceMode": "normal"}
    return {"maintenanceMode": "failed to exit maintenance mode"}


def _find_filtered_object(
    service_instance, datacenter_name=None, cluster_name=None, host_name=None
):
    """
    finds zero or one matching objects: plug in almost any combination of datacenter, cluster, and/or host name
    *if cluster_name is passed, datacenter_name must also be passed

    The most specific object will be returned.

    If the combination of parameters has the *potential* to match multiple objects, an exception is raised.

    At least one of these parameters must be set.

    service_instance
        The Service Instance Object from which to obtain cluster.

    datacenter_name
        (Optional) Datacenter name to filter by.

    cluster_name
        (Optional) Exact cluster name to filter by. If used, datacenter_name is required.

    host_name
        (Optional) Exact host name name to filter by.
    """
    try:
        if host_name:
            hosts = utils_esxi.get_hosts(
                service_instance,
                datacenter_name=datacenter_name,
                cluster_name=cluster_name,
                host_names=[host_name],
            )
            return hosts[0] if hosts else None
        elif cluster_name:
            datacenter = utils_common.get_datacenter(service_instance, datacenter_name)
            return utils_cluster.get_cluster(datacenter, cluster_name)
        elif datacenter_name:
            return utils_common.get_datacenter(service_instance, datacenter_name=datacenter_name)
        else:
            raise salt.exceptions.ArgumentValueError(
                "_find_filtered_object requires at least one of datacenter_name, host_name, or cluster_name with datacenter_name"
            )
    except salt.exceptions.VMwareObjectRetrievalError:
        return None


def _get_datastores(
    service_instance, datastore_name=None, datacenter_name=None, cluster_name=None, host_name=None
):
    """
    Gets datastores on the most specific of host_name, cluster_name, datacenter_name, or everywhere.

    Then optionally filters them by datastore_name.
    """
    if datacenter_name or cluster_name or host_name:
        reference = _find_filtered_object(
            service_instance,
            datacenter_name=datacenter_name,
            cluster_name=cluster_name,
            host_name=host_name,
        )
        return utils_vmware.get_datastores(
            service_instance,
            reference=reference,
            datastore_names=[datastore_name],
            get_all_datastores=not datastore_name,
        )
    else:
        # utils_vmware.get_datastores doesn't actually find all datastores when searching everything, this should work
        datastores = utils_common.get_mors_with_properties(
            service_instance, vim.Datastore, property_list=["name"]
        )
        if not datastore_name:
            return [datastore["object"] for datastore in datastores]
        else:
            return [
                datastore["object"]
                for datastore in datastores
                if datastore["name"] == datastore_name
            ]


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
    log.debug("Running vmware_esxi.get_datastore")
    ret = []
    if not service_instance:
        service_instance = get_service_instance(opts=__opts__, pillar=__pillar__)
    datastores = _get_datastores(
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
