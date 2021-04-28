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


__virtualname__ = "vmware_coredump"


def __virtual__():
    return __virtualname__


def _format_coredump_stdout(cmd_ret):
    """
    Helper function to format the stdout from the get_coredump_network_config function.

    cmd_ret
        The return dictionary that comes from a cmd.run_all call.
    """
    ret_dict = {}
    for line in cmd_ret["stdout"].splitlines():
        line = line.strip().lower()
        if line.startswith("enabled:"):
            enabled = line.split(":")
            if "true" in enabled[1]:
                ret_dict["enabled"] = True
            else:
                ret_dict["enabled"] = False
                break
        if line.startswith("host vnic:"):
            host_vnic = line.split(":")
            ret_dict["host_vnic"] = host_vnic[1].strip()
        if line.startswith("network server ip:"):
            ip = line.split(":")
            ret_dict["ip"] = ip[1].strip()
        if line.startswith("network server port:"):
            ip_port = line.split(":")
            ret_dict["port"] = ip_port[1].strip()

    return ret_dict


def get_coredump_network_config(
    host, username, password, protocol=None, port=None, esxi_hosts=None, credstore=None
):
    """
    Retrieve information on ESXi or vCenter network dump collection and
    format it into a dictionary.

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

    esxi_hosts
        If ``host`` is a vCenter host, then use esxi_hosts to execute this function
        on a list of one or more ESXi machines.

    credstore
        Optionally set to path to the credential store file.

    :return: A dictionary with the network configuration, or, if getting
             the network config failed, a an error message retrieved from the
             standard cmd.run_all dictionary, per host.

    CLI Example:

    .. code-block:: bash

        # Used for ESXi host connection information
        salt '*' vsphere.get_coredump_network_config my.esxi.host root bad-password

        # Used for connecting to a vCenter Server
        salt '*' vsphere.get_coredump_network_config my.vcenter.location root bad-password \
            esxi_hosts='[esxi-1.host.com, esxi-2.host.com]'

    """
    cmd = "system coredump network get"
    ret = {}
    if esxi_hosts:
        if not isinstance(esxi_hosts, list):
            raise CommandExecutionError("'esxi_hosts' must be a list.")

        for esxi_host in esxi_hosts:
            response = saltext.vmware.utils.vmware.esxcli(
                host,
                username,
                password,
                cmd,
                protocol=protocol,
                port=port,
                esxi_host=esxi_host,
                credstore=credstore,
            )
            if response["retcode"] != 0:
                ret.update({esxi_host: {"Error": response.get("stdout")}})
            else:
                # format the response stdout into something useful
                ret.update({esxi_host: {"Coredump Config": _format_coredump_stdout(response)}})
    else:
        # Handles a single host or a vCenter connection when no esxi_hosts are provided.
        response = saltext.vmware.utils.vmware.esxcli(
            host,
            username,
            password,
            cmd,
            protocol=protocol,
            port=port,
            credstore=credstore,
        )
        if response["retcode"] != 0:
            ret.update({host: {"Error": response.get("stdout")}})
        else:
            # format the response stdout into something useful
            stdout = _format_coredump_stdout(response)
            ret.update({host: {"Coredump Config": stdout}})

    return ret


def coredump_network_enable(
    host,
    username,
    password,
    enabled,
    protocol=None,
    port=None,
    esxi_hosts=None,
    credstore=None,
):
    """
    Enable or disable ESXi core dump collection. Returns ``True`` if coredump is enabled
    and returns ``False`` if core dump is not enabled. If there was an error, the error
    will be the value printed in the ``Error`` key dictionary for the given host.

    host
        The location of the host.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    enabled
        Python True or False to enable or disable coredumps.

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    esxi_hosts
        If ``host`` is a vCenter host, then use esxi_hosts to execute this function
        on a list of one or more ESXi machines.

    credstore
        Optionally set to path to the credential store file.

    CLI Example:

    .. code-block:: bash

        # Used for ESXi host connection information
        salt '*' vsphere.coredump_network_enable my.esxi.host root bad-password True

        # Used for connecting to a vCenter Server
        salt '*' vsphere.coredump_network_enable my.vcenter.location root bad-password True \
            esxi_hosts='[esxi-1.host.com, esxi-2.host.com]'
    """
    if enabled:
        enable_it = 1
    else:
        enable_it = 0
    cmd = "system coredump network set -e {}".format(enable_it)

    ret = {}
    if esxi_hosts:
        if not isinstance(esxi_hosts, list):
            raise CommandExecutionError("'esxi_hosts' must be a list.")

        for esxi_host in esxi_hosts:
            response = saltext.vmware.utils.vmware.esxcli(
                host,
                username,
                password,
                cmd,
                protocol=protocol,
                port=port,
                esxi_host=esxi_host,
                credstore=credstore,
            )
            if response["retcode"] != 0:
                ret.update({esxi_host: {"Error": response.get("stdout")}})
            else:
                ret.update({esxi_host: {"Coredump Enabled": enabled}})

    else:
        # Handles a single host or a vCenter connection when no esxi_hosts are provided.
        response = saltext.vmware.utils.vmware.esxcli(
            host,
            username,
            password,
            cmd,
            protocol=protocol,
            port=port,
            credstore=credstore,
        )
        if response["retcode"] != 0:
            ret.update({host: {"Error": response.get("stdout")}})
        else:
            ret.update({host: {"Coredump Enabled": enabled}})

    return ret


def set_coredump_network_config(
    host,
    username,
    password,
    dump_ip,
    protocol=None,
    port=None,
    host_vnic="vmk0",
    dump_port=6500,
    esxi_hosts=None,
    credstore=None,
):
    """

    Set the network parameters for a network coredump collection.
    Note that ESXi requires that the dumps first be enabled (see
    `coredump_network_enable`) before these parameters may be set.

    host
        The location of the host.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    dump_ip
        IP address of host that will accept the dump.

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    esxi_hosts
        If ``host`` is a vCenter host, then use esxi_hosts to execute this function
        on a list of one or more ESXi machines.

    host_vnic
        Host VNic port through which to communicate. Defaults to ``vmk0``.

    dump_port
        TCP port to use for the dump, defaults to ``6500``.

    credstore
        Optionally set to path to the credential store file.

    :return: A standard cmd.run_all dictionary with a `success` key added, per host.
             `success` will be True if the set succeeded, False otherwise.

    CLI Example:

    .. code-block:: bash

        # Used for ESXi host connection information
        salt '*' vsphere.set_coredump_network_config my.esxi.host root bad-password 'dump_ip.host.com'

        # Used for connecting to a vCenter Server
        salt '*' vsphere.set_coredump_network_config my.vcenter.location root bad-password 'dump_ip.host.com' \
            esxi_hosts='[esxi-1.host.com, esxi-2.host.com]'
    """
    cmd = "system coredump network set -v {} -i {} -o {}".format(host_vnic, dump_ip, dump_port)
    ret = {}
    if esxi_hosts:
        if not isinstance(esxi_hosts, list):
            raise CommandExecutionError("'esxi_hosts' must be a list.")

        for esxi_host in esxi_hosts:
            response = saltext.vmware.utils.vmware.esxcli(
                host,
                username,
                password,
                cmd,
                protocol=protocol,
                port=port,
                esxi_host=esxi_host,
                credstore=credstore,
            )
            if response["retcode"] != 0:
                response["success"] = False
            else:
                response["success"] = True

            # Update the cmd.run_all dictionary for each particular host.
            ret.update({esxi_host: response})
    else:
        # Handles a single host or a vCenter connection when no esxi_hosts are provided.
        response = saltext.vmware.utils.vmware.esxcli(
            host,
            username,
            password,
            cmd,
            protocol=protocol,
            port=port,
            credstore=credstore,
        )
        if response["retcode"] != 0:
            response["success"] = False
        else:
            response["success"] = True
        ret.update({host: response})

    return ret
