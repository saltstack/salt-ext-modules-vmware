# SPDX-License-Identifier: Apache-2.0
import os
import ssl

# pylint: disable=no-name-in-module
try:
    from pyVim import connect
    from pyVim.connect import GetSi, SmartConnect, Disconnect, GetStub, SoapStubAdapter
    from pyVmomi import vim, vmodl, VmomiSupport

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


def get_service_instance(opts=None, pillar=None):
    """
    Connect to VMware service instance

    Pillar Example:

    .. code-block::

        vmware_config:
            host: 198.51.100.100
            password: ****
            user: @example.com

    """
    ctx = ssl._create_unverified_context()
    host = (
        os.environ.get("VMWARE_CONFIG_HOST")
        or opts.get("vmware_config", {}).get("host")
        or pillar.get("vmware_config", {}).get("host")
    )
    password = (
        os.environ.get("VMWARE_CONFIG_PASSWORD")
        or opts.get("vmware_config", {}).get("password")
        or pillar.get("vmware_config", {}).get("password")
    )
    user = (
        os.environ.get("VMWARE_CONFIG_USER")
        or opts.get("vmware_config", {}).get("user")
        or pillar.get("vmware_config", {}).get("user")
    )
    config = {
        "host": host,
        "password": password,
        "user": user,
    }
    service_instance = connect.SmartConnect(
        host=config["host"],
        user=config["user"],
        pwd=config["password"],
        sslContext=ctx,
    )
    return service_instance
