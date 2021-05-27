# SPDX-License-Identifier: Apache-2.0

# Import python libs
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


def get_si(f):
    @functools.wraps(f)
    def wraps(*args, **kwargs):
        import ssl
        from pyVim import connect

        config = {
            "esxi_host_name": "10.206.240.192",
            "host": "10.206.240.210",
            "password": "VMware1!",
            "user": "administrator@vsphere.local",
        }
        ctx = ssl._create_unverified_context()
        f(
            service_instance=connect.SmartConnect(
                host=config["host"],
                user=config["user"],
                pwd=config["password"],
                sslContext=ctx,
            ),
            *args,
            **kwargs
        )

    return wraps


def get_service_instance(opts=None, pillar=None):

    ctx = ssl._create_unverified_context()
    config = {
        "host": "10.206.240.210",
        "password": "VMware1!",
        "user": "administrator@vsphere.local",
    }
    service_instance = connect.SmartConnect(
        host=config["host"],
        user=config["user"],
        pwd=config["password"],
        sslContext=ctx,
    )
    return service_instance
