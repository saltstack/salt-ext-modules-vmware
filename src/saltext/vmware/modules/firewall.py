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


__virtualname__ = "vmware_firewall"


def __virtual__():
    return __virtualname__


def _format_firewall_stdout(cmd_ret):
    """
    Helper function to format the stdout from the get_firewall_status function.

    cmd_ret
        The return dictionary that comes from a cmd.run_all call.
    """
    ret_dict = {"success": True, "rulesets": {}}
    for line in cmd_ret["stdout"].splitlines():
        if line.startswith("Name"):
            continue
        if line.startswith("---"):
            continue
        ruleset_status = line.split()
        ret_dict["rulesets"][ruleset_status[0]] = bool(ruleset_status[1])

    return ret_dict


def get_firewall_status(
    host, username, password, protocol=None, port=None, esxi_hosts=None, credstore=None
):
    """
    Show status of all firewall rule sets.

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

    :return: Nested dictionary with two toplevel keys ``rulesets`` and ``success``
             ``success`` will be True or False depending on query success
             ``rulesets`` will list the rulesets and their statuses if ``success``
             was true, per host.

    CLI Example:

    .. code-block:: bash

        # Used for ESXi host connection information
        salt '*' vsphere.get_firewall_status my.esxi.host root bad-password

        # Used for connecting to a vCenter Server
        salt '*' vsphere.get_firewall_status my.vcenter.location root bad-password \
            esxi_hosts='[esxi-1.host.com, esxi-2.host.com]'
    """
    cmd = "network firewall ruleset list"

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
                ret.update(
                    {
                        esxi_host: {
                            "Error": response["stdout"],
                            "success": False,
                            "rulesets": None,
                        }
                    }
                )
            else:
                # format the response stdout into something useful
                ret.update({esxi_host: _format_firewall_stdout(response)})
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
            ret.update(
                {
                    host: {
                        "Error": response["stdout"],
                        "success": False,
                        "rulesets": None,
                    }
                }
            )
        else:
            # format the response stdout into something useful
            ret.update({host: _format_firewall_stdout(response)})

    return ret


def enable_firewall_ruleset(
    host,
    username,
    password,
    ruleset_enable,
    ruleset_name,
    protocol=None,
    port=None,
    esxi_hosts=None,
    credstore=None,
):
    """
    Enable or disable an ESXi firewall rule set.

    host
        The location of the host.

    username
        The username used to login to the host, such as ``root``.

    password
        The password used to login to the host.

    ruleset_enable
        True to enable the ruleset, false to disable.

    ruleset_name
        Name of ruleset to target.

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

    :return: A standard cmd.run_all dictionary, per host.

    CLI Example:

    .. code-block:: bash

        # Used for ESXi host connection information
        salt '*' vsphere.enable_firewall_ruleset my.esxi.host root bad-password True 'syslog'

        # Used for connecting to a vCenter Server
        salt '*' vsphere.enable_firewall_ruleset my.vcenter.location root bad-password True 'syslog' \
            esxi_hosts='[esxi-1.host.com, esxi-2.host.com]'
    """
    cmd = "network firewall ruleset set --enabled {} --ruleset-id={}".format(
        ruleset_enable, ruleset_name
    )

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
        ret.update({host: response})

    return ret
