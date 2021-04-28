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


__virtualname__ = "vmware_service"


def __virtual__():
    return __virtualname__


def _get_service_manager(host_reference):
    """
    Helper function that returns a service manager object from a given host object.
    """
    return host_reference.configManager.serviceSystem


def service_start(
    host,
    username,
    password,
    service_name,
    protocol=None,
    port=None,
    host_names=None,
    verify_ssl=True,
):
    """
    Start the named service for the given host or list of hosts.

    host
        The location of the host.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    service_name
        The name of the service for which to set the policy. Supported service names are:
          - DCUI
          - TSM
          - SSH
          - lbtd
          - lsassd
          - lwiod
          - netlogond
          - ntpd
          - sfcbd-watchdog
          - snmpd
          - vprobed
          - vpxa
          - xorg

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    host_names
        List of ESXi host names. When the host, username, and password credentials
        are provided for a vCenter Server, the host_names argument is required to tell
        vCenter the hosts for which to start the service.

        If host_names is not provided, the service will be started for the ``host``
        location instead. This is useful for when service instance connection information
        is used for a single ESXi host.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        # Used for single ESXi host connection information
        salt '*' vsphere.service_start my.esxi.host root bad-password 'ntpd'

        # Used for connecting to a vCenter Server
        salt '*' vsphere.service_start my.vcenter.location root bad-password 'ntpd' \
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
    valid_services = [
        "DCUI",
        "TSM",
        "SSH",
        "ssh",
        "lbtd",
        "lsassd",
        "lwiod",
        "netlogond",
        "ntpd",
        "sfcbd-watchdog",
        "snmpd",
        "vprobed",
        "vpxa",
        "xorg",
    ]
    ret = {}

    # Don't require users to know that VMware lists the ssh service as TSM-SSH
    if service_name == "SSH" or service_name == "ssh":
        temp_service_name = "TSM-SSH"
    else:
        temp_service_name = service_name

    for host_name in host_names:
        # Check if the service_name provided is a valid one.
        # If we don't have a valid service, return. The service will be invalid for all hosts.
        if service_name not in valid_services:
            ret.update(
                {host_name: {"Error": "{} is not a valid service name.".format(service_name)}}
            )
            return ret

        host_ref = _get_host_ref(service_instance, host, host_name=host_name)
        service_manager = _get_service_manager(host_ref)
        log.debug("Starting the '{}' service on {}.".format(service_name, host_name))

        # Start the service
        try:
            service_manager.StartService(id=temp_service_name)
        except vim.fault.HostConfigFault as err:
            msg = "'vsphere.service_start' failed for host {}: {}".format(host_name, err)
            log.debug(msg)
            ret.update({host_name: {"Error": msg}})
            continue
        # Some services are restricted by the vSphere License Level.
        except vim.fault.RestrictedVersion as err:
            log.debug(err)
            ret.update({host_name: {"Error": err}})
            continue

        ret.update({host_name: {"Service Started": True}})

    return ret


def service_stop(
    host,
    username,
    password,
    service_name,
    protocol=None,
    port=None,
    host_names=None,
    verify_ssl=True,
):
    """
    Stop the named service for the given host or list of hosts.

    host
        The location of the host.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    service_name
        The name of the service for which to set the policy. Supported service names are:
          - DCUI
          - TSM
          - SSH
          - lbtd
          - lsassd
          - lwiod
          - netlogond
          - ntpd
          - sfcbd-watchdog
          - snmpd
          - vprobed
          - vpxa
          - xorg

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    host_names
        List of ESXi host names. When the host, username, and password credentials
        are provided for a vCenter Server, the host_names argument is required to tell
        vCenter the hosts for which to stop the service.

        If host_names is not provided, the service will be stopped for the ``host``
        location instead. This is useful for when service instance connection information
        is used for a single ESXi host.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        # Used for single ESXi host connection information
        salt '*' vsphere.service_stop my.esxi.host root bad-password 'ssh'

        # Used for connecting to a vCenter Server
        salt '*' vsphere.service_stop my.vcenter.location root bad-password 'ssh' \
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
    valid_services = [
        "DCUI",
        "TSM",
        "SSH",
        "ssh",
        "lbtd",
        "lsassd",
        "lwiod",
        "netlogond",
        "ntpd",
        "sfcbd-watchdog",
        "snmpd",
        "vprobed",
        "vpxa",
        "xorg",
    ]
    ret = {}

    # Don't require users to know that VMware lists the ssh service as TSM-SSH
    if service_name == "SSH" or service_name == "ssh":
        temp_service_name = "TSM-SSH"
    else:
        temp_service_name = service_name

    for host_name in host_names:
        # Check if the service_name provided is a valid one.
        # If we don't have a valid service, return. The service will be invalid for all hosts.
        if service_name not in valid_services:
            ret.update(
                {host_name: {"Error": "{} is not a valid service name.".format(service_name)}}
            )
            return ret

        host_ref = _get_host_ref(service_instance, host, host_name=host_name)
        service_manager = _get_service_manager(host_ref)
        log.debug("Stopping the '{}' service on {}.".format(service_name, host_name))

        # Stop the service.
        try:
            service_manager.StopService(id=temp_service_name)
        except vim.fault.HostConfigFault as err:
            msg = "'vsphere.service_stop' failed for host {}: {}".format(host_name, err)
            log.debug(msg)
            ret.update({host_name: {"Error": msg}})
            continue
        # Some services are restricted by the vSphere License Level.
        except vim.fault.RestrictedVersion as err:
            log.debug(err)
            ret.update({host_name: {"Error": err}})
            continue

        ret.update({host_name: {"Service Stopped": True}})

    return ret


def service_restart(
    host,
    username,
    password,
    service_name,
    protocol=None,
    port=None,
    host_names=None,
    verify_ssl=True,
):
    """
    Restart the named service for the given host or list of hosts.

    host
        The location of the host.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    service_name
        The name of the service for which to set the policy. Supported service names are:
          - DCUI
          - TSM
          - SSH
          - lbtd
          - lsassd
          - lwiod
          - netlogond
          - ntpd
          - sfcbd-watchdog
          - snmpd
          - vprobed
          - vpxa
          - xorg

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    host_names
        List of ESXi host names. When the host, username, and password credentials
        are provided for a vCenter Server, the host_names argument is required to tell
        vCenter the hosts for which to restart the service.

        If host_names is not provided, the service will be restarted for the ``host``
        location instead. This is useful for when service instance connection information
        is used for a single ESXi host.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        # Used for single ESXi host connection information
        salt '*' vsphere.service_restart my.esxi.host root bad-password 'ntpd'

        # Used for connecting to a vCenter Server
        salt '*' vsphere.service_restart my.vcenter.location root bad-password 'ntpd' \
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
    valid_services = [
        "DCUI",
        "TSM",
        "SSH",
        "ssh",
        "lbtd",
        "lsassd",
        "lwiod",
        "netlogond",
        "ntpd",
        "sfcbd-watchdog",
        "snmpd",
        "vprobed",
        "vpxa",
        "xorg",
    ]
    ret = {}

    # Don't require users to know that VMware lists the ssh service as TSM-SSH
    if service_name == "SSH" or service_name == "ssh":
        temp_service_name = "TSM-SSH"
    else:
        temp_service_name = service_name

    for host_name in host_names:
        # Check if the service_name provided is a valid one.
        # If we don't have a valid service, return. The service will be invalid for all hosts.
        if service_name not in valid_services:
            ret.update(
                {host_name: {"Error": "{} is not a valid service name.".format(service_name)}}
            )
            return ret

        host_ref = _get_host_ref(service_instance, host, host_name=host_name)
        service_manager = _get_service_manager(host_ref)
        log.debug("Restarting the '{}' service on {}.".format(service_name, host_name))

        # Restart the service.
        try:
            service_manager.RestartService(id=temp_service_name)
        except vim.fault.HostConfigFault as err:
            msg = "'vsphere.service_restart' failed for host {}: {}".format(host_name, err)
            log.debug(msg)
            ret.update({host_name: {"Error": msg}})
            continue
        # Some services are restricted by the vSphere License Level.
        except vim.fault.RestrictedVersion as err:
            log.debug(err)
            ret.update({host_name: {"Error": err}})
            continue

        ret.update({host_name: {"Service Restarted": True}})

    return ret


def set_service_policy(
    host,
    username,
    password,
    service_name,
    service_policy,
    protocol=None,
    port=None,
    host_names=None,
    verify_ssl=True,
):
    """
    Set the service name's policy for a given host or list of hosts.

    host
        The location of the host.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    service_name
        The name of the service for which to set the policy. Supported service names are:
          - DCUI
          - TSM
          - SSH
          - lbtd
          - lsassd
          - lwiod
          - netlogond
          - ntpd
          - sfcbd-watchdog
          - snmpd
          - vprobed
          - vpxa
          - xorg

    service_policy
        The policy to set for the service. For example, 'automatic'.

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    host_names
        List of ESXi host names. When the host, username, and password credentials
        are provided for a vCenter Server, the host_names argument is required to tell
        vCenter the hosts for which to set the service policy.

        If host_names is not provided, the service policy information will be retrieved
        for the ``host`` location instead. This is useful for when service instance
        connection information is used for a single ESXi host.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        # Used for single ESXi host connection information
        salt '*' vsphere.set_service_policy my.esxi.host root bad-password 'ntpd' 'automatic'

        # Used for connecting to a vCenter Server
        salt '*' vsphere.set_service_policy my.vcenter.location root bad-password 'ntpd' 'automatic' \
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
    valid_services = [
        "DCUI",
        "TSM",
        "SSH",
        "ssh",
        "lbtd",
        "lsassd",
        "lwiod",
        "netlogond",
        "ntpd",
        "sfcbd-watchdog",
        "snmpd",
        "vprobed",
        "vpxa",
        "xorg",
    ]
    ret = {}

    for host_name in host_names:
        # Check if the service_name provided is a valid one.
        # If we don't have a valid service, return. The service will be invalid for all hosts.
        if service_name not in valid_services:
            ret.update(
                {host_name: {"Error": "{} is not a valid service name.".format(service_name)}}
            )
            return ret

        host_ref = _get_host_ref(service_instance, host, host_name=host_name)
        service_manager = _get_service_manager(host_ref)
        services = host_ref.configManager.serviceSystem.serviceInfo.service

        # Services are stored in a general list - we need loop through the list and find
        # service key that matches our service name.
        for service in services:
            service_key = None

            # Find the service key based on the given service_name
            if service.key == service_name:
                service_key = service.key
            elif service_name == "ssh" or service_name == "SSH":
                if service.key == "TSM-SSH":
                    service_key = "TSM-SSH"

            # If we have a service_key, we've found a match. Update the policy.
            if service_key:
                try:
                    service_manager.UpdateServicePolicy(id=service_key, policy=service_policy)
                except vim.fault.NotFound:
                    msg = "The service name '{}' was not found.".format(service_name)
                    log.debug(msg)
                    ret.update({host_name: {"Error": msg}})
                    continue
                # Some services are restricted by the vSphere License Level.
                except vim.fault.HostConfigFault as err:
                    msg = "'vsphere.set_service_policy' failed for host {}: {}".format(
                        host_name, err
                    )
                    log.debug(msg)
                    ret.update({host_name: {"Error": msg}})
                    continue

                ret.update({host_name: True})

            # If we made it this far, something else has gone wrong.
            if ret.get(host_name) is None:
                msg = "Could not find service '{}' for host '{}'.".format(service_name, host_name)
                log.debug(msg)
                ret.update({host_name: {"Error": msg}})

    return ret


def get_service_policy(
    host,
    username,
    password,
    service_name,
    protocol=None,
    port=None,
    host_names=None,
    verify_ssl=True,
):
    """
    Get the service name's policy for a given host or list of hosts.

    host
        The location of the host.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    service_name
        The name of the service for which to retrieve the policy. Supported service names are:
          - DCUI
          - TSM
          - SSH
          - lbtd
          - lsassd
          - lwiod
          - netlogond
          - ntpd
          - sfcbd-watchdog
          - snmpd
          - vprobed
          - vpxa
          - xorg

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    host_names
        List of ESXi host names. When the host, username, and password credentials
        are provided for a vCenter Server, the host_names argument is required to tell
        vCenter the hosts for which to get service policy information.

        If host_names is not provided, the service policy information will be retrieved
        for the ``host`` location instead. This is useful for when service instance
        connection information is used for a single ESXi host.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        # Used for single ESXi host connection information
        salt '*' vsphere.get_service_policy my.esxi.host root bad-password 'ssh'

        # Used for connecting to a vCenter Server
        salt '*' vsphere.get_service_policy my.vcenter.location root bad-password 'ntpd' \
        host_names='[esxi-1.host.com, esxi-2.host.com]'
    """
    service_instance = salt.utils.vmware.get_service_instance(
        host=host,
        username=username,
        password=password,
        protocol=protocol,
        port=port,
        verify_ssl=verify_ssl,
    )
    valid_services = [
        "DCUI",
        "TSM",
        "SSH",
        "ssh",
        "lbtd",
        "lsassd",
        "lwiod",
        "netlogond",
        "ntpd",
        "sfcbd-watchdog",
        "snmpd",
        "vprobed",
        "vpxa",
        "xorg",
    ]
    host_names = _check_hosts(service_instance, host, host_names)

    ret = {}
    for host_name in host_names:
        # Check if the service_name provided is a valid one.
        # If we don't have a valid service, return. The service will be invalid for all hosts.
        if service_name not in valid_services:
            ret.update(
                {host_name: {"Error": "{} is not a valid service name.".format(service_name)}}
            )
            return ret

        host_ref = _get_host_ref(service_instance, host, host_name=host_name)
        services = host_ref.configManager.serviceSystem.serviceInfo.service

        # Don't require users to know that VMware lists the ssh service as TSM-SSH
        if service_name == "SSH" or service_name == "ssh":
            temp_service_name = "TSM-SSH"
        else:
            temp_service_name = service_name

        # Loop through services until we find a matching name
        for service in services:
            if service.key == temp_service_name:
                ret.update({host_name: {service_name: service.policy}})
                # We've found a match - break out of the loop so we don't overwrite the
                # Updated host_name value with an error message.
                break
            else:
                msg = "Could not find service '{}' for host '{}'.".format(service_name, host_name)
                ret.update({host_name: {"Error": msg}})

        # If we made it this far, something else has gone wrong.
        if ret.get(host_name) is None:
            msg = "'vsphere.get_service_policy' failed for host {}.".format(host_name)
            log.debug(msg)
            ret.update({host_name: {"Error": msg}})

    return ret


def get_service_running(
    host,
    username,
    password,
    service_name,
    protocol=None,
    port=None,
    host_names=None,
    verify_ssl=True,
):
    """
    Get the service name's running state for a given host or list of hosts.

    host
        The location of the host.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    service_name
        The name of the service for which to retrieve the policy. Supported service names are:
          - DCUI
          - TSM
          - SSH
          - lbtd
          - lsassd
          - lwiod
          - netlogond
          - ntpd
          - sfcbd-watchdog
          - snmpd
          - vprobed
          - vpxa
          - xorg

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    host_names
        List of ESXi host names. When the host, username, and password credentials
        are provided for a vCenter Server, the host_names argument is required to tell
        vCenter the hosts for which to get the service's running state.

        If host_names is not provided, the service's running state will be retrieved
        for the ``host`` location instead. This is useful for when service instance
        connection information is used for a single ESXi host.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        # Used for single ESXi host connection information
        salt '*' vsphere.get_service_running my.esxi.host root bad-password 'ssh'

        # Used for connecting to a vCenter Server
        salt '*' vsphere.get_service_running my.vcenter.location root bad-password 'ntpd' \
        host_names='[esxi-1.host.com, esxi-2.host.com]'
    """
    service_instance = salt.utils.vmware.get_service_instance(
        host=host,
        username=username,
        password=password,
        protocol=protocol,
        port=port,
        verify_ssl=verify_ssl,
    )
    valid_services = [
        "DCUI",
        "TSM",
        "SSH",
        "ssh",
        "lbtd",
        "lsassd",
        "lwiod",
        "netlogond",
        "ntpd",
        "sfcbd-watchdog",
        "snmpd",
        "vprobed",
        "vpxa",
        "xorg",
    ]
    host_names = _check_hosts(service_instance, host, host_names)

    ret = {}
    for host_name in host_names:
        # Check if the service_name provided is a valid one.
        # If we don't have a valid service, return. The service will be invalid for all hosts.
        if service_name not in valid_services:
            ret.update(
                {host_name: {"Error": "{} is not a valid service name.".format(service_name)}}
            )
            return ret

        host_ref = _get_host_ref(service_instance, host, host_name=host_name)
        services = host_ref.configManager.serviceSystem.serviceInfo.service

        # Don't require users to know that VMware lists the ssh service as TSM-SSH
        if service_name == "SSH" or service_name == "ssh":
            temp_service_name = "TSM-SSH"
        else:
            temp_service_name = service_name

        # Loop through services until we find a matching name
        for service in services:
            if service.key == temp_service_name:
                ret.update({host_name: {service_name: service.running}})
                # We've found a match - break out of the loop so we don't overwrite the
                # Updated host_name value with an error message.
                break
            else:
                msg = "Could not find service '{}' for host '{}'.".format(service_name, host_name)
                ret.update({host_name: {"Error": msg}})

        # If we made it this far, something else has gone wrong.
        if ret.get(host_name) is None:
            msg = "'vsphere.get_service_running' failed for host {}.".format(host_name)
            log.debug(msg)
            ret.update({host_name: {"Error": msg}})

    return ret
