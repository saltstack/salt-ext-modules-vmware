# SPDX-License-Identifier: Apache-2.0
# pylint: disable=no-name-in-module
try:
    from pyVim.connect import GetSi, SmartConnect, Disconnect, GetStub, SoapStubAdapter
    from pyVmomi import vim, vmodl, VmomiSupport

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False

def get_si(f):
    def wraps():
        import ssl
        from pyVim import connect
        config = {
            "esxi_host_name": "10.206.240.192",
            "host": "10.206.240.167",
            "password": "VMware1!",
            "user": "administrator@vsphere.local",
        }
        ctx = ssl._create_unverified_context()
        return f(service_instance=connect.SmartConnect( 
        host=config["host"], user=config["user"], pwd=config["password"], sslContext=ctx
    ))
    return wraps