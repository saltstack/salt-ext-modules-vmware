# SPDX-License-Identifier: Apache-2.0
import logging
import sys

import salt.utils.platform
import saltext.vmware.utils.vmware
from salt.utils.decorators import depends
from salt.utils.decorators import ignores_kwargs

log = logging.getLogger(__name__)

try:
    from saltext.vmware.config.schemas.esxi import (
        vim,
        vmodl,
        VmomiSupport,
    )

    # pylint: enable=no-name-in-module

    # We check the supported vim versions to infer the pyVmomi version
    if (
        "vim25/6.0" in VmomiSupport.versionMap
        and sys.version_info > (2, 7)
        and sys.version_info < (2, 7, 9)
    ):

        log.debug("pyVmomi not loaded: Incompatible versions " "of Python. See Issue #29537.")
        raise ImportError()
    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


__virtualname__ = "vmware_datastore"


def __virtual__():
    return __virtualname__


def list_datastore_clusters(
    host=None, vcenter=None, username=None, password=None, protocol=None, port=None, verify_ssl=True
):
    """
    Returns a list of datastore clusters for the specified host.

    host
        The location of the host.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        salt '*' vsphere.list_datastore_clusters 1.2.3.4 root bad-password
    """
    if salt.utils.platform.is_proxy():
        details = __salt__["vmware_info.get_proxy_connection_details"]()
    else:
        details = __salt__["vmware_info.get_connection_details"](
            host=host,
            vcenter=vcenter,
            username=username,
            password=password,
            protocol=protocol,
            port=port,
            verify_ssl=verify_ssl,
        )

    service_instance = saltext.vmware.utils.vmware.get_service_instance(**details)

    return saltext.vmware.utils.vmware.list_datastore_clusters(service_instance)


def list_datastores(
    host=None, vcenter=None, username=None, password=None, protocol=None, port=None, verify_ssl=True
):
    """
    Returns a list of datastores for the specified host.

    host
        The location of the host.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        salt '*' vsphere.list_datastores 1.2.3.4 root bad-password
    """
    if salt.utils.platform.is_proxy():
        details = __salt__["vmware_info.get_proxy_connection_details"]()
    else:
        details = __salt__["vmware_info.get_connection_details"](
            host=host,
            vcenter=vcenter,
            username=username,
            password=password,
            protocol=protocol,
            port=port,
            verify_ssl=verify_ssl,
        )

    service_instance = saltext.vmware.utils.vmware.get_service_instance(**details)
    return saltext.vmware.utils.vmware.list_datastores(service_instance)


def assign_default_storage_policy_to_datastore(policy, datastore, service_instance=None):
    """
    Assigns a storage policy as the default policy to a datastore.

    policy
        Name of the policy to assign.

    datastore
        Name of the datastore to assign.
        The datastore needs to be visible to the VMware entity the proxy
        points to.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.assign_storage_policy_to_datastore
            policy='policy name' datastore=ds1
    """
    log.trace("Assigning policy {} to datastore {}" "".format(policy, datastore))
    profile_manager = salt.utils.pbm.get_profile_manager(service_instance)
    # Find policy
    policies = salt.utils.pbm.get_storage_policies(profile_manager, [policy])
    if not policies:
        raise VMwareObjectRetrievalError("Policy '{}' was not found" "".format(policy))
    policy_ref = policies[0]
    # Find datastore
    target_ref = _get_proxy_target(service_instance)
    ds_refs = salt.utils.vmware.get_datastores(
        service_instance, target_ref, datastore_names=[datastore]
    )
    if not ds_refs:
        raise VMwareObjectRetrievalError("Datastore '{}' was not " "found".format(datastore))
    ds_ref = ds_refs[0]
    salt.utils.pbm.assign_default_storage_policy_to_datastore(profile_manager, policy_ref, ds_ref)
    return True


def list_datacenters_via_proxy(datacenter_names=None, service_instance=None):
    """
    Returns a list of dict representations of VMware datacenters.
    Connection is done via the proxy details.

    Supported proxies: esxdatacenter

    datacenter_names
        List of datacenter names.
        Default is None.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.list_datacenters_via_proxy

        salt '*' vsphere.list_datacenters_via_proxy dc1

        salt '*' vsphere.list_datacenters_via_proxy dc1,dc2

        salt '*' vsphere.list_datacenters_via_proxy datacenter_names=[dc1, dc2]
    """
    if not datacenter_names:
        dc_refs = salt.utils.vmware.get_datacenters(service_instance, get_all_datacenters=True)
    else:
        dc_refs = salt.utils.vmware.get_datacenters(service_instance, datacenter_names)

    return [{"name": salt.utils.vmware.get_managed_object_name(dc_ref)} for dc_ref in dc_refs]


def create_vmfs_datastore(
    datastore_name,
    disk_id,
    vmfs_major_version,
    safety_checks=True,
    service_instance=None,
):
    """
    Creates a ESXi host disk group with the specified cache and capacity disks.

    datastore_name
        The name of the datastore to be created.

    disk_id
        The disk id (canonical name) on which the datastore is created.

    vmfs_major_version
        The VMFS major version.

    safety_checks
        Specify whether to perform safety check or to skip the checks and try
        performing the required task. Default is True.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.create_vmfs_datastore datastore_name=ds1 disk_id=
            vmfs_major_version=5
    """

    log.debug("Validating vmfs datastore input")
    schema = VmfsDatastoreSchema.serialize()
    try:
        jsonschema.validate(
            {
                "datastore": {
                    "name": datastore_name,
                    "backing_disk_id": disk_id,
                    "vmfs_version": vmfs_major_version,
                }
            },
            schema,
        )
    except jsonschema.exceptions.ValidationError as exc:
        raise ArgumentValueError(exc)
    host_ref = __salt__["vmware_info.get_proxy_target"](service_instance)
    hostname = __proxy__["esxi.get_details"]()["esxi_host"]
    if safety_checks:
        disks = salt.utils.vmware.get_disks(host_ref, disk_ids=[disk_id])
        if not disks:
            raise VMwareObjectRetrievalError(
                "Disk '{}' was not found in host '{}'".format(disk_id, hostname)
            )
    ds_ref = saltext.vmware.utils.vmware.create_vmfs_datastore(
        host_ref, datastore_name, disks[0], vmfs_major_version
    )
    return True


def rename_datastore(datastore_name, new_datastore_name, service_instance=None):
    """
    Renames a datastore. The datastore needs to be visible to the proxy.

    datastore_name
        Current datastore name.

    new_datastore_name
        New datastore name.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.rename_datastore old_name new_name
    """
    # Argument validation
    log.trace("Renaming datastore {} to {}" "".format(datastore_name, new_datastore_name))
    target = _get_proxy_target(service_instance)
    datastores = salt.utils.vmware.get_datastores(
        service_instance, target, datastore_names=[datastore_name]
    )
    if not datastores:
        raise VMwareObjectRetrievalError("Datastore '{}' was not found" "".format(datastore_name))
    ds = datastores[0]
    salt.utils.vmware.rename_datastore(ds, new_datastore_name)
    return True


def remove_datastore(datastore, service_instance=None):
    """
    Removes a datastore. If multiple datastores an error is raised.

    datastore
        Datastore name

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.remove_datastore ds_name
    """
    log.trace("Removing datastore '{}'".format(datastore))
    target = _get_proxy_target(service_instance)
    datastores = salt.utils.vmware.get_datastores(
        service_instance, reference=target, datastore_names=[datastore]
    )
    if not datastores:
        raise VMwareObjectRetrievalError("Datastore '{}' was not found".format(datastore))
    if len(datastores) > 1:
        raise VMwareObjectRetrievalError("Multiple datastores '{}' were found".format(datastore))
    salt.utils.vmware.remove_datastore(service_instance, datastores[0])
    return True


def list_storage_policies(policy_names=None, service_instance=None):
    """
    Returns a list of storage policies.

    policy_names
        Names of policies to list. If None, all policies are listed.
        Default is None.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.list_storage_policies

        salt '*' vsphere.list_storage_policy policy_names=[policy_name]
    """
    profile_manager = salt.utils.pbm.get_profile_manager(service_instance)
    if not policy_names:
        policies = salt.utils.pbm.get_storage_policies(profile_manager, get_all_policies=True)
    else:
        policies = salt.utils.pbm.get_storage_policies(profile_manager, policy_names)
    return [_get_policy_dict(p) for p in policies]


def list_default_storage_policy_of_datastore(
    datastore,
    host=None,
    vcenter=None,
    username=None,
    password=None,
    protocol=None,
    port=None,
    verify_ssl=True,
):
    """
    Returns a list of datastores assign the storage policies.

    datastore
        Name of the datastore to assign.
        The datastore needs to be visible to the VMware entity the proxy
        points to.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.list_default_storage_policy_of_datastore datastore=ds1
    """
    log.trace("Listing the default storage policy of datastore '{}'" "".format(datastore))
    if salt.utils.platform.is_proxy():
        details = __salt__["vmware_info.get_proxy_connection_details"]()
    else:
        details = __salt__["vmware_info.get_connection_details"](
            host=host,
            vcenter=vcenter,
            username=username,
            password=password,
            protocol=protocol,
            port=port,
            verify_ssl=verify_ssl,
        )

    service_instance = saltext.vmware.utils.vmware.get_service_instance(**details)

    # Find datastore
    target_ref = __salt__["vmware_info.get_proxy_target"](service_instance)
    ds_refs = saltext.vmware.utils.vmware.get_datastores(
        service_instance, target_ref, datastore_names=[datastore]
    )
    if not ds_refs:
        raise VMwareObjectRetrievalError("Datastore '{}' was not " "found".format(datastore))
    profile_manager = salt.utils.pbm.get_profile_manager(service_instance)
    policy = salt.utils.pbm.get_default_storage_policy_of_datastore(profile_manager, ds_refs[0])
    return saltext.vmware.utils.get_policy_dict(policy)


def _apply_policy_config(policy_spec, policy_dict):
    """Applies a policy dictionary to a policy spec"""
    log.trace("policy_dict = {}".format(policy_dict))
    if policy_dict.get("name"):
        policy_spec.name = policy_dict["name"]
    if policy_dict.get("description"):
        policy_spec.description = policy_dict["description"]
    if policy_dict.get("subprofiles"):
        # Incremental changes to subprofiles and capabilities are not
        # supported because they would complicate updates too much
        # The whole configuration of all sub-profiles is expected and applied
        policy_spec.constraints = pbm.profile.SubProfileCapabilityConstraints()
        subprofiles = []
        for subprofile_dict in policy_dict["subprofiles"]:
            subprofile_spec = pbm.profile.SubProfileCapabilityConstraints.SubProfile(
                name=subprofile_dict["name"]
            )
            cap_specs = []
            if subprofile_dict.get("force_provision"):
                subprofile_spec.forceProvision = subprofile_dict["force_provision"]
            for cap_dict in subprofile_dict["capabilities"]:
                prop_inst_spec = pbm.capability.PropertyInstance(id=cap_dict["id"])
                setting_type = cap_dict["setting"]["type"]
                if setting_type == "set":
                    prop_inst_spec.value = pbm.capability.types.DiscreteSet()
                    prop_inst_spec.value.values = cap_dict["setting"]["values"]
                elif setting_type == "range":
                    prop_inst_spec.value = pbm.capability.types.Range()
                    prop_inst_spec.value.max = cap_dict["setting"]["max"]
                    prop_inst_spec.value.min = cap_dict["setting"]["min"]
                elif setting_type == "scalar":
                    prop_inst_spec.value = cap_dict["setting"]["value"]
                cap_spec = pbm.capability.CapabilityInstance(
                    id=pbm.capability.CapabilityMetadata.UniqueId(
                        id=cap_dict["id"], namespace=cap_dict["namespace"]
                    ),
                    constraint=[
                        pbm.capability.ConstraintInstance(propertyInstance=[prop_inst_spec])
                    ],
                )
                cap_specs.append(cap_spec)
            subprofile_spec.capability = cap_specs
            subprofiles.append(subprofile_spec)
        policy_spec.constraints.subProfiles = subprofiles
    log.trace("updated policy_spec = {}".format(policy_spec))
    return policy_spec


def create_storage_policy(policy_name, policy_dict, service_instance=None):
    """
    Creates a storage policy.

    Supported capability types: scalar, set, range.

    policy_name
        Name of the policy to create.
        The value of the argument will override any existing name in
        ``policy_dict``.

    policy_dict
        Dictionary containing the changes to apply to the policy.
        (example in salt.states.pbm)

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.create_storage_policy policy_name='policy name'
            policy_dict="$policy_dict"
    """
    log.trace("create storage policy '{}', dict = {}" "".format(policy_name, policy_dict))
    profile_manager = salt.utils.pbm.get_profile_manager(service_instance)
    policy_create_spec = pbm.profile.CapabilityBasedProfileCreateSpec()
    # Hardcode the storage profile resource type
    policy_create_spec.resourceType = pbm.profile.ResourceType(
        resourceType=pbm.profile.ResourceTypeEnum.STORAGE
    )
    # Set name argument
    policy_dict["name"] = policy_name
    log.trace("Setting policy values in policy_update_spec")
    _apply_policy_config(policy_create_spec, policy_dict)
    salt.utils.pbm.create_storage_policy(profile_manager, policy_create_spec)
    return {"create_storage_policy": True}


def update_storage_policy(policy, policy_dict, service_instance=None):
    """
    Updates a storage policy.

    Supported capability types: scalar, set, range.

    policy
        Name of the policy to update.

    policy_dict
        Dictionary containing the changes to apply to the policy.
        (example in salt.states.pbm)

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.update_storage_policy policy='policy name'
            policy_dict="$policy_dict"
    """
    log.trace("updating storage policy, dict = {}".format(policy_dict))
    profile_manager = salt.utils.pbm.get_profile_manager(service_instance)
    policies = salt.utils.pbm.get_storage_policies(profile_manager, [policy])
    if not policies:
        raise VMwareObjectRetrievalError("Policy '{}' was not found" "".format(policy))
    policy_ref = policies[0]
    policy_update_spec = pbm.profile.CapabilityBasedProfileUpdateSpec()
    log.trace("Setting policy values in policy_update_spec")
    for prop in ["description", "constraints"]:
        setattr(policy_update_spec, prop, getattr(policy_ref, prop))
    _apply_policy_config(policy_update_spec, policy_dict)
    salt.utils.pbm.update_storage_policy(profile_manager, policy_ref, policy_update_spec)
    return {"update_storage_policy": True}
