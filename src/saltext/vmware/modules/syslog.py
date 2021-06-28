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


__virtualname__ = "vmware_syslog"


def __virtual__():
    return __virtualname__


def _reset_syslog_config_params(
    host,
    username,
    password,
    cmd,
    resets,
    valid_resets,
    protocol=None,
    port=None,
    esxi_host=None,
    credstore=None,
):
    """
    Helper function for reset_syslog_config that resets the config and populates the return dictionary.
    """
    ret_dict = {}
    all_success = True

    if not isinstance(resets, list):
        resets = [resets]

    for reset_param in resets:
        if reset_param in valid_resets:
            ret = salt.utils.vmware.esxcli(
                host,
                username,
                password,
                cmd + reset_param,
                protocol=protocol,
                port=port,
                esxi_host=esxi_host,
                credstore=credstore,
            )
            ret_dict[reset_param] = {}
            ret_dict[reset_param]["success"] = ret["retcode"] == 0
            if ret["retcode"] != 0:
                all_success = False
                ret_dict[reset_param]["message"] = ret["stdout"]
        else:
            all_success = False
            ret_dict[reset_param] = {}
            ret_dict[reset_param]["success"] = False
            ret_dict[reset_param]["message"] = "Invalid syslog " "configuration parameter"

    ret_dict["success"] = all_success

    return ret_dict


def _set_syslog_config_helper(
    host,
    username,
    password,
    syslog_config,
    config_value,
    protocol=None,
    port=None,
    reset_service=None,
    esxi_host=None,
    credstore=None,
):
    """
    Helper function for set_syslog_config that sets the config and populates the return dictionary.
    """
    cmd = "system syslog config set --{} {}".format(syslog_config, config_value)
    ret_dict = {}

    valid_resets = [
        "logdir",
        "loghost",
        "default-rotate",
        "default-size",
        "default-timeout",
        "logdir-unique",
    ]
    if syslog_config not in valid_resets:
        ret_dict.update(
            {
                "success": False,
                "message": "'{}' is not a valid config variable.".format(syslog_config),
            }
        )
        return ret_dict

    response = salt.utils.vmware.esxcli(
        host,
        username,
        password,
        cmd,
        protocol=protocol,
        port=port,
        esxi_host=esxi_host,
        credstore=credstore,
    )

    # Update the return dictionary for success or error messages.
    if response["retcode"] != 0:
        ret_dict.update({syslog_config: {"success": False, "message": response["stdout"]}})
    else:
        ret_dict.update({syslog_config: {"success": True}})

    # Restart syslog for each host, if desired.
    if reset_service:
        if esxi_host:
            host_name = esxi_host
            esxi_host = [esxi_host]
        else:
            host_name = host
        response = syslog_service_reload(
            host,
            username,
            password,
            protocol=protocol,
            port=port,
            esxi_hosts=esxi_host,
            credstore=credstore,
        ).get(host_name)
        ret_dict.update({"syslog_restart": {"success": response["retcode"] == 0}})

    return ret_dict


def _format_syslog_config(cmd_ret):
    """
    Helper function to format the stdout from the get_syslog_config function.

    cmd_ret
        The return dictionary that comes from a cmd.run_all call.
    """
    ret_dict = {"success": cmd_ret["retcode"] == 0}

    if cmd_ret["retcode"] != 0:
        ret_dict["message"] = cmd_ret["stdout"]
    else:
        for line in cmd_ret["stdout"].splitlines():
            line = line.strip()
            cfgvars = line.split(": ")
            key = cfgvars[0].strip()
            value = cfgvars[1].strip()
            ret_dict[key] = value

    return ret_dict


def syslog_service_reload(
    host, username, password, protocol=None, port=None, esxi_hosts=None, credstore=None
):
    """
    Reload the syslog service so it will pick up any changes.

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

    :return: A standard cmd.run_all dictionary.  This dictionary will at least
             have a `retcode` key.  If `retcode` is 0 the command was successful.

    CLI Example:

    .. code-block:: bash

        # Used for ESXi host connection information
        salt '*' vsphere.syslog_service_reload my.esxi.host root bad-password

        # Used for connecting to a vCenter Server
        salt '*' vsphere.syslog_service_reload my.vcenter.location root bad-password \
            esxi_hosts='[esxi-1.host.com, esxi-2.host.com]'
    """
    cmd = "system syslog reload"

    ret = {}
    if esxi_hosts:
        if not isinstance(esxi_hosts, list):
            raise CommandExecutionError("'esxi_hosts' must be a list.")

        for esxi_host in esxi_hosts:
            response = salt.utils.vmware.esxcli(
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
        response = salt.utils.vmware.esxcli(
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


def set_syslog_config(
    host,
    username,
    password,
    syslog_config,
    config_value,
    protocol=None,
    port=None,
    firewall=True,
    reset_service=True,
    esxi_hosts=None,
    credstore=None,
):
    """
    Set the specified syslog configuration parameter. By default, this function will
    reset the syslog service after the configuration is set.

    host
        ESXi or vCenter host to connect to.

    username
        User to connect as, usually root.

    password
        Password to connect with.

    syslog_config
        Name of parameter to set (corresponds to the command line switch for
        esxcli without the double dashes (--))

        Valid syslog_config values are ``logdir``, ``loghost``, ``default-rotate`,
        ``default-size``, ``default-timeout``, and ``logdir-unique``.

    config_value
        Value for the above parameter. For ``loghost``, URLs or IP addresses to
        use for logging. Multiple log servers can be specified by listing them,
        comma-separated, but without spaces before or after commas.

        (reference: https://blogs.vmware.com/vsphere/2012/04/configuring-multiple-syslog-servers-for-esxi-5.html)

    protocol
        Optionally set to alternate protocol if the host is not using the default
        protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the host is not using the default
        port. Default port is ``443``.

    firewall
        Enable the firewall rule set for syslog. Defaults to ``True``.

    reset_service
        After a successful parameter set, reset the service. Defaults to ``True``.

    esxi_hosts
        If ``host`` is a vCenter host, then use esxi_hosts to execute this function
        on a list of one or more ESXi machines.

    credstore
        Optionally set to path to the credential store file.

    :return: Dictionary with a top-level key of 'success' which indicates
             if all the parameters were reset, and individual keys
             for each parameter indicating which succeeded or failed, per host.

    CLI Example:

    .. code-block:: bash

        # Used for ESXi host connection information
        salt '*' vsphere.set_syslog_config my.esxi.host root bad-password \
            loghost ssl://localhost:5432,tcp://10.1.0.1:1514

        # Used for connecting to a vCenter Server
        salt '*' vsphere.set_syslog_config my.vcenter.location root bad-password \
            loghost ssl://localhost:5432,tcp://10.1.0.1:1514 \
            esxi_hosts='[esxi-1.host.com, esxi-2.host.com]'

    """
    ret = {}

    # First, enable the syslog firewall ruleset, for each host, if needed.
    if firewall and syslog_config == "loghost":
        if esxi_hosts:
            if not isinstance(esxi_hosts, list):
                raise CommandExecutionError("'esxi_hosts' must be a list.")

            for esxi_host in esxi_hosts:
                response = enable_firewall_ruleset(
                    host,
                    username,
                    password,
                    ruleset_enable=True,
                    ruleset_name="syslog",
                    protocol=protocol,
                    port=port,
                    esxi_hosts=[esxi_host],
                    credstore=credstore,
                ).get(esxi_host)
                if response["retcode"] != 0:
                    ret.update(
                        {
                            esxi_host: {
                                "enable_firewall": {
                                    "message": response["stdout"],
                                    "success": False,
                                }
                            }
                        }
                    )
                else:
                    ret.update({esxi_host: {"enable_firewall": {"success": True}}})
        else:
            # Handles a single host or a vCenter connection when no esxi_hosts are provided.
            response = enable_firewall_ruleset(
                host,
                username,
                password,
                ruleset_enable=True,
                ruleset_name="syslog",
                protocol=protocol,
                port=port,
                credstore=credstore,
            ).get(host)
            if response["retcode"] != 0:
                ret.update(
                    {
                        host: {
                            "enable_firewall": {
                                "message": response["stdout"],
                                "success": False,
                            }
                        }
                    }
                )
            else:
                ret.update({host: {"enable_firewall": {"success": True}}})

    # Set the config value on each esxi_host, if provided.
    if esxi_hosts:
        if not isinstance(esxi_hosts, list):
            raise CommandExecutionError("'esxi_hosts' must be a list.")

        for esxi_host in esxi_hosts:
            response = _set_syslog_config_helper(
                host,
                username,
                password,
                syslog_config,
                config_value,
                protocol=protocol,
                port=port,
                reset_service=reset_service,
                esxi_host=esxi_host,
                credstore=credstore,
            )
            # Ensure we don't overwrite any dictionary data already set
            # By updating the esxi_host directly.
            if ret.get(esxi_host) is None:
                ret.update({esxi_host: {}})
            ret[esxi_host].update(response)

    else:
        # Handles a single host or a vCenter connection when no esxi_hosts are provided.
        response = _set_syslog_config_helper(
            host,
            username,
            password,
            syslog_config,
            config_value,
            protocol=protocol,
            port=port,
            reset_service=reset_service,
            credstore=credstore,
        )
        # Ensure we don't overwrite any dictionary data already set
        # By updating the host directly.
        if ret.get(host) is None:
            ret.update({host: {}})
        ret[host].update(response)

    return ret


def get_syslog_config(
    host, username, password, protocol=None, port=None, esxi_hosts=None, credstore=None
):
    """
    Retrieve the syslog configuration.

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

    :return: Dictionary with keys and values corresponding to the
             syslog configuration, per host.

    CLI Example:

    .. code-block:: bash

        # Used for ESXi host connection information
        salt '*' vsphere.get_syslog_config my.esxi.host root bad-password

        # Used for connecting to a vCenter Server
        salt '*' vsphere.get_syslog_config my.vcenter.location root bad-password \
            esxi_hosts='[esxi-1.host.com, esxi-2.host.com]'
    """
    cmd = "system syslog config get"

    ret = {}
    if esxi_hosts:
        if not isinstance(esxi_hosts, list):
            raise CommandExecutionError("'esxi_hosts' must be a list.")

        for esxi_host in esxi_hosts:
            response = salt.utils.vmware.esxcli(
                host,
                username,
                password,
                cmd,
                protocol=protocol,
                port=port,
                esxi_host=esxi_host,
                credstore=credstore,
            )
            # format the response stdout into something useful
            ret.update({esxi_host: _format_syslog_config(response)})
    else:
        # Handles a single host or a vCenter connection when no esxi_hosts are provided.
        response = salt.utils.vmware.esxcli(
            host,
            username,
            password,
            cmd,
            protocol=protocol,
            port=port,
            credstore=credstore,
        )
        # format the response stdout into something useful
        ret.update({host: _format_syslog_config(response)})

    return ret


def reset_syslog_config(
    host,
    username,
    password,
    protocol=None,
    port=None,
    syslog_config=None,
    esxi_hosts=None,
    credstore=None,
):
    """
    Reset the syslog service to its default settings.

    Valid syslog_config values are ``logdir``, ``loghost``, ``logdir-unique``,
    ``default-rotate``, ``default-size``, ``default-timeout``,
    or ``all`` for all of these.

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

    syslog_config
        List of parameters to reset, provided as a comma-delimited string, or 'all' to
        reset all syslog configuration parameters. Required.

    esxi_hosts
        If ``host`` is a vCenter host, then use esxi_hosts to execute this function
        on a list of one or more ESXi machines.

    credstore
        Optionally set to path to the credential store file.

    :return: Dictionary with a top-level key of 'success' which indicates
             if all the parameters were reset, and individual keys
             for each parameter indicating which succeeded or failed, per host.

    CLI Example:

    ``syslog_config`` can be passed as a quoted, comma-separated string, e.g.

    .. code-block:: bash

        # Used for ESXi host connection information
        salt '*' vsphere.reset_syslog_config my.esxi.host root bad-password \
            syslog_config='logdir,loghost'

        # Used for connecting to a vCenter Server
        salt '*' vsphere.reset_syslog_config my.vcenter.location root bad-password \
            syslog_config='logdir,loghost' esxi_hosts='[esxi-1.host.com, esxi-2.host.com]'
    """
    if not syslog_config:
        raise CommandExecutionError(
            "The 'reset_syslog_config' function requires a " "'syslog_config' setting."
        )

    valid_resets = [
        "logdir",
        "loghost",
        "default-rotate",
        "default-size",
        "default-timeout",
        "logdir-unique",
    ]
    cmd = "system syslog config set --reset="
    if "," in syslog_config:
        resets = [ind_reset.strip() for ind_reset in syslog_config.split(",")]
    elif syslog_config == "all":
        resets = valid_resets
    else:
        resets = [syslog_config]

    ret = {}
    if esxi_hosts:
        if not isinstance(esxi_hosts, list):
            raise CommandExecutionError("'esxi_hosts' must be a list.")

        for esxi_host in esxi_hosts:
            response_dict = _reset_syslog_config_params(
                host,
                username,
                password,
                cmd,
                resets,
                valid_resets,
                protocol=protocol,
                port=port,
                esxi_host=esxi_host,
                credstore=credstore,
            )
            ret.update({esxi_host: response_dict})
    else:
        # Handles a single host or a vCenter connection when no esxi_hosts are provided.
        response_dict = _reset_syslog_config_params(
            host,
            username,
            password,
            cmd,
            resets,
            valid_resets,
            protocol=protocol,
            port=port,
            credstore=credstore,
        )
        ret.update({host: response_dict})

    return ret
