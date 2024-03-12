# Copyright 2021 VMware, Inc.
# SPDX-License: Apache-2.0
import logging
import os

import salt.exceptions
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.connect as utils_connect
import saltext.vmware.utils.esxi as utils_esxi
import saltext.vmware.utils.vsphere as utils_vmware
from salt.defaults import DEFAULT_TARGET_DELIM
from saltext.vmware.utils.connect import get_config

log = logging.getLogger(__name__)

try:
    from pyVmomi import vmodl, vim, VmomiSupport

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_esxi"

DEFAULT_EXCEPTIONS = (
    vim.fault.InvalidState,
    vim.fault.NotFound,
    vim.fault.HostConfigFault,
    vmodl.fault.InvalidArgument,
    salt.exceptions.VMwareApiError,
    vim.fault.AlreadyExists,
    vim.fault.UserNotFound,
    salt.exceptions.CommandExecutionError,
    vmodl.fault.SystemError,
    TypeError,
)


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def get_lun_ids(service_instance=None, profile=None):
    """
    Return a list of LUN (Logical Unit Number) NAA (Network Addressing Authority) IDs.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)
    """

    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )

    hosts = utils_esxi.get_hosts(service_instance=service_instance, get_all_hosts=True)
    ids = set()
    for host in hosts:
        for datastore in host.datastore:
            for extent in datastore.info.vmfs.extent:
                ids.add(extent.diskName)
    return list(ids)


def _get_capability_attribs(host):
    ret = {}
    for attrib in dir(host.capability):
        if attrib.startswith("_") or attrib.lower() == "array":
            continue
        val = getattr(host.capability, attrib)
        # Convert all pyvmomi str[], bool[] and int[] to list.
        if isinstance(val, list):
            val = list(val)
        ret.update({utils_common.camel_to_snake_case(attrib): val})
    return ret


def get_capabilities(service_instance=None, profile=None):
    """
    Return ESXi host's capability information.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)
    """
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(service_instance=service_instance, get_all_hosts=True)
    capabilities = {}
    for host in hosts:
        capabilities[host.name] = _get_capability_attribs(host)
    return capabilities


def power_state(
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    state=None,
    timeout=600,
    force=True,
    profile=None,
    service_instance=None,
):
    """
    Manage the power state of the ESXi host.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname whose power state needs to be managed (optional).

    state
        Sets the ESXi host to this power state. Valid values: "reboot", "standby", "poweron", "shutdown".

    timeout
        Timeout when transitioning power state to standby / poweron. Default: 600 seconds

    force
        Force power state transition. Default: True

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.power_state datacenter_name=dc1 cluster_name=cl1 host_name=host1 state=shutdown
    """
    ret = None
    task = None
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            if state == "reboot":
                task = h.RebootHost_Task(force)
            elif state == "standby":
                task = h.PowerDownHostToStandBy_Task(timeout, force)
            elif state == "poweron":
                task = h.PowerUpHostFromStandBy_Task(timeout)
            elif state == "shutdown":
                task = h.ShutdownHost_Task(force)
            if task:
                utils_common.wait_for_task(task, h.name, "PowerStateTask")
            ret = True
    except (vmodl.fault.NotSupported, salt.exceptions.VMwareApiError) as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def service_start(
    service_name,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Start service on the ESXi host.

    service_name
        Service that needs to be managed.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname whose power state needs to be managed (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.service_start sshd datacenter_name=dc1 cluster_name=cl1 host_name=host1
    """
    log.debug("Running vmware_esxi.service_start")
    ret = None
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )
    try:
        for host in hosts:
            host_service = host.configManager.serviceSystem
            if not host_service:
                continue
            host_service.StartService(id=service_name)
        ret = True
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def service_stop(
    service_name,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Stop service on the ESXi host.

    service_name
        Service that needs to be managed.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname whose power state needs to be managed (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.service_stop sshd datacenter_name=dc1 cluster_name=cl1 host_name=host1
    """
    log.debug("Running vmware_esxi.service_stop")
    ret = None
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )
    try:
        for host in hosts:
            host_service = host.configManager.serviceSystem
            if not host_service:
                continue
            host_service.StopService(id=service_name)
        ret = True
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def service_restart(
    service_name,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Restart service on the ESXi host.

    service_name
        Service that needs to be managed.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname whose power state needs to be managed (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.service_restart sshd datacenter_name=dc1 cluster_name=cl1 host_name=host1
    """
    log.debug("Running vmware_esxi.service_restart")
    ret = None
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )
    try:
        for host in hosts:
            host_service = host.configManager.serviceSystem
            if not host_service:
                continue
            host_service.RestartService(id=service_name)
        ret = True
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def service_policy(
    service_name,
    startup_policy,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Manage service policy on the ESXi host.

    service_name
        Service that needs to be managed.

    startup_policy
        Valid values "on", "off", "automatic".
        - on: Start and stop with host
        - off: Start and stop manually
        - automatic: Start automatically if any ports are open, and stop when all ports are closed

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname whose power state needs to be managed (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.service_restart sshd datacenter_name=dc1 cluster_name=cl1 host_name=host1
    """
    log.debug("Running vmware_esxi.service_restart")
    ret = None
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )
    try:
        for host in hosts:
            host_service = host.configManager.serviceSystem
            if not host_service:
                continue
            if startup_policy is True:
                startup_policy = "on"
            elif startup_policy is False:
                startup_policy = "off"
            host_service.UpdateServicePolicy(id=service_name, policy=startup_policy)
        ret = True
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def get_service_policy(
    service_name,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    .. versionadded:: 23.4.4.0rc1

    Get the service name's policy for a given host or list of hosts.

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

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname whose power state needs to be managed (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_esxi.get_service_policy 'ssh'

    """
    log.debug("Running vmware_esxi.get_service_policy")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
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

    for host in hosts:
        # Check if the service_name provided is a valid one.
        # If we don't have a valid service, return. The service will be invalid for all hosts.
        if service_name not in valid_services:
            ret.update(
                {host_name: {"Error": "{} is not a valid service name.".format(service_name)}}
            )
            return ret

        services = host.configManager.serviceSystem.serviceInfo.service

        # Don't require users to know that VMware lists the ssh service as TSM-SSH
        if service_name == "SSH" or service_name == "ssh":
            temp_service_name = "TSM-SSH"
        else:
            temp_service_name = service_name

        # Loop through services until we find a matching name
        for service in services:
            if service.key == temp_service_name:
                ret.update({host.name: {service_name: service.policy}})
                # We've found a match - break out of the loop so we don't overwrite the
                # Updated host.name value with an error message.
                break
            else:
                msg = "Could not find service '{}' for host '{}'.".format(service_name, host.name)
                ret.update({host.name: {"Error": msg}})

        # If we made it this far, something else has gone wrong.
        if ret.get(host.name) is None:
            msg = "'vsphere.get_service_policy' failed for host {}.".format(host.name)
            log.debug(msg)
            ret.update({host.name: {"Error": msg}})

    return ret


def get_service_running(
    service_name,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    .. versionadded:: 23.4.4.0rc1

    Get the service name's running state for a given host or list of hosts.

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

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname whose power state needs to be managed (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_esxi.get_service_running 'ntpd'
    """
    log.debug("Running vmware_esxi.get_service_running")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
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
    for host in hosts:
        # Check if the service_name provided is a valid one.
        # If we don't have a valid service, return. The service will be invalid for all hosts.
        if service_name not in valid_services:
            ret.update(
                {host.name: {"Error": "{} is not a valid service name.".format(service_name)}}
            )
            return ret

        services = host.configManager.serviceSystem.serviceInfo.service

        # Don't require users to know that VMware lists the ssh service as TSM-SSH
        if service_name == "SSH" or service_name == "ssh":
            temp_service_name = "TSM-SSH"
        else:
            temp_service_name = service_name

        # Loop through services until we find a matching name
        for service in services:
            if service.key == temp_service_name:
                ret.update({host.name: {service_name: service.running}})
                # We've found a match - break out of the loop so we don't overwrite the
                # Updated host.name value with an error message.
                break
            else:
                msg = "Could not find service '{}' for host '{}'.".format(service_name, host.name)
                ret.update({host.name: {"Error": msg}})

        # If we made it this far, something else has gone wrong.
        if ret.get(host.name) is None:
            msg = "'vsphere.get_service_running' failed for host {}.".format(host.name)
            log.debug(msg)
            ret.update({host.name: {"Error": msg}})

    return ret


def list_services(
    service_name=None,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    state=None,
    startup_policy=None,
    service_instance=None,
    profile=None,
):
    """
    List the state of services running on matching ESXi hosts.

    service_name
        Filter by this service name. (optional)

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    state
        Filter by this service state. Valid values: "running", "stopped"

    startup_policy
        Filter by this service startup policy. Valid values "on", "off", "automatic".

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.list_services
    """
    log.debug("Running vmware_esxi.list_services")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            host_service = h.configManager.serviceSystem
            ret[h.name] = {}
            if not host_service:
                continue
            if startup_policy is not None:
                # salt converts command line input "on" and "off" to True and False. Handle explicitly.
                if startup_policy is True:
                    startup_policy = "on"
                elif startup_policy is False:
                    startup_policy = "off"
            services = host_service.serviceInfo.service
            for service in services or []:
                if service_name and service.key != service_name:
                    continue
                if startup_policy and service.policy != startup_policy:
                    continue
                if state and state == "running" and not service.running:
                    continue
                if state and state == "stopped" and service.running:
                    continue
                ret[h.name][service.key] = {
                    "state": "running" if service.running else "stopped",
                    "startup_policy": service.policy,
                }
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def get_acceptance_level(
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    acceptance_level=None,
    service_instance=None,
    profile=None,
):
    """
    Get acceptance level on matching ESXi hosts.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    acceptance_level
        Filter by this acceptance level. Valid values: "community", "partner", "vmware_accepted", "vmware_certified". (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.get_acceptance_level

    Returns:

    .. code-block:: json

        {
            "host1": "partner",
            "host2": "partner"
        }

    """

    log.debug("Running vmware_esxi.get_acceptance_level")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            host_config_manager = h.configManager.imageConfigManager
            if not host_config_manager:
                continue
            host_acceptance_level = host_config_manager.HostImageConfigGetAcceptance()
            if acceptance_level and host_acceptance_level != acceptance_level:
                continue
            ret[h.name] = host_acceptance_level
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def set_acceptance_level(
    acceptance_level,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Set acceptance level on matching ESXi hosts.

    acceptance_level
        Set to this acceptance level. Valid values: "community", "partner", "vmware_accepted", "vmware_certified".

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.set_acceptance_level

    Returns:

    .. code-block:: json

        {
            "host1": "partner",
            "host2": "partner"
        }

    """

    log.debug("Running vmware_esxi.set_acceptance_level")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            host_config_manager = h.configManager.imageConfigManager
            if not host_config_manager:
                continue
            host_config_manager.UpdateHostImageAcceptanceLevel(newAcceptanceLevel=acceptance_level)
            ret[h.name] = acceptance_level
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def get_advanced_config(
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    config_name=None,
    service_instance=None,
    profile=None,
):
    """
    Get advanced config on matching ESXi hosts.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    config_name
        Filter by this config_name. (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.get_advanced_config
    """
    log.debug("Running vmware_esxi.get_advanced_config")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            config_manager = h.configManager.advancedOption
            ret[h.name] = (
                {}
                if not config_manager
                else {data.key: data.value for data in config_manager.QueryOptions(config_name)}
            )

    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def set_advanced_configs(
    config_dict,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Set multiple advanced configurations on matching ESXi hosts.

    config_dict
        Set the configuration key to the configuration value. Eg: {"Annotations.WelcomeMessage": "Hello"}

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.set_advanced_config config_name=Annotations.WelcomeMessage config_value=Hello

    Returns:

    .. code-block:: json

        {
            "host1": {
                "Annotations.WelcomeMessage": "HelloDemo"
            },
        }

    """
    log.debug("Running vmware_esxi.set_advanced_configs")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            config_manager = h.configManager.advancedOption
            ret[h.name] = {}
            if not config_manager:
                continue

            supported_configs = {}
            for opt in config_manager.supportedOption:
                if opt.key not in config_dict:
                    continue
                supported_configs[opt.key] = opt.optionType

            advanced_configs = []
            for opt in config_dict:
                opt_type = supported_configs[opt]
                val = config_dict[opt]
                if isinstance(opt_type, vim.option.BoolOption) and not isinstance(val, bool):
                    val = val.lower() == "true"
                elif isinstance(opt_type, vim.option.LongOption):
                    val = VmomiSupport.vmodlTypes["long"](val)
                elif isinstance(opt_type, vim.option.IntOption):
                    val = VmomiSupport.vmodlTypes["int"](val)
                advanced_configs.append(vim.option.OptionValue(key=opt, value=val))
                ret[h.name][opt] = config_dict[opt]
            config_manager.UpdateOptions(changedValue=advanced_configs)
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def set_advanced_config(
    config_name,
    config_value,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Set a single advanced configuration on matching ESXi hosts.

    config_name
        Name of the advanced configuration to be set.

    config_value
        Set the advanced configuration to this value.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.set_advanced_config config_name=Annotations.WelcomeMessage config_value=Hello

    Returns:

    .. code-block:: json

        {
            "host1": {
                "Annotations.WelcomeMessage": "HelloDemo"
            },
        }

    """
    log.debug("Running vmware_esxi.set_advanced_config")
    return set_advanced_configs(
        config_dict={config_name: config_value},
        datacenter_name=datacenter_name,
        cluster_name=cluster_name,
        host_name=host_name,
        service_instance=service_instance,
        profile=profile,
    )


def get_all_firewall_configs(
    datacenter_name=None, cluster_name=None, host_name=None, service_instance=None, profile=None
):
    """
    Get Firewall configurations on matching ESXi hosts.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.get_all_firewall_configs
    """
    log.debug("Running vmware_esxi.get_all_firewall_configs")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            firewall_config = h.configManager.firewallSystem
            if not firewall_config:
                continue
            for ruleset in firewall_config.firewallInfo.ruleset:
                ret.setdefault(h.name, []).append(
                    {
                        "allowed_hosts": {
                            "ip_address": list(ruleset.allowedHosts.ipAddress),
                            "all_ip": ruleset.allowedHosts.allIp,
                            "ip_network": [
                                "{}/{}".format(ip.network, ip.prefixLength)
                                for ip in ruleset.allowedHosts.ipNetwork
                            ],
                        },
                        "key": ruleset.key,
                        "service": ruleset.service,
                        "enabled": ruleset.enabled,
                        "rule": [
                            {
                                "port": r.port,
                                "end_port": r.endPort,
                                "direction": r.direction,
                                "port_type": r.portType,
                                "protocol": r.protocol,
                            }
                            for r in ruleset.rule
                        ],
                    }
                )
        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def get_firewall_config(
    ruleset_name,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Get Firewall a rule configuration on matching ESXi hosts.

    ruleset_name
        Name of firewall rule.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.get_firewall_config
    """
    log.debug("Running vmware_esxi.get_firewall_config")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            firewall_config = h.configManager.firewallSystem
            if not firewall_config:
                continue
            for ruleset in firewall_config.firewallInfo.ruleset:
                if ruleset_name == ruleset.key:
                    ret.setdefault(h.name, []).append(
                        {
                            "allowed_hosts": {
                                "ip_address": list(ruleset.allowedHosts.ipAddress),
                                "all_ip": ruleset.allowedHosts.allIp,
                                "ip_network": [
                                    "{}/{}".format(ip.network, ip.prefixLength)
                                    for ip in ruleset.allowedHosts.ipNetwork
                                ],
                            },
                            "key": ruleset.key,
                            "service": ruleset.service,
                            "enabled": ruleset.enabled,
                            "rule": [
                                {
                                    "port": r.port,
                                    "end_port": r.endPort,
                                    "direction": r.direction,
                                    "port_type": r.portType,
                                    "protocol": r.protocol,
                                }
                                for r in ruleset.rule
                            ],
                        }
                    )
        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def set_firewall_config(
    firewall_config,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Set Firewall rule configuration on matching ESXi hosts.

    firewall_config
        Dict of Rule set to be used to change Firewall configuration. Eg: {"name": "CIMHttpServer"}

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.set_firewall_config
    """
    log.debug("Running vmware_esxi.set_firewall_config")
    ret = []
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )
    try:
        for host in hosts:
            firewall = host.configManager.firewallSystem
            if not firewall:
                continue
            firewall_rulespec = vim.host.Ruleset.RulesetSpec()
            firewall_rulespec.allowedHosts = vim.host.Ruleset.IpList()
            if "enabled" in firewall_config and firewall_config["enabled"]:
                firewall.EnableRuleset(id=firewall_config["name"])
            else:
                firewall.DisableRuleset(id=firewall_config["name"])
            if "allowed_hosts" in firewall_config:
                if "all_ip" in firewall_config["allowed_hosts"]:
                    firewall_rulespec.allowedHosts.allIp = firewall_config["allowed_hosts"][
                        "all_ip"
                    ]
                if "ip_address" in firewall_config["allowed_hosts"]:
                    firewall_rulespec.allowedHosts.ipAddress = list(
                        firewall_config["allowed_hosts"]["ip_address"]
                    )
                firewall_rulespec.allowedHosts.ipNetwork = []
                if "ip_network" in firewall_config["allowed_hosts"]:
                    for network in firewall_config["allowed_hosts"]["ip_network"]:
                        address, mask = network.split("/")
                        tmp_ip_network_spec = vim.host.Ruleset.IpNetwork()
                        tmp_ip_network_spec.network = address
                        tmp_ip_network_spec.prefixLength = int(mask)
                        firewall_rulespec.allowedHosts.ipNetwork.append(tmp_ip_network_spec)
                firewall.UpdateRuleset(id=firewall_config["name"], spec=firewall_rulespec)
            res = get_firewall_config(
                firewall_config["name"], host_name=host.name, service_instance=service_instance
            )
            ret.append(res)
        return ret

    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def set_all_firewall_configs(
    firewall_configs,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
):
    """
    Set Firewall rule configurations on matching ESXi hosts.

    firewall_configs
        List of Rule sets to be used to change Firewall configuration. Eg: [{"name": "CIMHttpServer"},{"name":"DHCPv6"}]

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.set_all_firewall_configs
    """
    log.debug("Running vmware_esxi.set_all_firewall_configs")
    ret = []
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )
    for host in hosts:
        for rule_set in enumerate(list(firewall_configs)):
            res = set_firewall_config(
                rule_set[1], host_name=host.name, service_instance=service_instance
            )
            ret.append(res)
    return ret


def backup_config(
    push_file_to_master=False,
    http_opts=None,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Backup configuration for matching ESXi hosts.

    push_file_to_master
        Push the downloaded configuration file to the salt master. (optional)
        Refer: https://docs.saltproject.io/en/latest/ref/modules/all/salt.modules.cp.html#salt.modules.cp.push

    http_opts
        Extra HTTP options to be passed to download from the URL. (optional)
        Refer: https://docs.saltproject.io/en/latest/ref/modules/all/salt.modules.http.html#salt.modules.http.query

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt * vmware_esxi.backup_config host_name=203.0.113.53 http_opts='{"verify_ssl": False}'
    """
    log.debug("Running vmware_esxi.backup_config")
    ret = {}
    http_opts = http_opts or {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            try:
                url = h.configManager.firmwareSystem.BackupFirmwareConfiguration()
                url = url.replace("*", h.name)
                file_name = os.path.join(__opts__["cachedir"], url.rsplit("/", 1)[1])
                data = __salt__["http.query"](url, decode_body=False, **http_opts)
                with open(file_name, "wb") as fp:
                    fp.write(data["body"])
                if push_file_to_master:
                    __salt__["cp.push"](file_name)
                ret.setdefault(h.name, {"file_name": file_name})
                ret[h.name]["url"] = url
            except salt.exceptions.CommandExecutionError as exc:
                log.error("Unable to backup configuration for host - %s. Error - %s", h.name, exc)
        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def restore_config(
    source_file,
    saltenv=None,
    http_opts=None,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Restore configuration for matching ESXi hosts.

    source_file
        Specify the source file from which the configuration is to be restored.
        The file can be either on the master, locally on the minion or url.
        E.g.: salt://vmware_config.tgz, /tmp/minion1/vmware_config.tgz or
        203.0.113.53/downloads/5220da48-552e-5779-703e-5705367bd6d6/configBundle-ESXi-190313806785.eng.vmware.com.tgz

    saltenv
        Specify the saltenv when the source file needs to be retireved from the master. (optional)

    http_opts
        Extra HTTP options to be passed to download from the URL. (optional).
        Refer: https://docs.saltproject.io/en/latest/ref/modules/all/salt.modules.http.html#salt.modules.http.query

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.backup_config datacenter_name=dc1 host_name=host1
    """
    log.debug("Running vmware_esxi.backup_config")
    ret = {}
    http_opts = http_opts or {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    for h in hosts:
        try:
            data = None
            url = h.configManager.firmwareSystem.QueryFirmwareConfigUploadURL().replace("*", h.name)
            if source_file.startswith("salt://"):
                cached = __salt__["cp.cache_file"](source_file, saltenv=saltenv)
                with open(cached, "rb") as fp:
                    data = fp.read()
            elif source_file.startswith("http"):
                data = __salt__["http.query"](url, decode_body=False, **http_opts)
            else:
                with open(source_file, "rb") as fp:
                    data = fp.read()
            conf = get_config(esxi_host=h.name, config=__opts__, profile=profile)
            resp = __salt__["http.query"](
                url,
                data=data,
                method="PUT",
                username=conf["user"],
                password=conf["password"],
                **http_opts,
            )
            if "error" in resp:
                ret[h.name] = resp["error"]
                continue
            if not h.runtime.inMaintenanceMode:
                log.debug("Host - %s entering maintenance mode", h.name)
                utils_common.wait_for_task(
                    h.EnterMaintenanceMode_Task(timeout=60), h.name, "EnterMaintenanceMode"
                )
            h.configManager.firmwareSystem.RestoreFirmwareConfiguration(force=False)
            ret[h.name] = True
        except Exception as exc:
            msg = "Unable to restore configuration for host - {}. Error - {}".format(h.name, exc)
            log.error(msg)
            ret[h.name] = msg
            if h.runtime.inMaintenanceMode:
                log.debug("Host - %s exiting maintenance mode", h.name)
                utils_common.wait_for_task(
                    h.ExitMaintenanceMode_Task(timeout=60), h.name, "ExitMaintenanceMode"
                )

    return ret


def reset_config(
    datacenter_name=None, cluster_name=None, host_name=None, service_instance=None, profile=None
):
    """
    Reset configuration for matching ESXi hosts.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.reset_config
    """
    log.debug("Running vmware_esxi.reset_config")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    for h in hosts:
        try:
            if not h.runtime.inMaintenanceMode:
                log.debug("Host - %s entering maintenance mode", h.name)
                utils_common.wait_for_task(
                    h.EnterMaintenanceMode_Task(timeout=60), h.name, "EnterMaintenanceMode"
                )
            h.configManager.firmwareSystem.ResetFirmwareToFactoryDefaults()
            ret[h.name] = True
        except vmodl.fault.HostCommunication as exc:
            msg = "Unable to reach host - {}. Error - {}".format(h.name, str(exc))
            ret[h.name] = msg
            log.error(msg)
        except Exception as exc:
            msg = "Unable to reset configuration for host - {}. Error - {}".format(h.name, str(exc))
            ret[h.name] = msg
            log.error(msg)
            log.debug("Host - %s exiting maintenance mode", h.name)
            utils_common.wait_for_task(
                h.ExitMaintenanceMode_Task(timeout=60), h.name, "ExitMaintenanceMode"
            )
    return ret


def get_dns_config(
    datacenter_name=None, cluster_name=None, host_name=None, service_instance=None, profile=None
):
    """
    Get DNS configuration on matching ESXi hosts.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.get_dns_config
    """
    log.debug("Running vmware_esxi.get_dns_config")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            dns_config = h.config.network.dnsConfig
            if not dns_config:
                continue
            ret[h.name] = {}
            ret[h.name]["dhcp"] = dns_config.dhcp
            ret[h.name]["virtual_nic"] = dns_config.virtualNicDevice
            ret[h.name]["host_name"] = dns_config.hostName
            ret[h.name]["domain_name"] = dns_config.domainName
            ret[h.name]["ip"] = list(dns_config.address)
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))
    return ret


def get_ntp_config(
    datacenter_name=None, cluster_name=None, host_name=None, service_instance=None, profile=None
):
    """
    Get NTP configuration on matching ESXi hosts.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.get_ntp_config
    """
    log.debug("Running vmware_esxi.get_ntp_config")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            ntp_config = h.configManager.dateTimeSystem
            if ntp_config:
                ret[h.name] = {
                    "time_zone": ntp_config.dateTimeInfo.timeZone.key,
                    "time_zone_name": ntp_config.dateTimeInfo.timeZone.name,
                    "time_zone_description": ntp_config.dateTimeInfo.timeZone.description,
                    "time_zone_gmt_offset": ntp_config.dateTimeInfo.timeZone.gmtOffset,
                    "ntp_servers": list(ntp_config.dateTimeInfo.ntpConfig.server),
                    "ntp_config_file": list(ntp_config.dateTimeInfo.ntpConfig.configFile)
                    if ntp_config.dateTimeInfo.ntpConfig.configFile
                    else None,
                }
        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def set_ntp_config(
    ntp_servers,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Set NTP configuration on matching ESXi hosts.

    ntp_servers
        A list of servers that should be added to and configured for the specified
        host's NTP configuration.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    CLI Example:
    .. code-block:: bash

        salt '*' vmware_esxi.set_ntp_config '[192.174.1.100, 192.174.1.200]'
    """
    log.debug("Running vmware_esxi.set_ntp_config")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )

    if not isinstance(ntp_servers, list):
        raise salt.exceptions.CommandExecutionError("'ntp_servers' must be a list.")

    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for host in hosts:
            date_time_manager = host.configManager.dateTimeSystem

            ntp_config = vim.host.NtpConfig()
            ntp_config.server = ntp_servers
            date_config_spec = vim.host.DateTimeConfig()
            date_config_spec.ntpConfig = ntp_config

            date_time_manager.UpdateDateTimeConfig(date_config_spec)
            ret[host.name] = True

        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def list_hosts(
    datacenter_name=None, cluster_name=None, host_name=None, service_instance=None, profile=None
):
    """
    List ESXi hosts.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.list_hosts
    """
    log.debug("Running vmware_esxi.list_hosts")
    ret = []
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            ret.append(h.name)
        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def add_user(
    user_name,
    password,
    description=None,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Add local user on matching ESXi hosts.

    user_name
        User to create on matching ESXi hosts. (required).

    password
        Password for the new user. (required).

    description
        Description for the new user. (optional).

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.add_user user_name=foo password=bar@123 descripton="new user"
    """
    log.debug("Running vmware_esxi.add_user")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            account_spec = vim.host.LocalAccountManager.AccountSpecification()
            account_spec.id = user_name
            account_spec.password = password
            account_spec.description = description
            h.configManager.accountManager.CreateUser(account_spec)
            ret[h.name] = True
        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def update_user(
    user_name,
    password,
    description=None,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Update local user on matching ESXi hosts.

    user_name
        Existing user to update on matching ESXi hosts. (required).

    password
        New Password for the existing user. (required).

    description
        New description for the existing user. (optional).

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.update_user user_name=foo password=bar@123 descripton="existing user"
    """
    log.debug("Running vmware_esxi.update_user")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for host in hosts:
            account_spec = vim.host.LocalAccountManager.AccountSpecification()
            account_spec.id = user_name
            account_spec.password = password
            account_spec.description = description
            host.configManager.accountManager.UpdateUser(account_spec)
            ret[host.name] = True
        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def remove_user(
    user_name,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Remove local user on matching ESXi hosts.

    user_name
        User to delete on matching ESXi hosts. (required).

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.remove_user user_name=foo
    """
    log.debug("Running vmware_esxi.remove_user")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            h.configManager.accountManager.RemoveUser(user_name)
            ret[h.name] = True
        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def get_user(
    user_name,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Get local user on matching ESXi hosts.

    user_name
        User to delete on matching ESXi hosts. (required).

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.get_user user_name=foo
    """
    log.debug("Running vmware_esxi.get_user")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for host in hosts:
            user_account = host.configManager.userDirectory.RetrieveUserGroups(
                None, user_name, None, None, True, True, False
            )
            ret[host.name] = user_account
        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def _get_net_stack(network_tcpip_stack):
    return {
        "default": "defaultTcpipStack",
        "provisioning": "vSphereProvisioning",
        "vmotion": "vmotion",
        "vxlan": "vxlan",
        "defaulttcpipstack": "default",
        "vsphereprovisioning": "provisioning",
    }.get(network_tcpip_stack.lower())


def create_vmkernel_adapter(
    port_group_name,
    dvswitch_name=None,
    vswitch_name=None,
    enable_fault_tolerance=None,
    enable_management_traffic=None,
    enable_provisioning=None,
    enable_replication=None,
    enable_replication_nfc=None,
    enable_vmotion=None,
    enable_vsan=None,
    mtu=1500,
    network_default_gateway=None,
    network_ip_address=None,
    network_subnet_mask=None,
    network_tcp_ip_stack="default",
    network_type="static",
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Create VMKernel Adapter on matching ESXi hosts.

    port_group_name
        The name of the port group for the VMKernel interface. (required).

    dvswitch_name
        The name of the vSphere Distributed Switch (vDS) where to add the VMKernel interface.
        One of dvswitch_name or vswitch_name is required.

    vswitch_name
        The name of the vSwitch where to add the VMKernel interface.
        One of dvswitch_name or vswitch_name is required.

    enable_fault_tolerance
        Enable Fault Tolerance traffic on the VMKernel adapter. Valid values: True, False.

    enable_management_traffic
        Enable Management traffic on the VMKernel adapter. Valid values: True, False.

    enable_provisioning
        Enable Provisioning traffic on the VMKernel adapter. Valid values: True, False.

    enable_replication
        Enable vSphere Replication traffic on the VMKernel adapter. Valid values: True, False.

    enable_replication_nfc
        Enable vSphere Replication NFC traffic on the VMKernel adapter. Valid values: True, False.

    enable_vmotion
        Enable vMotion traffic on the VMKernel adapter. Valid values: True, False.

    enable_vsan
        Enable VSAN traffic on the VMKernel adapter. Valid values: True, False.

    mtu
        The MTU for the VMKernel interface.

    network_default_gateway
        Default gateway (Override default gateway for this adapter).

    network_type
        Type of IP assignment. Valid values: "static", "dhcp".

    network_ip_address
        Static IP address. Required if type = 'static'.

    network_subnet_mask
        Static netmask required. Required if type = 'static'.

    network_tcpip_stack
        The TCP/IP stack for the VMKernel interface. Valid values: "default", "provisioning", "vmotion", "vxlan".

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.create_vmkernel_adapter port_group_name=portgroup1 dvswitch_name=dvs1
    """
    log.debug("Running vmware_esxi.create_vmkernel_adapter")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            vmk_device = _save_vmkernel_adapter(
                host=h,
                service_instance=service_instance,
                action="create",
                port_group_name=port_group_name,
                dvswitch_name=dvswitch_name,
                vswitch_name=vswitch_name,
                adapter_name=None,
                enable_fault_tolerance=enable_fault_tolerance,
                enable_management_traffic=enable_management_traffic,
                enable_provisioning=enable_provisioning,
                enable_replication=enable_replication,
                enable_replication_nfc=enable_replication_nfc,
                enable_vmotion=enable_vmotion,
                enable_vsan=enable_vsan,
                mtu=mtu,
                network_default_gateway=network_default_gateway,
                network_ip_address=network_ip_address,
                network_subnet_mask=network_subnet_mask,
                network_tcp_ip_stack=network_tcp_ip_stack,
                network_type=network_type,
            )
            ret[h.name] = vmk_device
        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def _save_vmkernel_adapter(
    host,
    service_instance,
    action,
    port_group_name,
    dvswitch_name,
    vswitch_name,
    adapter_name,
    enable_fault_tolerance,
    enable_management_traffic,
    enable_provisioning,
    enable_replication,
    enable_replication_nfc,
    enable_vmotion,
    enable_vsan,
    mtu,
    network_default_gateway,
    network_ip_address,
    network_subnet_mask,
    network_tcp_ip_stack,
    network_type,
):
    vnic_config = vim.host.VirtualNic.Specification()
    ip_spec = vim.host.IpConfig()
    if network_type == "dhcp":
        ip_spec.dhcp = True
    else:
        ip_spec.dhcp = False
        ip_spec.ipAddress = network_ip_address
        ip_spec.subnetMask = network_subnet_mask
        if network_default_gateway:
            vnic_config.ipRouteSpec = vim.host.VirtualNic.IpRouteSpec()
            vnic_config.ipRouteSpec.ipRouteConfig = vim.host.IpRouteConfig()
            vnic_config.ipRouteSpec.ipRouteConfig.defaultGateway = network_default_gateway
    vnic_config.ip = ip_spec
    vnic_config.mtu = mtu
    vnic_config.netStackInstanceKey = _get_net_stack(network_tcp_ip_stack)
    port_group = None
    if dvswitch_name:
        vnic_config.distributedVirtualPort = vim.dvs.PortConnection()
        dvs = utils_vmware._get_dvs(service_instance, dvswitch_name)
        port_group = utils_vmware._get_dvs_portgroup(dvs=dvs, portgroup_name=port_group_name)
        vnic_config.distributedVirtualPort.switchUuid = dvs.uuid
        vnic_config.distributedVirtualPort.portgroupKey = port_group.key

    vnic = vmk_device = None
    if action == "update":
        for v in host.config.network.vnic:
            if v.device == adapter_name:
                vnic = v
                vmk_device = vnic.device
                break
        host.configManager.networkSystem.UpdateVirtualNic(vmk_device, vnic_config)
    else:
        vmk_device = host.configManager.networkSystem.AddVirtualNic(
            portgroup="" if dvswitch_name else port_group_name, nic=vnic_config
        )

    for enable, service in [
        (enable_management_traffic, "management"),
        (enable_fault_tolerance, "faultToleranceLogging"),
        (enable_provisioning, "vSphereProvisioning"),
        (enable_replication, "vSphereReplication"),
        (enable_replication_nfc, "vSphereReplicationNFC"),
        (enable_vmotion, "vmotion"),
    ]:
        if enable:
            host.configManager.virtualNicManager.SelectVnicForNicType(service, vmk_device)
        elif enable is False:
            host.configManager.virtualNicManager.DeselectVnicForNicType(service, vmk_device)

    vsan_config = vim.vsan.host.ConfigInfo()
    vsan_config.networkInfo = host.configManager.vsanSystem.config.networkInfo
    current_vsan_vnics = [
        portConfig.device for portConfig in host.configManager.vsanSystem.config.networkInfo.port
    ]
    if enable_vsan:
        if vmk_device not in current_vsan_vnics:
            vsan_port_config = vim.vsan.host.ConfigInfo.NetworkInfo.PortConfig()
            vsan_port_config.device = vmk_device
            if vsan_config.networkInfo is None:
                vsan_config.networkInfo = vim.vsan.host.ConfigInfo.NetworkInfo()
                vsan_config.networkInfo.port = [vsan_port_config]
            else:
                vsan_config.networkInfo.port.append(vsan_port_config)
    elif enable_vsan is False and vmk_device in current_vsan_vnics:
        vsan_config.networkInfo.port = list(
            filter(lambda portConfig: portConfig.device != vmk_device, vsan_config.networkInfo.port)
        )
    task = host.configManager.vsanSystem.UpdateVsan_Task(vsan_config)
    utils_common.wait_for_task(task, host.name, "UpdateVsan_Task")
    return vmk_device


def get_vmkernel_adapters(
    adapter_name=None,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Update VMKernel Adapter on matching ESXi hosts.

    adapter_name
        Filter by this vmkernel adapter name.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.get_vmkernel_adapter port_group_name=portgroup1
    """
    log.debug("Running vmware_esxi.get_vmkernel_adapter")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            vmk_devices = []
            for v in h.config.network.vnic:
                if adapter_name and v.device != adapter_name:
                    continue
                vmk_devices.append(v.device)
            ret[h.name] = vmk_devices
        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def update_vmkernel_adapter(
    adapter_name,
    port_group_name,
    dvswitch_name=None,
    vswitch_name=None,
    enable_fault_tolerance=None,
    enable_management_traffic=None,
    enable_provisioning=None,
    enable_replication=None,
    enable_replication_nfc=None,
    enable_vmotion=None,
    enable_vsan=None,
    mtu=1500,
    network_default_gateway=None,
    network_ip_address=None,
    network_subnet_mask=None,
    network_tcp_ip_stack="default",
    network_type="static",
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Update VMKernel Adapter on matching ESXi hosts.

    adapter_name
        The name of the VMKernel interface to update. (required).

    port_group_name
        The name of the port group for the VMKernel interface. (required).

    dvswitch_name
        The name of the vSphere Distributed Switch (vDS) where to update the VMKernel interface.

    vswitch_name
        The name of the vSwitch where to update the VMKernel interface.

    enable_fault_tolerance
        Enable Fault Tolerance traffic on the VMKernel adapter. Valid values: True, False.

    enable_management_traffic
        Enable Management traffic on the VMKernel adapter. Valid values: True, False.

    enable_provisioning
        Enable Provisioning traffic on the VMKernel adapter. Valid values: True, False.

    enable_replication
        Enable vSphere Replication traffic on the VMKernel adapter. Valid values: True, False.

    enable_replication_nfc
        Enable vSphere Replication NFC traffic on the VMKernel adapter. Valid values: True, False.

    enable_vmotion
        Enable vMotion traffic on the VMKernel adapter. Valid values: True, False.

    enable_vsan
        Enable VSAN traffic on the VMKernel adapter. Valid values: True, False.

    mtu
        The MTU for the VMKernel interface.

    network_default_gateway
        Default gateway (Override default gateway for this adapter).

    network_type
        Type of IP assignment. Valid values: "static", "dhcp".

    network_ip_address
        Static IP address. Required if type = 'static'.

    network_subnet_mask
        Static netmask required. Required if type = 'static'.

    network_tcpip_stack
        The TCP/IP stack for the VMKernel interface. Valid values: "default", "provisioning", "vmotion", "vxlan".

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.update_vmkernel_adapter dvswitch_name=dvs1 mtu=2000
    """
    log.debug("Running vmware_esxi.update_vmkernel_adapter")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            ret[h.name] = _save_vmkernel_adapter(
                host=h,
                service_instance=service_instance,
                action="update",
                port_group_name=port_group_name,
                dvswitch_name=dvswitch_name,
                vswitch_name=vswitch_name,
                adapter_name=adapter_name,
                enable_fault_tolerance=enable_fault_tolerance,
                enable_management_traffic=enable_management_traffic,
                enable_provisioning=enable_provisioning,
                enable_replication=enable_replication,
                enable_replication_nfc=enable_replication_nfc,
                enable_vmotion=enable_vmotion,
                enable_vsan=enable_vsan,
                mtu=mtu,
                network_default_gateway=network_default_gateway,
                network_ip_address=network_ip_address,
                network_subnet_mask=network_subnet_mask,
                network_tcp_ip_stack=network_tcp_ip_stack,
                network_type=network_type,
            )
        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def delete_vmkernel_adapter(
    adapter_name,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Delete VMKernel Adapter on matching ESXi hosts.

    adapter_name
        The name of the VMKernel Adapter to delete (required).

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.delete_vmkernel_adapter name=vmk1
    """
    log.debug("Running vmware_esxi.delete_vmkernel_adapter")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            try:
                h.configManager.networkSystem.RemoveVirtualNic(adapter_name)
                ret[h.name] = True
            except vim.fault.NotFound:
                ret[h.name] = False
        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def get_user(
    user_name,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    Get local user on matching ESXi hosts.

    user_name
        Filter by this user name (required).

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.get_user user_name=foo
    """
    log.debug("Running vmware_esxi.get_user")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            users = h.configManager.userDirectory.RetrieveUserGroups(
                searchStr=user_name,
                belongsToGroup=None,
                belongsToUser=None,
                domain=None,
                exactMatch=True,
                findUsers=True,
                findGroups=True,
            )
            for user in users:
                ret[h.name] = {
                    # user.principal is the user name
                    user.principal: {
                        "description": user.fullName,
                        "group": user.group,
                        "user_id": user.id,
                        "shell_access": user.shellAccess,
                    }
                }
        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def add_role(
    role_name,
    privilege_ids,
    esxi_host_name=None,
    service_instance=None,
):
    """
    Add local role to service instance, which may be an ESXi host or vCenter instance.

    role_name
        Role to create on service instance. (required).

    privilege_ids
        List of privileges for the role. (required).
        Refer: https://docs.vmware.com/en/VMware-vSphere/7.0/com.vmware.vsphere.security.doc/GUID-ED56F3C4-77D0-49E3-88B6-B99B8B437B62.html
        Example: ['Folder.Create', 'Folder.Delete'].

    esxi_host_name
        Connect to this ESXi host using your pillar's service_instance credentials. (optional).

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.add_role role_name=foo privileges=['Folder.Create']
    """
    log.debug("Running vmware_esxi.add_role")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__,
        profile=profile,
        esxi_host=esxi_host_name,
    )
    try:
        ret["role_id"] = service_instance.content.authorizationManager.AddAuthorizationRole(
            name=role_name, privIds=privilege_ids
        )
        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def update_role(
    role_name,
    privilege_ids,
    esxi_host_name=None,
    service_instance=None,
):
    """
    Update local role on service instance, which may be an ESXi host or vCenter instance.

    role_name
        Role to update on service instance. (required).

    privilege_ids
        List of privileges for the role. (required).
        Refer: https://docs.vmware.com/en/VMware-vSphere/7.0/com.vmware.vsphere.security.doc/GUID-ED56F3C4-77D0-49E3-88B6-B99B8B437B62.html
        Example: ['Folder.Create', 'Folder.Delete'].

    esxi_host_name
        Connect to this ESXi host using your pillar's service_instance credentials. (optional).

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.update_role role_name=foo privileges=['Folder.Create']
    """
    log.debug("Running vmware_esxi.update_role")
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__,
        profile=profile,
        esxi_host=esxi_host_name,
    )
    try:
        role = get_role(role_name=role_name, service_instance=service_instance)
        if not role:
            raise salt.exceptions.SaltException("Role {} not found".format(role_name))
        service_instance.content.authorizationManager.UpdateAuthorizationRole(
            roleId=role["role_id"], newName=role_name, privIds=privilege_ids
        )
        return True
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def remove_role(
    role_name,
    force=False,
    esxi_host_name=None,
    service_instance=None,
):
    """
    Remove local role on service instance, which may be an ESXi host or vCenter instance.

    role_name
        Role to update on service instance. (required).

    force
        Forcefully remove a role even when in use. Default False. (optional).

    esxi_host_name
        Connect to this ESXi host using your pillar's service_instance credentials. (optional).

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    .. code-block:: bash

        salt '*' vmware_esxi.remove_role role_name=foo
    """
    log.debug("Running vmware_esxi.update_role")
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__,
        profile=profile,
        esxi_host=esxi_host_name,
    )
    try:
        role = get_role(role_name=role_name, service_instance=service_instance)
        if not role:
            raise salt.exceptions.SaltException("Role {} not found".format(role_name))
        service_instance.content.authorizationManager.RemoveAuthorizationRole(
            roleId=role["role_id"], failIfUsed=force
        )
        return True
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def get_role(role_name, esxi_host_name=None, service_instance=None, profile=None):
    """
    Get local role on service instance, which may be an ESXi host or vCenter instance.

    role_name
        Retrieve this role on service instance. (required).

    esxi_host_name
        Connect to this ESXi host using your pillar's service_instance credentials. (optional).

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.get_role role_name=foo
    """
    log.debug("Running vmware_esxi.get_role")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__,
        profile=profile,
        esxi_host=esxi_host_name,
    )
    try:
        for role in service_instance.content.authorizationManager.roleList:
            if role.name == role_name:
                ret["role_id"] = role.roleId
                ret["role_name"] = role.name
                ret["privilege_ids"] = list(role.privilege)
        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def connect(host, service_instance=None, profile=None):
    """
    Connect an ESXi instance to a vCenter instance.

    host
        Name of ESXi instance in vCenter.

    service_instance
        The Service Instance from which to obtain managed object references. (Optional)

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.connect host=host01
    """
    log.debug(f"Connect ESXi instance {host}.")
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )

    state = utils_esxi.reconnect_host(host, service_instance)
    return {"state": state}


def disconnect(host, service_instance=None, profile=None):
    """
    Disconnect an ESXi instance.

    host
        Name of ESXi instance in vCenter.

    service_instance
        The Service Instance from which to obtain managed object references. (Optional)

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.disconnect host=host01
    """
    log.debug(f"Disconnect ESXi instance {host}.")
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )

    state = utils_esxi.disconnect_host(host, service_instance)
    return {"state": state}


def remove(host, service_instance=None, profile=None):
    """
    Remove an ESXi instance from a vCenter instance.

    host
        Name of ESXi instance in vCenter.

    service_instance
        The Service Instance from which to obtain managed object references. (Optional)

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.remove host=host01
    """
    log.debug(f"Remove ESXi instance {host}.")
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )

    state = utils_esxi.remove_host(host, service_instance)
    return {"state": state}


def move(host, cluster_name, service_instance=None, profile=None):
    """
    Move an ESXi instance to a different cluster.

    host
        Name of ESXi instance in vCenter.

    cluster_name
        Name of cluster to move host to.

    service_instance
        The Service Instance from which to obtain managed object references. (Optional)

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.move host=host01 cluster=cl1
    """
    log.debug(f"Move ESXi instance {host}.")
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )

    state = utils_esxi.move_host(host, cluster_name, service_instance)
    return {"state": state}


def add(
    host,
    root_user,
    password,
    cluster_name,
    datacenter_name,
    verify_host_cert=True,
    connect=True,
    service_instance=None,
    profile=None,
):
    """
    Add an ESXi instance to a vCenter instance.

    host
        IP address or hostname of ESXi instance.

    root_user
        Username with root privilege to ESXi instance.

    password
        Password to root user.

    cluster_name
        Name of cluster ESXi host is being added to.

    datacenter_name
        Datacenter that contains cluster that ESXi instance is being added to.

    verify_host_cert
        Validates the host's SSL certificate is signed by a CA, and that the hostname in the certificate matches the host. Defaults to True.

    connect
        Specifies whether host should be connected after being added. Defaults to True.

    service_instance
        The Service Instance from which to obtain managed object references. (Optional)

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.add host=host01 root_user=root password=CorrectHorseBatteryStaple cluster_name=cl1 datacenter_name=dc1 verify_host_cert=False connect=True
    """
    log.debug(f"Adding ESXi instance {host}.")
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    state = utils_esxi.add_host(
        host,
        root_user,
        password,
        cluster_name,
        datacenter_name,
        verify_host_cert,
        connect,
        service_instance,
    )
    return {"state": state}


def list_pkgs(
    pkg_name=None,
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    service_instance=None,
    profile=None,
):
    """
    List the packages installed on matching ESXi hosts.
    Note: Appropriate filters are recommended for large installations.

    pkg_name
        Filter by this package name. (optional)

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.list_pkgs
    """
    log.debug("Running vmware_esxi.list_pkgs")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            host_pkg_manager = h.configManager.imageConfigManager
            if not host_pkg_manager:
                continue
            ret[h.name] = {}
            pkgs = host_pkg_manager.FetchSoftwarePackages()
            for pkg in pkgs:
                if pkg_name and pkg.name != pkg_name:
                    continue
                ret[h.name][pkg.name] = {
                    "version": pkg.version,
                    "vendor": pkg.vendor,
                    "summary": pkg.summary,
                    "description": pkg.description,
                    "acceptance_level": pkg.acceptanceLevel,
                    "maintenance_mode_required": pkg.maintenanceModeRequired,
                    "creation_date": pkg.creationDate,
                }
        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def get(
    datacenter_name=None,
    cluster_name=None,
    host_name=None,
    key=None,
    default="",
    delimiter=DEFAULT_TARGET_DELIM,
    service_instance=None,
    profile=None,
):
    """
    Get configuration information for matching ESXi hosts.

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    host_name
        Filter by this ESXi hostname (optional)

    key

        Attempt to retrieve the named value from ESXi host configuration data, if the named value is not
        available return the passed default. The default return is an empty string.
        Follows the grains.get filter semantics. (optional)

        The value can also represent a value in a nested dict using a ":" delimiter
        for the dict. This means that if a dict in ESXi host configuration looks like this:

        {'vsan': {'health': 'good'}}

        To retrieve the value associated with the apache key in the pkg dict this
        key can be passed:

        vsan:health

    delimiter
        Specify an alternate delimiter to use when traversing a nested dict.
        This is useful for when the desired key contains a colon. (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.get dc1 cl1
    """
    log.debug("Running vmware_esxi.get")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    try:
        for h in hosts:
            ret[h.name] = {}
            ret[h.name]["vsan"] = {}
            vsan_manager = h.configManager.vsanSystem
            if vsan_manager:
                vsan = vsan_manager.QueryHostStatus()
                ret[h.name]["vsan"]["cluster_uuid"] = vsan.uuid
                ret[h.name]["vsan"]["node_uuid"] = vsan.nodeUuid
                ret[h.name]["vsan"]["health"] = vsan.health

            ret[h.name]["datastores"] = {}
            for store in h.datastore:
                ret[h.name]["datastores"][store.name] = {}
                ret[h.name]["datastores"][store.name]["capacity"] = store.summary.capacity
                ret[h.name]["datastores"][store.name]["free_space"] = store.summary.freeSpace

            ret[h.name]["vnics"] = {}
            for nic in h.config.network.vnic:
                ret[h.name]["vnics"][nic.device] = {}
                ret[h.name]["vnics"][nic.device]["ip_address"] = nic.spec.ip.ipAddress
                ret[h.name]["vnics"][nic.device]["subnet_mask"] = nic.spec.ip.subnetMask
                ret[h.name]["vnics"][nic.device]["mac"] = nic.spec.mac
                ret[h.name]["vnics"][nic.device]["mtu"] = nic.spec.mtu
                ret[h.name]["vnics"][nic.device]["portgroup"] = nic.spec.portgroup
                if nic.spec.distributedVirtualPort:
                    ret[h.name]["vnics"][nic.device][
                        "distributed_virtual_portgroup"
                    ] = nic.spec.distributedVirtualPort.portgroupKey
                    ret[h.name]["vnics"][nic.device][
                        "distributed_virtual_switch"
                    ] = utils_vmware._get_dvs_by_uuid(
                        service_instance, nic.spec.distributedVirtualPort.switchUuid
                    ).config.name
                else:
                    ret[h.name]["vnics"][nic.device]["distributed_virtual_portgroup"] = None
                    ret[h.name]["vnics"][nic.device]["distributed_virtual_switch"] = None

            ret[h.name]["pnics"] = {}
            for nic in h.config.network.pnic:
                ret[h.name]["pnics"][nic.device] = {}
                ret[h.name]["pnics"][nic.device]["mac"] = nic.mac
                if nic.linkSpeed:
                    ret[h.name]["pnics"][nic.device]["speed"] = nic.linkSpeed.speedMb
                else:
                    ret[h.name]["pnics"][nic.device]["speed"] = -1

                if not h.configManager.networkSystem.capabilities.supportsNetworkHints:
                    continue

                # Add CDP/LLDP information
                # TODO: Add LLDP information
                ret[h.name]["pnics"][nic.device]["cdp"] = {}
                for hint in h.configManager.networkSystem.QueryNetworkHint(nic.device):
                    csp = hint.connectedSwitchPort
                    if csp:
                        ret[h.name]["pnics"][nic.device]["cdp"]["switch_id"] = csp.devId
                        ret[h.name]["pnics"][nic.device]["cdp"]["system_name"] = csp.systemName
                        ret[h.name]["pnics"][nic.device]["cdp"]["platform"] = csp.hardwarePlatform
                        ret[h.name]["pnics"][nic.device]["cdp"]["ip_address"] = csp.address
                        ret[h.name]["pnics"][nic.device]["cdp"]["port_id"] = csp.portId
                        ret[h.name]["pnics"][nic.device]["cdp"]["vlan"] = csp.vlan

            ret[h.name]["vswitches"] = {}
            for vswitch in h.config.network.vswitch:
                ret[h.name]["vswitches"][vswitch.name] = {}
                ret[h.name]["vswitches"][vswitch.name]["mtu"] = vswitch.mtu
                ret[h.name]["vswitches"][vswitch.name]["pnics"] = []
                ret[h.name]["vswitches"][vswitch.name]["portgroups"] = []
                for pnic in vswitch.pnic:
                    ret[h.name]["vswitches"][vswitch.name]["pnics"].append(
                        pnic.replace("key-vim.host.PhysicalNic-", "")
                    )
                for pg in vswitch.portgroup:
                    ret[h.name]["vswitches"][vswitch.name]["portgroups"].append(
                        pg.replace("key-vim.host.PortGroup-", "")
                    )

            ret[h.name]["portgroups"] = {}
            for portgroup in h.config.network.portgroup:
                ret[h.name]["portgroups"][portgroup.spec.name] = {}
                ret[h.name]["portgroups"][portgroup.spec.name]["vlan_id"] = (portgroup.spec.vlanId,)
                ret[h.name]["portgroups"][portgroup.spec.name][
                    "switch_name"
                ] = portgroup.spec.vswitchName

            ret[h.name]["cpu_model"] = h.summary.hardware.cpuModel
            ret[h.name]["num_cpu_cores"] = h.summary.hardware.numCpuCores
            ret[h.name]["num_cpu_pkgs"] = h.summary.hardware.numCpuPkgs
            ret[h.name]["num_cpu_threads"] = h.summary.hardware.numCpuThreads
            ret[h.name]["memory_size"] = h.summary.hardware.memorySize
            ret[h.name]["overall_memory_usage"] = h.summary.quickStats.overallMemoryUsage
            ret[h.name]["product_name"] = h.config.product.name
            ret[h.name]["product_version"] = h.config.product.version
            ret[h.name]["product_build"] = h.config.product.build
            ret[h.name]["product_os_type"] = h.config.product.osType
            ret[h.name]["host_name"] = h.summary.config.name
            ret[h.name]["system_vendor"] = h.hardware.systemInfo.vendor
            ret[h.name]["system_model"] = h.hardware.systemInfo.model
            ret[h.name]["bios_release_date"] = h.hardware.biosInfo.releaseDate
            ret[h.name]["bios_release_version"] = h.hardware.biosInfo.biosVersion
            ret[h.name]["uptime"] = h.summary.quickStats.uptime
            ret[h.name]["in_maintenance_mode"] = h.runtime.inMaintenanceMode
            ret[h.name]["system_uuid"] = h.hardware.systemInfo.uuid
            for info in h.hardware.systemInfo.otherIdentifyingInfo:
                ret[h.name].update(
                    {
                        utils_common.camel_to_snake_case(
                            info.identifierType.key
                        ): info.identifierValue
                    }
                )
            ret[h.name]["capabilities"] = _get_capability_attribs(host=h)

            if key:
                ret[h.name] = salt.utils.data.traverse_dict_and_list(
                    ret[h.name], key, default, delimiter
                )

        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def in_maintenance_mode(host, service_instance=None, profile=None):
    """
    Check if host is in maintenance mode.

    host
        Host IP or HostSystem/ManagedObjectReference (required).

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.in_maintenance_mode '192.0.2.117'
    """
    if isinstance(host, vim.HostSystem):
        host_ref = host
    else:
        service_instance = service_instance or utils_connect.get_service_instance(
            config=__opts__, profile=profile
        )
        host_ref = utils_esxi.get_host(host, service_instance)
    mode = "normal"
    if host_ref.runtime.inMaintenanceMode:
        mode = "inMaintenance"
    return {"maintenanceMode": mode}


def maintenance_mode(
    host,
    timeout=0,
    evacuate_powered_off_vms=False,
    maintenance_spec=None,
    catch_task_error=True,
    service_instance=None,
    profile=None,
):
    """
    Put host into maintenance mode.

    host
        Host IP or HostSystem/ManagedObjectReference (required).

    timeout
        If value is greater than 0 then task will timeout if not completed with in window (optional).

    evacuate_powered_off_vms
        Only supported by VirtualCenter (optional).
         If True, for DRS will fail unless all powered-off VMs have been manually registered.
         If False, task will successed with powered-off VMs.

    maintenance_spec
        HostMaintenanceSpec (optional).

    catch_task_error
        If False and task failed then a salt exception will be thrown (optional).

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.maintenance_mode '192.0.2.117'
    """
    if isinstance(host, vim.HostSystem):
        host_ref = host
    else:
        service_instance = service_instance or utils_connect.get_service_instance(
            config=__opts__, profile=profile
        )
        host_ref = utils_esxi.get_host(host, service_instance)
    mode = in_maintenance_mode(host_ref, service_instance)
    if mode["maintenanceMode"] == "inMaintenance":
        mode["changes"] = False
        return mode
    try:
        task = host_ref.EnterMaintenanceMode_Task(
            timeout, evacuate_powered_off_vms, maintenance_spec
        )
        utils_common.wait_for_task(task, host_ref.name, "maintenanceMode")
    except salt.exceptions.SaltException as exc:
        if not catch_task_error:
            raise exc
    mode = in_maintenance_mode(host_ref, service_instance)
    mode["changes"] = mode["maintenanceMode"] == "inMaintenance"
    return mode


def exit_maintenance_mode(
    host, timeout=0, catch_task_error=True, service_instance=None, profile=None
):
    """
    Put host out of maintenance mode.

    host
        Host IP or HostSystem/ManagedObjectReference (required).

    timeout
        If value is greater than 0 then task will timeout if not completed with in window (optional).

    catch_task_error
        If False and task failed then a salt exception will be thrown (optional).

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.exit_maintenance_mode '192.0.2.117'
    """
    if isinstance(host, vim.HostSystem):
        host_ref = host
    else:
        service_instance = service_instance or utils_connect.get_service_instance(
            config=__opts__, profile=profile
        )
        host_ref = utils_esxi.get_host(host, service_instance)
    mode = in_maintenance_mode(host_ref, service_instance)
    if mode["maintenanceMode"] == "normal":
        mode["changes"] = False
        return mode
    try:
        task = host_ref.ExitMaintenanceMode_Task(timeout)
        utils_common.wait_for_task(task, host_ref.name, "maintenanceMode")
    except salt.exceptions.SaltException as exc:
        if not catch_task_error:
            raise exc
    mode = in_maintenance_mode(host_ref, service_instance)
    mode["changes"] = mode["maintenanceMode"] == "normal"
    return mode


def in_lockdown_mode(host, service_instance=None, profile=None):
    """
    Check if host is in lockdown mode.

    host
        Host IP or HostSystem/ManagedObjectReference (required).

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.in_lockdown_mode '192.0.2.117'
    """
    if isinstance(host, vim.HostSystem):
        host_ref = host
    else:
        service_instance = service_instance or utils_connect.get_service_instance(
            config=__opts__, profile=profile
        )
        host_ref = utils_esxi.get_host(host, service_instance)
    mode = "normal"
    if host_ref.config.adminDisabled:
        mode = "inLockdown"
    return {"lockdownMode": mode}


def lockdown_mode(host, catch_task_error=True, service_instance=None, profile=None):
    """
    Put host into lockdown mode.

    host
        Host IP or HostSystem/ManagedObjectReference (required).

    catch_task_error
        If False and task failed then a salt exception will be thrown (optional).

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.lockdown_mode '192.0.2.117'
    """
    if isinstance(host, vim.HostSystem):
        host_ref = host
    else:
        service_instance = service_instance or utils_connect.get_service_instance(
            config=__opts__, profile=profile
        )
        host_ref = utils_esxi.get_host(host, service_instance)
    mode = in_lockdown_mode(host_ref)
    if mode["lockdownMode"] == "inLockdown":
        mode["changes"] = False
        return mode
    try:
        host_ref.EnterLockdownMode()
    except salt.exceptions.SaltException as exc:
        if not catch_task_error:
            raise exc
    mode = in_lockdown_mode(host_ref, service_instance)
    mode["changes"] = mode["lockdownMode"] == "inLockdown"
    return mode


def exit_lockdown_mode(host, catch_task_error=True, service_instance=None, profile=None):
    """
    Put host out of lockdown mode.

    host
        Host IP or HostSystem/ManagedObjectReference (required).

    catch_task_error
        If False and task failed then a salt exception will be thrown (optional).

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.exit_lockdown_mode '192.0.2.117'
    """
    if isinstance(host, vim.HostSystem):
        host_ref = host
    else:
        service_instance = service_instance or utils_connect.get_service_instance(
            config=__opts__, profile=profile
        )
        host_ref = utils_esxi.get_host(host, service_instance)
    mode = in_lockdown_mode(host_ref)
    if mode["lockdownMode"] == "normal":
        mode["changes"] = False
        return mode
    try:
        host_ref.ExitLockdownMode()
    except salt.exceptions.SaltException as exc:
        if not catch_task_error:
            raise exc
    mode = in_lockdown_mode(host_ref, service_instance)
    mode["changes"] = mode["lockdownMode"] == "normal"
    return mode


def get_vsan_enabled(
    host_name=None,
    datacenter_name=None,
    cluster_name=None,
    service_instance=None,
    profile=None,
):
    """
    Get the VSAN enabled status for a given host or all hosts. Returns ``True``
    if VSAN is enabled, ``False`` if it is not enabled.

    host_name
        Filter by this ESXi hostname (optional)

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.get_vsan_enabled host_name='192.0.2.117'
    """
    log.debug("Running vmware_esxi.get_vsan_enabled")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    for host in hosts:
        ret[host.name] = host.config.vsanHostConfig.enabled
    return ret


def vsan_enable(
    enable=True,
    host_name=None,
    datacenter_name=None,
    cluster_name=None,
    service_instance=None,
    profile=None,
):
    """
    Enable VSAN for a given host or all hosts.

    enable
        Enable vSAN. Valid values: True, False.

    host_name
        Filter by this ESXi hostname (optional)

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.vsan_enable host_name='192.0.2.117'
    """
    log.debug("Running vmware_esxi.get_vsan_enabled")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    for host in hosts:
        config = vim.vsan.host.ConfigInfo()
        config.enabled = enable
        task = host.configManager.vsanSystem.UpdateVsan_Task(config)
        utils_common.wait_for_task(task, host.name, "UpdateVsan_Task")
        ret[host.name] = host.config.vsanHostConfig.enabled
    return ret


def _get_vsan_eligible_disks(hosts):
    """
    Helper function that returns a dictionary of host_name keys with either a list of eligible
    disks that can be added to VSAN or either an 'Error' message or a message saying no
    eligible disks were found. Possible keys/values look like:

    return = {'host_1': {'Error': 'VSAN System Config Manager is unset ...'},
              'host_2': {'Eligible': 'The host xxx does not have any VSAN eligible disks.'},
              'host_3': {'Eligible': [disk1, disk2, disk3, disk4],
              'host_4': {'Eligible': []}}

    hosts
        list of host references

    """
    ret = {}
    for host in hosts:
        # Get VSAN System Config Manager, if available.
        vsan_system = host.configManager.vsanSystem
        if vsan_system is None:
            msg = (
                "VSAN System Config Manager is unset for host '{}'. "
                "VSAN configuration cannot be changed without a configured "
                "VSAN System.".format(host.name)
            )
            log.debug(msg)
            ret.update({host.name: {"Error": msg}})
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
            msg = "The host '{}' does not have any VSAN eligible disks.".format(host.name)
            log.warning(msg)
            ret.update({host.name: {"Eligible": msg}})
            continue

        # Get disks for host and combine into one list of Disk Objects
        disks = utils_esxi.get_host_ssds(host) + utils_esxi.get_host_non_ssds(host)

        # Get disks that are in both the disks list and suitable_disks lists.
        matching = []
        for disk in disks:
            for suitable_disk in suitable_disks:
                if disk.canonicalName == suitable_disk.disk.canonicalName:
                    matching.append(disk)

        ret.update({host.name: {"Eligible": matching}})
    return ret


def get_vsan_eligible_disks(
    host_name=None,
    datacenter_name=None,
    cluster_name=None,
    service_instance=None,
    profile=None,
):
    """
    Returns a list of VSAN-eligible disks for a given host or list of host_names.

    host_name
        Filter by this ESXi hostname (optional)

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.get_vsan_enabled host_name='192.0.2.117'
    """
    log.debug("Running vmware_esxi.get_vsan_enabled")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    response = _get_vsan_eligible_disks(hosts)
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


def vsan_add_disks(
    host_name=None,
    datacenter_name=None,
    cluster_name=None,
    service_instance=None,
    profile=None,
):
    """
    Add any VSAN-eligible disks to the VSAN System for the given host or list of host_names.

    host_name
        Filter by this ESXi hostname (optional)

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    .. code-block:: bash

        salt '*' vmware_esxi.vsan_add_disks host_name='192.0.2.117'
    """
    log.debug("Running vmware_esxi.vsan_add_disks")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    response = _get_vsan_eligible_disks(hosts)

    for host_name, value in response.items():
        host_ref = utils_esxi.get_host(host_name, service_instance)
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
                    utils_common.wait_for_task(
                        task, host_name, "Adding disks to VSAN", sleep_seconds=3
                    )
                except vim.fault.InsufficientDisks as err:
                    log.debug(err.msg)
                    ret.update({host_name: {"Error": err.msg}})
                    continue
                except Exception as err:
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


def list_disks(
    disk_ids=None,
    scsi_addresses=None,
    host_name=None,
    datacenter_name=None,
    cluster_name=None,
    service_instance=None,
    profile=None,
):
    """
    Returns a list of dict representations of the disks in an ESXi host.
    The list of disks can be filtered by disk canonical names or
    scsi addresses.

    disk_ids:
        List of disk canonical names to be retrieved. Default is None.

    scsi_addresses
        List of scsi addresses of disks to be retrieved. Default is None

    host_name
        Filter by this ESXi hostname (optional)

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_esxi.list_disks
        salt '*' vmware_esxi.list_disks disk_ids='[naa.00, naa.001]'
        salt '*' vmware_esxi.list_disks scsi_addresses='[vmhba0:C0:T0:L0, vmhba1:C0:T0:L0]'
    """
    log.debug("Running vmware_esxi.list_disks")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    for host in hosts:
        get_all_disks = True if not (disk_ids or scsi_addresses) else False
        ret[host.name] = []
        scsi_address_to_lun = utils_common.get_scsi_address_to_lun_map(host, hostname=host.name)
        canonical_name_to_scsi_address = {
            lun.canonicalName: scsi_addr for scsi_addr, lun in scsi_address_to_lun.items()
        }
        for disk in utils_common.get_disks(host, disk_ids, scsi_addresses, get_all_disks):
            ret[host.name].append(
                {
                    "id": disk.canonicalName,
                    "scsi_address": canonical_name_to_scsi_address[disk.canonicalName],
                }
            )
    return ret


def list_diskgroups(
    cache_disk_ids=None,
    host_name=None,
    datacenter_name=None,
    cluster_name=None,
    service_instance=None,
    profile=None,
):
    """
    Returns a list of disk group dict representation on an ESXi host.
    The list of disk groups can be filtered by the cache disks
    canonical names. If no filtering is applied, all disk groups are returned.

    cache_disk_ids
        List of cache disk canonical names of the disk groups to be retrieved.
        Default is None.

    use_proxy_details
        Specify whether to use the proxy minion's details instead of the
        arguments

    host_name
        Filter by this ESXi hostname (optional)

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_esxi.list_diskgroups
        salt '*' vmware_esxi.list_diskgroups cache_disk_ids='[naa.000000000000001]'
    """
    log.debug("Running vmware_esxi.list_diskgroups")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    get_all_diskgroups = True if not cache_disk_ids else False
    for host in hosts:
        ret[host.name] = []
        for diskgroup in utils_common.get_diskgroups(host, cache_disk_ids, get_all_diskgroups):
            ret[host.name].append(
                {
                    "cache_disk": diskgroup.ssd.canonicalName,
                    "capacity_disks": [d.canonicalName for d in diskgroup.nonSsd],
                }
            )
    return ret


def get_host_datetime(
    host_name=None,
    datacenter_name=None,
    cluster_name=None,
    service_instance=None,
    profile=None,
):
    """
    .. versionadded:: 23.4.4.0rc1

    Get the date/time information for a given host or all hosts.

    host_name
        Filter by this ESXi hostname (optional)

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_esxi.get_host_datetime

    """
    log.debug("Running vmware_esxi.get_host_datetime")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )
    for host in hosts:
        date_time_manager = utils_common.get_date_time_mgr(host)
        date_time = date_time_manager.QueryDateTime()
        ret.update({host.name: date_time.ctime()})

    return ret


def get_vmotion_enabled(
    host_name=None,
    datacenter_name=None,
    cluster_name=None,
    service_instance=None,
    profile=None,
    host_names=None,
):
    """
    .. versionadded:: 23.4.4.0rc1

    Get the VMotion enabled status for a given host or a list of host_names. Returns ``True``
    if VMotion is enabled, ``False`` if it is not enabled.

    host_name
        Filter by this ESXi hostname (optional)

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    host_names
        List of ESXi host names provided for a vCenter Server, the host_names argument
        is required to tell vCenter which hosts to check if VMotion is enabled.

        If host_names is not provided, the VMotion status will be retrieved for the
        ``host`` location instead. This is useful for when service instance
        connection information is used for a single ESXi host.


    CLI Example:

    .. code-block:: bash

        salt '*' vmware_esxi.get_vmotion_enabled
    """
    log.debug("Running vmware_esxi.get_vmotion_enabled")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    if not host_names:
        host_names = host

    try:
        for host in hosts:
            if host in host_names:
                vmotion_vnic = host.configManager.vmotionSystem.netConfig.selectedVnic
                if vmotion_vnic:
                    ret.update({host.name: {"VMotion Enabled": True}})
                else:
                    ret.update({host.name: {"VMotion Enabled": False}})
        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def vmotion_disable(
    host_name=None,
    datacenter_name=None,
    cluster_name=None,
    service_instance=None,
    profile=None,
    host_names=None,
):
    """
    .. versionadded:: 23.6.29.0rc1

    Disable vMotion for a given host or list of host_names.

    host_name
        Filter by this ESXi hostname (optional)

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    host_names
        List of ESXi host names provided for a vCenter Server, the host_names argument
        is required to tell vCenter which hosts should disable VMotion.

        If host_names is not provided, VMotion will be disabled for the ``host``
        location instead. This is useful for when service instance connection
        information is used for a single ESXi host.

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_esxi.vmotion_disable
    """
    log.debug("Running vmware_esxi.vmotion_disable")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    ## host_names = _check_hosts(service_instance, host, host_names)
    if not host_names:
        host_names = host

    try:
        ## for host_name in host_names:
        ##     host_ref = _get_host_ref(service_instance, host, host_name=host_name)
        ##     vmotion_system = host_ref.configManager.vmotionSystem

        for host in hosts:
            if host in host_names:
                vmotion_system = host.configManager.vmotionSystem

                # Disable VMotion for the host by removing the VNic selected to use for VMotion.
                try:
                    vmotion_system.DeselectVnic()
                except vim.fault.HostConfigFault as err:
                    msg = f"vsphere.vmotion_disable failed: {err}"
                    log.debug(msg)
                    ret.update({host_name: {"Error": msg, "VMotion Disabled": False}})
                    continue

                ret.update({host_name: {"VMotion Disabled": True}})

        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))


def vmotion_enable(
    host_name=None,
    datacenter_name=None,
    cluster_name=None,
    service_instance=None,
    profile=None,
    host_names=None,
    device="vmk0",
):
    """
    .. versionadded:: 23.6.29.0rc1

    Enable vMotion for a given host or list of host_names.

    host_name
        Filter by this ESXi hostname (optional)

    datacenter_name
        Filter by this datacenter name (required when cluster is specified)

    cluster_name
        Filter by this cluster name (optional)

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)

    host_names
        List of ESXi host names provided for a vCenter Server, the host_names argument
        is required to tell vCenter which hosts should enable VMotion.

        If host_names is not provided, VMotion will be enabled for the ``host``
        location instead. This is useful for when service instance connection
        information is used for a single ESXi host.

    device
        The device that uniquely identifies the VirtualNic that will be used for
        VMotion for each host. Defaults to ``vmk0``.

    CLI Example:

    .. code-block:: bash

        salt '*' vmware_esxi.vmotion_disable
    """
    log.debug("Running vmware_esxi.vmotion_disable")
    ret = {}
    service_instance = service_instance or utils_connect.get_service_instance(
        config=__opts__, profile=profile
    )
    hosts = utils_esxi.get_hosts(
        service_instance=service_instance,
        host_names=[host_name] if host_name else None,
        cluster_name=cluster_name,
        datacenter_name=datacenter_name,
        get_all_hosts=host_name is None,
    )

    ## host_names = _check_hosts(service_instance, host, host_names)
    if not host_names:
        host_names = host

    try:
        ## for host_name in host_names:
        ##     host_ref = _get_host_ref(service_instance, host, host_name=host_name)
        ##     vmotion_system = host_ref.configManager.vmotionSystem

        for host in hosts:
            if host in host_names:
                vmotion_system = host.configManager.vmotionSystem

                # Enable VMotion for the host by setting the given device to provide the VNic to use for VMotion.
                try:
                    vmotion_system.SelectVnic(device)
                except vim.fault.HostConfigFault as err:
                    msg = f"vsphere.vmotion_disable failed: {err}"
                    log.debug(msg)
                    ret.update({host_name: {"Error": msg, "VMotion Enabled": False}})
                    continue

                ret.update({host_name: {"VMotion Enabled": True}})

        return ret
    except DEFAULT_EXCEPTIONS as exc:
        raise salt.exceptions.SaltException(str(exc))
