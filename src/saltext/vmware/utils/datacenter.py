# SPDX-License-Identifier: Apache-2.0
from os import sys

# pylint: disable=no-name-in-module
try:
    from pyVim.connect import GetSi, SmartConnect, Disconnect, GetStub, SoapStubAdapter
    from pyVmomi import vim, vmodl, VmomiSupport

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


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


def get_service_instance_datacenter(*, service_instance, datacenter_name):
    """
    Return a datacenter from service instance
    """
    datacenter = None
    content = service_instance.content
    for child in content.rootFolder.childEntity:
        if child.name == datacenter_name:
            datacenter = child
            break
    if datacenter == None:
        sys.exit(f"Datacenter {datacenter_name} not found!")
    return datacenter


def get_destination_host(*, service_instance, host_name):
    """
    Return Destination Host
    """
    content = service_instance.content
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    destination_host = None
    for obj in container.view:
        if obj.name == host_name:
            destination_host = obj
            break
    container.Destroy()
    if destination_host == None:
        sys.exit(f"Destination host {host_name} not found!")
    return destination_host


def get_cluster(*, datacenter, cluster_name):
    cluster_list = datacenter.hostFolder.childEntity
    cluster_obj = None
    if cluster_name:
        for cluster in cluster_list:
            if cluster.name == cluster_name:
                cluster_obj = cluster
    elif cluster_obj == None and len(cluster_list) > 0:
        cluster_obj = cluster_list[0]
    else:
        exit(f"No clusters found in datacenter ({datacenter.name}).")
    return cluster_obj
