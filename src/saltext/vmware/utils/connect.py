# SPDX-License-Identifier: Apache-2.0
import functools
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
        vmware_config:
            esxi_host_name: 10.100.100.100
            host: 10.100.100.100
            password: ****
            user: you@you.com

    """
    ctx = ssl._create_unverified_context()
    host = pillar["vmware_config"]["host"]
    password = pillar["vmware_config"]["password"]
    user = pillar["vmware_config"]["user"]
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
