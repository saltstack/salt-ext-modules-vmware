# SPDX-License-Identifier: Apache-2.0
import logging
import sys

import saltext.vmware.utils.vmware
from salt.utils.decorators import depends
from salt.utils.decorators import ignores_kwargs

log = logging.getLogger(__name__)

try:
    # pylint: disable=no-name-in-module
    from pyVmomi import (
        vim,
        vmodl,
        pbm,
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


__virtualname__ = "vmware_vsan"


def __virtual__():
    return __virtualname__


def _get_vsan_eligible_disks(service_instance, host, host_names):
    """
    Helper function that returns a dictionary of host_name keys with either a list of eligible
    disks that can be added to VSAN or either an 'Error' message or a message saying no
    eligible disks were found. Possible keys/values look like:

    return = {'host_1': {'Error': 'VSAN System Config Manager is unset ...'},
              'host_2': {'Eligible': 'The host xxx does not have any VSAN eligible disks.'},
              'host_3': {'Eligible': [disk1, disk2, disk3, disk4],
              'host_4': {'Eligible': []}}
    """
    ret = {}
    for host_name in host_names:

        # Get VSAN System Config Manager, if available.
        host_ref = _get_host_ref(service_instance, host, host_name=host_name)
        vsan_system = host_ref.configManager.vsanSystem
        if vsan_system is None:
            msg = (
                "VSAN System Config Manager is unset for host '{}'. "
                "VSAN configuration cannot be changed without a configured "
                "VSAN System.".format(host_name)
            )
            log.debug(msg)
            ret.update({host_name: {"Error": msg}})
            continue

        # Get all VSAN suitable disks for this host.
        suitable_disks = []
        query = vsan_system.QueryDisksForVsan()
        for item in query:
            if item.state == "eligible":
                suitable_disks.append(item)

        # No suitable disks were found to add. Warn and move on.
        # This isn't an error as the state may run repeatedly after all eligible disks are added.
        if not suitable_disks:
            msg = "The host '{}' does not have any VSAN eligible disks.".format(host_name)
            log.warning(msg)
            ret.update({host_name: {"Eligible": msg}})
            continue

        # Get disks for host and combine into one list of Disk Objects
        disks = _get_host_ssds(host_ref) + _get_host_non_ssds(host_ref)

        # Get disks that are in both the disks list and suitable_disks lists.
        matching = []
        for disk in disks:
            for suitable_disk in suitable_disks:
                if disk.canonicalName == suitable_disk.disk.canonicalName:
                    matching.append(disk)

        ret.update({host_name: {"Eligible": matching}})

    return ret


def vsan_add_disks(
    host, username, password, protocol=None, port=None, host_names=None, verify_ssl=True
):
    """
    Add any VSAN-eligible disks to the VSAN System for the given host or list of host_names.

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

    host_names
        List of ESXi host names. When the host, username, and password credentials
        are provided for a vCenter Server, the host_names argument is required to
        tell vCenter which hosts need to add any VSAN-eligible disks to the host's
        VSAN system.

        If host_names is not provided, VSAN-eligible disks will be added to the hosts's
        VSAN system for the ``host`` location instead. This is useful for when service
        instance connection information is used for a single ESXi host.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        # Used for single ESXi host connection information
        salt '*' vsphere.vsan_add_disks my.esxi.host root bad-password

        # Used for connecting to a vCenter Server
        salt '*' vsphere.vsan_add_disks my.vcenter.location root bad-password \
        host_names='[esxi-1.host.com, esxi-2.host.com]'
    """
    service_instance = saltext.vmware.utils.vmware.get_service_instance(
        host=host,
        username=username,
        password=password,
        protocol=protocol,
        port=port,
        verify_ssl=verify_ssl,
    )
    host_names = _check_hosts(service_instance, host, host_names)
    response = _get_vsan_eligible_disks(service_instance, host, host_names)

    ret = {}
    for host_name, value in response.items():
        host_ref = _get_host_ref(service_instance, host, host_name=host_name)
        vsan_system = host_ref.configManager.vsanSystem

        # We must have a VSAN Config in place before we can manipulate it.
        if vsan_system is None:
            msg = (
                "VSAN System Config Manager is unset for host '{}'. "
                "VSAN configuration cannot be changed without a configured "
                "VSAN System.".format(host_name)
            )
            log.debug(msg)
            ret.update({host_name: {"Error": msg}})
        else:
            eligible = value.get("Eligible")
            error = value.get("Error")

            if eligible and isinstance(eligible, list):
                # If we have eligible, matching disks, add them to VSAN.
                try:
                    task = vsan_system.AddDisks(eligible)
                    saltext.vmware.utils.vmware.wait_for_task(
                        task, host_name, "Adding disks to VSAN", sleep_seconds=3
                    )
                except vim.fault.InsufficientDisks as err:
                    log.debug(err.msg)
                    ret.update({host_name: {"Error": err.msg}})
                    continue
                except Exception as err:  # pylint: disable=broad-except
                    msg = "'vsphere.vsan_add_disks' failed for host {}: {}".format(host_name, err)
                    log.debug(msg)
                    ret.update({host_name: {"Error": msg}})
                    continue

                log.debug(
                    "Successfully added disks to the VSAN system for host '{}'.".format(host_name)
                )
                # We need to return ONLY the disk names, otherwise Message Pack can't deserialize the disk objects.
                disk_names = []
                for disk in eligible:
                    disk_names.append(disk.canonicalName)
                ret.update({host_name: {"Disks Added": disk_names}})
            elif eligible and isinstance(eligible, str):
                # If we have a string type in the eligible value, we don't
                # have any VSAN-eligible disks. Pull the message through.
                ret.update({host_name: {"Disks Added": eligible}})
            elif error:
                # If we hit an error, populate the Error return dict for state functions.
                ret.update({host_name: {"Error": error}})
            else:
                # If we made it this far, we somehow have eligible disks, but they didn't
                # match the disk list and just got an empty list of matching disks.
                ret.update(
                    {host_name: {"Disks Added": "No new VSAN-eligible disks were found to add."}}
                )

    return ret


def vsan_disable(
    host, username, password, protocol=None, port=None, host_names=None, verify_ssl=True
):
    """
    Disable VSAN for a given host or list of host_names.

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

    host_names
        List of ESXi host names. When the host, username, and password credentials
        are provided for a vCenter Server, the host_names argument is required to
        tell vCenter which hosts should disable VSAN.

        If host_names is not provided, VSAN will be disabled for the ``host``
        location instead. This is useful for when service instance connection
        information is used for a single ESXi host.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        # Used for single ESXi host connection information
        salt '*' vsphere.vsan_disable my.esxi.host root bad-password

        # Used for connecting to a vCenter Server
        salt '*' vsphere.vsan_disable my.vcenter.location root bad-password \
        host_names='[esxi-1.host.com, esxi-2.host.com]'
    """
    service_instance = saltext.vmware.utils.vmware.get_service_instance(
        host=host,
        username=username,
        password=password,
        protocol=protocol,
        port=port,
        verify_ssl=verify_ssl,
    )
    # Create a VSAN Configuration Object and set the enabled attribute to True
    vsan_config = vim.vsan.host.ConfigInfo()
    vsan_config.enabled = False

    host_names = _check_hosts(service_instance, host, host_names)
    ret = {}
    for host_name in host_names:
        host_ref = _get_host_ref(service_instance, host, host_name=host_name)
        vsan_system = host_ref.configManager.vsanSystem

        # We must have a VSAN Config in place before we can manipulate it.
        if vsan_system is None:
            msg = (
                "VSAN System Config Manager is unset for host '{}'. "
                "VSAN configuration cannot be changed without a configured "
                "VSAN System.".format(host_name)
            )
            log.debug(msg)
            ret.update({host_name: {"Error": msg}})
        else:
            try:
                # Disable vsan on the host
                task = vsan_system.UpdateVsan_Task(vsan_config)
                saltext.vmware.utils.vmware.wait_for_task(
                    task, host_name, "Disabling VSAN", sleep_seconds=3
                )
            except vmodl.fault.SystemError as err:
                log.debug(err.msg)
                ret.update({host_name: {"Error": err.msg}})
                continue
            except Exception as err:  # pylint: disable=broad-except
                msg = "'vsphere.vsan_disable' failed for host {}: {}".format(host_name, err)
                log.debug(msg)
                ret.update({host_name: {"Error": msg}})
                continue

            ret.update({host_name: {"VSAN Disabled": True}})

    return ret


def vsan_enable(
    host, username, password, protocol=None, port=None, host_names=None, verify_ssl=True
):
    """
    Enable VSAN for a given host or list of host_names.

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

    host_names
        List of ESXi host names. When the host, username, and password credentials
        are provided for a vCenter Server, the host_names argument is required to
        tell vCenter which hosts should enable VSAN.

        If host_names is not provided, VSAN will be enabled for the ``host``
        location instead. This is useful for when service instance connection
        information is used for a single ESXi host.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        # Used for single ESXi host connection information
        salt '*' vsphere.vsan_enable my.esxi.host root bad-password

        # Used for connecting to a vCenter Server
        salt '*' vsphere.vsan_enable my.vcenter.location root bad-password \
        host_names='[esxi-1.host.com, esxi-2.host.com]'
    """
    service_instance = saltext.vmware.utils.vmware.get_service_instance(
        host=host,
        username=username,
        password=password,
        protocol=protocol,
        port=port,
        verify_ssl=verify_ssl,
    )
    # Create a VSAN Configuration Object and set the enabled attribute to True
    vsan_config = vim.vsan.host.ConfigInfo()
    vsan_config.enabled = True

    host_names = _check_hosts(service_instance, host, host_names)
    ret = {}
    for host_name in host_names:
        host_ref = _get_host_ref(service_instance, host, host_name=host_name)
        vsan_system = host_ref.configManager.vsanSystem

        # We must have a VSAN Config in place before we can manipulate it.
        if vsan_system is None:
            msg = (
                "VSAN System Config Manager is unset for host '{}'. "
                "VSAN configuration cannot be changed without a configured "
                "VSAN System.".format(host_name)
            )
            log.debug(msg)
            ret.update({host_name: {"Error": msg}})
        else:
            try:
                # Enable vsan on the host
                task = vsan_system.UpdateVsan_Task(vsan_config)
                saltext.vmware.utils.vmware.wait_for_task(
                    task, host_name, "Enabling VSAN", sleep_seconds=3
                )
            except vmodl.fault.SystemError as err:
                log.debug(err.msg)
                ret.update({host_name: {"Error": err.msg}})
                continue
            except vim.fault.VsanFault as err:
                msg = "'vsphere.vsan_enable' failed for host {}: {}".format(host_name, err)
                log.debug(msg)
                ret.update({host_name: {"Error": msg}})
                continue

            ret.update({host_name: {"VSAN Enabled": True}})

    return ret


def get_vsan_enabled(
    host,
    username,
    password,
    protocol=None,
    port=None,
    host_names=None,
    verify_ssl=True,
):
    """
    Get the VSAN enabled status for a given host or a list of host_names. Returns ``True``
    if VSAN is enabled, ``False`` if it is not enabled, and ``None`` if a VSAN Host Config
    is unset, per host.

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

    host_names
        List of ESXi host names. When the host, username, and password credentials
        are provided for a vCenter Server, the host_names argument is required to
        tell vCenter which hosts to check if VSAN enabled.

        If host_names is not provided, the VSAN status will be retrieved for the
        ``host`` location instead. This is useful for when service instance
        connection information is used for a single ESXi host.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        # Used for single ESXi host connection information
        salt '*' vsphere.get_vsan_enabled my.esxi.host root bad-password

        # Used for connecting to a vCenter Server
        salt '*' vsphere.get_vsan_enabled my.vcenter.location root bad-password \
        host_names='[esxi-1.host.com, esxi-2.host.com]'
    """
    service_instance = saltext.vmware.utils.vmware.get_service_instance(
        host=host,
        username=username,
        password=password,
        protocol=protocol,
        port=port,
        verify_ssl=verify_ssl,
    )
    host_names = _check_hosts(service_instance, host, host_names)
    ret = {}
    for host_name in host_names:
        host_ref = _get_host_ref(service_instance, host, host_name=host_name)
        vsan_config = host_ref.config.vsanHostConfig

        # We must have a VSAN Config in place get information about VSAN state.
        if vsan_config is None:
            msg = "VSAN System Config Manager is unset for host '{}'.".format(host_name)
            log.debug(msg)
            ret.update({host_name: {"Error": msg}})
        else:
            ret.update({host_name: {"VSAN Enabled": vsan_config.enabled}})

    return ret


def get_vsan_eligible_disks(
    host,
    username,
    password,
    protocol=None,
    port=None,
    host_names=None,
    verify_ssl=True,
):
    """
    Returns a list of VSAN-eligible disks for a given host or list of host_names.

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

    host_names
        List of ESXi host names. When the host, username, and password credentials
        are provided for a vCenter Server, the host_names argument is required to
        tell vCenter which hosts to check if any VSAN-eligible disks are available.

        If host_names is not provided, the VSAN-eligible disks will be retrieved
        for the ``host`` location instead. This is useful for when service instance
        connection information is used for a single ESXi host.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        # Used for single ESXi host connection information
        salt '*' vsphere.get_vsan_eligible_disks my.esxi.host root bad-password

        # Used for connecting to a vCenter Server
        salt '*' vsphere.get_vsan_eligible_disks my.vcenter.location root bad-password \
        host_names='[esxi-1.host.com, esxi-2.host.com]'
    """
    service_instance = saltext.vmware.utils.vmware.get_service_instance(
        host=host,
        username=username,
        password=password,
        protocol=protocol,
        port=port,
        verify_ssl=verify_ssl,
    )
    host_names = _check_hosts(service_instance, host, host_names)
    response = _get_vsan_eligible_disks(service_instance, host, host_names)

    ret = {}
    for host_name, value in response.items():
        error = value.get("Error")
        if error:
            ret.update({host_name: {"Error": error}})
            continue

        disks = value.get("Eligible")
        # If we have eligible disks, it will be a list of disk objects
        if disks and isinstance(disks, list):
            disk_names = []
            # We need to return ONLY the disk names, otherwise
            # MessagePack can't deserialize the disk objects.
            for disk in disks:
                disk_names.append(disk.canonicalName)
            ret.update({host_name: {"Eligible": disk_names}})
        else:
            # If we have disks, but it's not a list, it's actually a
            # string message that we're passing along.
            ret.update({host_name: {"Eligible": disks}})

    return ret


def list_default_vsan_policy(service_instance=None):
    """
    Returns the default vsan storage policy.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.list_storage_policies

        salt '*' vsphere.list_storage_policy policy_names=[policy_name]
    """
    profile_manager = salt.utils.pbm.get_profile_manager(service_instance)
    policies = salt.utils.pbm.get_storage_policies(profile_manager, get_all_policies=True)
    def_policies = [p for p in policies if p.systemCreatedProfileType == "VsanDefaultProfile"]
    if not def_policies:
        raise VMwareObjectRetrievalError("Default VSAN policy was not " "retrieved")
    return _get_policy_dict(def_policies[0])
