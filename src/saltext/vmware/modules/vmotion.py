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


__virtualname__ = "vmware_vmotion"


def __virtual__():
    return __virtualname__


def get_vmotion_enabled(
    host,
    username,
    password,
    protocol=None,
    port=None,
    host_names=None,
    verify_ssl=True,
):
    """
    Get the VMotion enabled status for a given host or a list of host_names. Returns ``True``
    if VMotion is enabled, ``False`` if it is not enabled.

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
        tell vCenter which hosts to check if VMotion is enabled.

        If host_names is not provided, the VMotion status will be retrieved for the
        ``host`` location instead. This is useful for when service instance
        connection information is used for a single ESXi host.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        # Used for single ESXi host connection information
        salt '*' vsphere.get_vmotion_enabled my.esxi.host root bad-password

        # Used for connecting to a vCenter Server
        salt '*' vsphere.get_vmotion_enabled my.vcenter.location root bad-password \
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
        vmotion_vnic = host_ref.configManager.vmotionSystem.netConfig.selectedVnic
        if vmotion_vnic:
            ret.update({host_name: {"VMotion Enabled": True}})
        else:
            ret.update({host_name: {"VMotion Enabled": False}})

    return ret


def vmotion_disable(
    host, username, password, protocol=None, port=None, host_names=None, verify_ssl=True
):
    """
    Disable vMotion for a given host or list of host_names.

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
        tell vCenter which hosts should disable VMotion.

        If host_names is not provided, VMotion will be disabled for the ``host``
        location instead. This is useful for when service instance connection
        information is used for a single ESXi host.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        # Used for single ESXi host connection information
        salt '*' vsphere.vmotion_disable my.esxi.host root bad-password

        # Used for connecting to a vCenter Server
        salt '*' vsphere.vmotion_disable my.vcenter.location root bad-password \
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
        vmotion_system = host_ref.configManager.vmotionSystem

        # Disable VMotion for the host by removing the VNic selected to use for VMotion.
        try:
            vmotion_system.DeselectVnic()
        except vim.fault.HostConfigFault as err:
            msg = "vsphere.vmotion_disable failed: {}".format(err)
            log.debug(msg)
            ret.update({host_name: {"Error": msg, "VMotion Disabled": False}})
            continue

        ret.update({host_name: {"VMotion Disabled": True}})

    return ret


def vmotion_enable(
    host,
    username,
    password,
    protocol=None,
    port=None,
    host_names=None,
    device="vmk0",
    verify_ssl=True,
):
    """
    Enable vMotion for a given host or list of host_names.

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
        tell vCenter which hosts should enable VMotion.

        If host_names is not provided, VMotion will be enabled for the ``host``
        location instead. This is useful for when service instance connection
        information is used for a single ESXi host.

    device
        The device that uniquely identifies the VirtualNic that will be used for
        VMotion for each host. Defaults to ``vmk0``.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        # Used for single ESXi host connection information
        salt '*' vsphere.vmotion_enable my.esxi.host root bad-password

        # Used for connecting to a vCenter Server
        salt '*' vsphere.vmotion_enable my.vcenter.location root bad-password \
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
        vmotion_system = host_ref.configManager.vmotionSystem

        # Enable VMotion for the host by setting the given device to provide the VNic to use for VMotion.
        try:
            vmotion_system.SelectVnic(device)
        except vim.fault.HostConfigFault as err:
            msg = "vsphere.vmotion_disable failed: {}".format(err)
            log.debug(msg)
            ret.update({host_name: {"Error": msg, "VMotion Enabled": False}})
            continue

        ret.update({host_name: {"VMotion Enabled": True}})

    return ret
