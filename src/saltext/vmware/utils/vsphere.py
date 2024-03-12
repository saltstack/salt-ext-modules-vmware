# SPDX-License-Identifier: Apache-2.0
"""
Connection library for VMware

.. versionadded:: 2015.8.2

This is a base library used by a number of VMware services such as VMware
ESX, ESXi, and vCenter servers.

:codeauthor: Nitin Madhok <nmadhok@g.clemson.edu>
:codeauthor: Alexandru Bleotu <alexandru.bleotu@morganstanley.com>

Dependencies
~~~~~~~~~~~~

- pyVmomi Python Module
- ESXCLI: This dependency is only needed to use the ``esxcli`` function. No other
  functions in this module rely on ESXCLI.

pyVmomi
-------

PyVmomi can be installed via pip:

.. code-block:: bash

    pip install pyVmomi

.. note::

    Version 6.0 of pyVmomi has some problems with SSL error handling on certain
    versions of Python. If using version 6.0 of pyVmomi, Python 2.6,
    Python 2.7.9, or newer must be present. This is due to an upstream dependency
    in pyVmomi 6.0 that is not supported in Python versions 2.7 to 2.7.8. If the
    version of Python is not in the supported range, you will need to install an
    earlier version of pyVmomi. See `Issue #29537`_ for more information.

.. _Issue #29537: https://github.com/saltstack/salt/issues/29537

Based on the note above, to install an earlier version of pyVmomi than the
version currently listed in PyPi, run the following:

.. code-block:: bash

    pip install pyVmomi==5.5.0.2014.1.1

The 5.5.0.2014.1.1 is a known stable version that this original VMware utils file
was developed against.

ESXCLI
------

This dependency is only needed to use the ``esxcli`` function. At the time of this
writing, no other functions in this module rely on ESXCLI.

Once all of the required dependencies are in place and the vCLI package is
installed, you can check to see if you can connect to your ESXi host or vCenter
server by running the following command:

.. code-block:: bash

    esxcli -s <host-location> -u <username> -p <password> system syslog config get

If the connection was successful, ESXCLI was successfully installed on your system.
You should see output related to the ESXi host's syslog configuration.

"""
import atexit
import logging
import ssl

import salt.exceptions
import salt.modules.cmdmod
import salt.utils.path
import salt.utils.platform
import salt.utils.stringutils
import saltext.vmware.utils.cluster as utils_cluster
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.datacenter as utils_datacenter
import saltext.vmware.utils.datastore as utils_datastore

# pylint: disable=no-name-in-module
try:
    from pyVim.connect import GetSi, SmartConnect, Disconnect, GetStub, SoapStubAdapter
    from pyVmomi import vim, vmodl, VmomiSupport

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False

try:
    from com.vmware.vapi.std.errors_client import Unauthenticated
    from vmware.vapi.vsphere.client import create_vsphere_client

    HAS_VSPHERE_SDK = True

except ImportError:
    HAS_VSPHERE_SDK = False
# pylint: enable=no-name-in-module
try:
    import gssapi
    import base64

    HAS_GSSAPI = True
except ImportError:
    HAS_GSSAPI = False


log = logging.getLogger(__name__)


def __virtual__():
    """
    Only load if PyVmomi is installed.
    """
    if HAS_PYVMOMI:
        return True

    return False, "Missing dependency: The salt.utils.vmware module requires pyVmomi."


def get_vsphere_client(server, username, password, session=None, verify_ssl=True, ca_bundle=None):
    """
    Internal helper method to create an instance of the vSphere API client.
    Please provide username and password to authenticate.

    :param basestring server:
        vCenter host name or IP address
    :param basestring username:
        Name of the user
    :param basestring password:
        Password of the user
    :param Session session:
        Request HTTP session instance. If not specified, one
        is automatically created and used
    :param boolean verify_ssl:
        Verify the SSL certificate. Default: True
    :param basestring ca_bundle:
        Path to the ca bundle to use when verifying SSL certificates.

    :returns:
        Vsphere Client instance
    :rtype:
        :class:`vmware.vapi.vmc.client.VsphereClient`
    """
    if not session:
        # Create an https session to be used for a vSphere client
        session = salt.utils.http.session(verify_ssl=verify_ssl, ca_bundle=ca_bundle)
    client = None
    try:
        client = create_vsphere_client(
            server=server, username=username, password=password, session=session
        )
    except Unauthenticated as err:
        log.trace(err)
    return client


def _get_service_instance(
    host,
    username,
    password,
    protocol,
    port,
    mechanism,
    principal,
    domain,
    verify_ssl=True,
):
    """
    Internal method to authenticate with a vCenter server or ESX/ESXi host
    and return the service instance object.
    """
    log.trace("Retrieving new service instance")
    token = None
    if mechanism == "userpass":
        if username is None:
            raise salt.exceptions.CommandExecutionError(
                "Login mechanism userpass was specified but the mandatory "
                "parameter 'username' is missing"
            )
        if password is None:
            raise salt.exceptions.CommandExecutionError(
                "Login mechanism userpass was specified but the mandatory "
                "parameter 'password' is missing"
            )
    elif mechanism == "sspi":
        if principal is not None and domain is not None:
            try:
                token = get_gssapi_token(principal, host, domain)
            except Exception as exc:  # pylint: disable=broad-except
                raise salt.exceptions.VMwareConnectionError(str(exc))
        else:
            err_msg = (
                "Login mechanism '{}' was specified but the"
                " mandatory parameters are missing".format(mechanism)
            )
            raise salt.exceptions.CommandExecutionError(err_msg)
    else:
        raise salt.exceptions.CommandExecutionError("Unsupported mechanism: '{}'".format(mechanism))

    log.trace(
        "Connecting using the '%s' mechanism, with username '%s'",
        mechanism,
        username,
    )
    default_msg = (
        "Could not connect to host '{}'. "
        "Please check the debug log for more information.".format(host)
    )

    try:
        if verify_ssl:
            service_instance = SmartConnect(
                host=host,
                user=username,
                pwd=password,
                protocol=protocol,
                port=port,
                b64token=token,
                mechanism=mechanism,
            )
    except TypeError as exc:
        if "unexpected keyword argument" in exc.message:
            log.error("Initial connect to the VMware endpoint failed with %s", exc.message)
            log.error(
                "This may mean that a version of PyVmomi EARLIER than 6.0.0.2016.6 is installed."
            )
            log.error("We recommend updating to that version or later.")
            raise
    except Exception as exc:  # pylint: disable=broad-except
        # pyVmomi's SmartConnect() actually raises Exception in some cases.
        if (
            isinstance(exc, vim.fault.HostConnectFault)
            and "[SSL: CERTIFICATE_VERIFY_FAILED]" in exc.msg
        ) or "[SSL: CERTIFICATE_VERIFY_FAILED]" in str(exc):
            err_msg = (
                "Could not verify the SSL certificate. You can use "
                "verify_ssl: False if you do not want to verify the "
                "SSL certificate. This is not recommended as it is "
                "considered insecure."
            )
        else:
            log.exception(exc)
            err_msg = exc.msg if hasattr(exc, "msg") else default_msg
        raise salt.exceptions.VMwareConnectionError(err_msg)

    if not verify_ssl:
        try:
            service_instance = SmartConnect(
                host=host,
                user=username,
                pwd=password,
                protocol=protocol,
                port=port,
                sslContext=ssl._create_unverified_context(),
                b64token=token,
                mechanism=mechanism,
            )
        except Exception as exc:  # pylint: disable=broad-except
            # pyVmomi's SmartConnect() actually raises Exception in some cases.
            if "certificate verify failed" in str(exc):
                context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
                context.verify_mode = ssl.CERT_NONE
                try:
                    service_instance = SmartConnect(
                        host=host,
                        user=username,
                        pwd=password,
                        protocol=protocol,
                        port=port,
                        sslContext=context,
                        b64token=token,
                        mechanism=mechanism,
                    )
                except Exception as exc:  # pylint: disable=broad-except
                    log.exception(exc)
                    err_msg = exc.msg if hasattr(exc, "msg") else str(exc)
                    raise salt.exceptions.VMwareConnectionError(
                        "Could not connect to host '{}': " "{}".format(host, err_msg)
                    )
            else:
                err_msg = exc.msg if hasattr(exc, "msg") else default_msg
                log.trace(exc)
                raise salt.exceptions.VMwareConnectionError(err_msg)

    atexit.register(Disconnect, service_instance)
    return service_instance


def get_customizationspec_ref(si, customization_spec_name):
    """
    Get a reference to a VMware customization spec for the purposes of customizing a clone

    si
        ServiceInstance for the vSphere or ESXi server (see get_service_instance)

    customization_spec_name
        Name of the customization spec

    """
    customization_spec_name = si.content.customizationSpecManager.GetCustomizationSpec(
        name=customization_spec_name
    )
    return customization_spec_name


def get_mor_using_container_view(si, obj_type, obj_name):
    """
    Get reference to an object of specified object type and name

    si
        ServiceInstance for the vSphere or ESXi server (see get_service_instance)

    obj_type
        Type of the object (vim.StoragePod, vim.Datastore, etc)

    obj_name
        Name of the object

    """
    inventory = get_inventory(si)
    container = inventory.viewManager.CreateContainerView(inventory.rootFolder, [obj_type], True)
    for item in container.view:
        if item.name == obj_name:
            return item
    return None


def get_service_instance(
    host,
    username=None,
    password=None,
    protocol=None,
    port=None,
    mechanism="userpass",
    principal=None,
    domain=None,
    verify_ssl=True,
):
    """
    Authenticate with a vCenter server or ESX/ESXi host and return the service instance object.

    host
        The location of the vCenter server or ESX/ESXi host.

    username
        The username used to login to the vCenter server or ESX/ESXi host.
        Required if mechanism is ``userpass``

    password
        The password used to login to the vCenter server or ESX/ESXi host.
        Required if mechanism is ``userpass``

    protocol
        Optionally set to alternate protocol if the vCenter server or ESX/ESXi host is not
        using the default protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the vCenter server or ESX/ESXi host is not
        using the default port. Default port is ``443``.

    mechanism
        pyVmomi connection mechanism. Can either be ``userpass`` or ``sspi``.
        Default mechanism is ``userpass``.

    principal
        Kerberos service principal. Required if mechanism is ``sspi``

    domain
        Kerberos user domain. Required if mechanism is ``sspi``

    verify_ssl
        Verify the SSL certificate. Default: True
    """

    if protocol is None:
        protocol = "https"
    if port is None:
        port = 443

    service_instance = GetSi()
    if service_instance:
        stub = GetStub()
        if salt.utils.platform.is_proxy() or (
            hasattr(stub, "host") and stub.host != ":".join([host, str(port)])
        ):
            # Proxies will fork and mess up the cached service instance.
            # If this is a proxy or we are connecting to a different host
            # invalidate the service instance to avoid a potential memory leak
            # and reconnect
            Disconnect(service_instance)
            service_instance = None

    if not service_instance:
        service_instance = _get_service_instance(
            host,
            username,
            password,
            protocol,
            port,
            mechanism,
            principal,
            domain,
            verify_ssl=verify_ssl,
        )

    # Test if data can actually be retrieved or connection has gone stale
    log.trace("Checking connection is still authenticated")
    try:
        service_instance.CurrentTime()
    except vim.fault.NotAuthenticated:
        log.trace("Session no longer authenticating. Reconnecting")
        Disconnect(service_instance)
        service_instance = _get_service_instance(
            host,
            username,
            password,
            protocol,
            port,
            mechanism,
            principal,
            domain,
            verify_ssl=verify_ssl,
        )
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)

    return service_instance


def get_new_service_instance_stub(service_instance, path, ns=None, version=None):
    """
    Returns a stub that points to a different path,
    created from an existing connection.

    service_instance
        The Service Instance.

    path
        Path of the new stub.

    ns
        Namespace of the new stub.
        Default value is None

    version
        Version of the new stub.
        Default value is None.
    """
    # For python 2.7.9 and later, the default SSL context has more strict
    # connection handshaking rule. We may need turn off the hostname checking
    # and the client side cert verification.
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    stub = service_instance._stub
    hostname = stub.host.split(":")[0]
    session_cookie = stub.cookie.split('"')[1]
    VmomiSupport.GetRequestContext()["vcSessionCookie"] = session_cookie
    new_stub = SoapStubAdapter(
        host=hostname, ns=ns, path=path, version=version, poolSize=0, sslContext=context
    )
    new_stub.cookie = stub.cookie
    return new_stub


def disconnect(service_instance):
    """
    Function that disconnects from the vCenter server or ESXi host

    service_instance
        The Service Instance from which to obtain managed object references.
    """
    log.trace("Disconnecting")
    try:
        Disconnect(service_instance)
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)


def is_connection_to_a_vcenter(service_instance):
    """
    Function that returns True if the connection is made to a vCenter Server and
    False if the connection is made to an ESXi host

    service_instance
        The Service Instance from which to obtain managed object references.
    """
    try:
        api_type = service_instance.content.about.apiType
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    log.trace("api_type = %s", api_type)
    if api_type == "VirtualCenter":
        return True
    elif api_type == "HostAgent":
        return False
    else:
        raise salt.exceptions.VMwareApiError(
            "Unexpected api type '{}' . Supported types: "
            "'VirtualCenter/HostAgent'".format(api_type)
        )


def get_service_info(service_instance):
    """
    Returns information of the vCenter or ESXi host

    service_instance
        The Service Instance from which to obtain managed object references.
    """
    try:
        return service_instance.content.about
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)


def _get_dvs(service_instance, dvs_name):
    """
    Return a reference to a Distributed Virtual Switch object.

    :param service_instance: PyVmomi service instance
    :param dvs_name: Name of DVS to return
    :return: A PyVmomi DVS object
    """
    switches = list_dvs(service_instance)
    if dvs_name in switches:
        inventory = get_inventory(service_instance)
        container = inventory.viewManager.CreateContainerView(
            inventory.rootFolder, [vim.DistributedVirtualSwitch], True
        )
        for item in container.view:
            if item.name == dvs_name:
                return item

    return None


def _get_dvs_by_uuid(service_instance, dvs_uuid):
    """
    Return a reference to a Distributed Virtual Switch object.
    :param service_instance: PyVmomi service instance
    :param dvs_uuid: UUID of DVS to return
    :return: A PyVmomi DVS object
    """
    switches = list_dvs(service_instance, ["uuid"])
    if dvs_uuid in switches:
        inventory = get_inventory(service_instance)
        container = inventory.viewManager.CreateContainerView(
            inventory.rootFolder, [vim.DistributedVirtualSwitch], True
        )
        for item in container.view:
            if item.uuid == dvs_uuid:
                return item

    return None


def _get_pnics(host_reference):
    """
    Helper function that returns a list of PhysicalNics and their information.
    """
    return host_reference.config.network.pnic


def _get_vnics(host_reference):
    """
    Helper function that returns a list of VirtualNics and their information.
    """
    return host_reference.config.network.vnic


def _get_vnic_manager(host_reference):
    """
    Helper function that returns a list of Virtual NicManagers
    and their information.
    """
    return host_reference.configManager.virtualNicManager


def _get_dvs_portgroup(dvs, portgroup_name):
    """
    Return a portgroup object corresponding to the portgroup name on the dvs

    :param dvs: DVS object
    :param portgroup_name: Name of portgroup to return
    :return: Portgroup object
    """
    for portgroup in dvs.portgroup:
        if portgroup.name == portgroup_name:
            return portgroup

    return None


def _get_dvs_uplink_portgroup(dvs, portgroup_name):
    """
    Return a portgroup object corresponding to the portgroup name on the dvs

    :param dvs: DVS object
    :param portgroup_name: Name of portgroup to return
    :return: Portgroup object
    """
    for portgroup in dvs.portgroup:
        if portgroup.name == portgroup_name:
            return portgroup

    return None


def get_gssapi_token(principal, host, domain):
    """
    Get the gssapi token for Kerberos connection

    principal
       The service principal
    host
       Host url where we would like to authenticate
    domain
       Kerberos user domain
    """

    if not HAS_GSSAPI:
        raise ImportError("The gssapi library is not imported.")

    service = "{}/{}@{}".format(principal, host, domain)
    log.debug("Retrieving gsspi token for service %s", service)
    service_name = gssapi.Name(service, gssapi.C_NT_USER_NAME)
    ctx = gssapi.InitContext(service_name)
    in_token = None
    while not ctx.established:
        out_token = ctx.step(in_token)
        if out_token:
            return base64.b64encode(salt.utils.stringutils.to_bytes(out_token))
        if ctx.established:
            break
        if not in_token:
            raise salt.exceptions.CommandExecutionError(
                "Can't receive token, no response from server"
            )
    raise salt.exceptions.CommandExecutionError("Context established, but didn't receive token")


def get_hardware_grains(service_instance):
    """
    Return hardware info for standard minion grains if the service_instance is a HostAgent type

    service_instance
        The service instance object to get hardware info for

    .. versionadded:: 2016.11.0
    """
    hw_grain_data = {}
    if get_inventory(service_instance).about.apiType == "HostAgent":
        view = service_instance.content.viewManager.CreateContainerView(
            service_instance.RetrieveContent().rootFolder, [vim.HostSystem], True
        )
        if view and view.view:
            hw_grain_data["manufacturer"] = view.view[0].hardware.systemInfo.vendor
            hw_grain_data["productname"] = view.view[0].hardware.systemInfo.model

            for _data in view.view[0].hardware.systemInfo.otherIdentifyingInfo:
                if _data.identifierType.key == "ServiceTag":
                    hw_grain_data["serialnumber"] = _data.identifierValue

            hw_grain_data["osfullname"] = view.view[0].summary.config.product.fullName
            hw_grain_data["osmanufacturer"] = view.view[0].summary.config.product.vendor
            hw_grain_data["osrelease"] = view.view[0].summary.config.product.version
            hw_grain_data["osbuild"] = view.view[0].summary.config.product.build
            hw_grain_data["os_family"] = view.view[0].summary.config.product.name
            hw_grain_data["os"] = view.view[0].summary.config.product.name
            hw_grain_data["mem_total"] = view.view[0].hardware.memorySize / 1024 / 1024
            hw_grain_data["biosversion"] = view.view[0].hardware.biosInfo.biosVersion
            hw_grain_data["biosreleasedate"] = (
                view.view[0].hardware.biosInfo.releaseDate.date().strftime("%m/%d/%Y")
            )
            hw_grain_data["cpu_model"] = view.view[0].hardware.cpuPkg[0].description
            hw_grain_data["kernel"] = view.view[0].summary.config.product.productLineId
            hw_grain_data["num_cpu_sockets"] = view.view[0].hardware.cpuInfo.numCpuPackages
            hw_grain_data["num_cpu_cores"] = view.view[0].hardware.cpuInfo.numCpuCores
            hw_grain_data["num_cpus"] = (
                hw_grain_data["num_cpu_sockets"] * hw_grain_data["num_cpu_cores"]
            )
            hw_grain_data["ip_interfaces"] = {}
            hw_grain_data["ip4_interfaces"] = {}
            hw_grain_data["ip6_interfaces"] = {}
            hw_grain_data["hwaddr_interfaces"] = {}
            for _vnic in view.view[0].configManager.networkSystem.networkConfig.vnic:
                hw_grain_data["ip_interfaces"][_vnic.device] = []
                hw_grain_data["ip4_interfaces"][_vnic.device] = []
                hw_grain_data["ip6_interfaces"][_vnic.device] = []

                hw_grain_data["ip_interfaces"][_vnic.device].append(_vnic.spec.ip.ipAddress)
                hw_grain_data["ip4_interfaces"][_vnic.device].append(_vnic.spec.ip.ipAddress)
                if _vnic.spec.ip.ipV6Config:
                    hw_grain_data["ip6_interfaces"][_vnic.device].append(
                        _vnic.spec.ip.ipV6Config.ipV6Address
                    )
                hw_grain_data["hwaddr_interfaces"][_vnic.device] = _vnic.spec.mac
            hw_grain_data["host"] = view.view[0].configManager.networkSystem.dnsConfig.hostName
            hw_grain_data["domain"] = view.view[0].configManager.networkSystem.dnsConfig.domainName
            hw_grain_data["fqdn"] = "{}{}{}".format(
                view.view[0].configManager.networkSystem.dnsConfig.hostName,
                ("." if view.view[0].configManager.networkSystem.dnsConfig.domainName else ""),
                view.view[0].configManager.networkSystem.dnsConfig.domainName,
            )

            for _pnic in view.view[0].configManager.networkSystem.networkInfo.pnic:
                hw_grain_data["hwaddr_interfaces"][_pnic.device] = _pnic.mac

            hw_grain_data["timezone"] = view.view[
                0
            ].configManager.dateTimeSystem.dateTimeInfo.timeZone.name
        view = None
    return hw_grain_data


def get_inventory(service_instance):
    """
    Return the inventory of a Service Instance Object.

    service_instance
        The Service Instance Object for which to obtain inventory.
    """
    return service_instance.RetrieveContent()


def get_network_adapter_type(adapter_type):
    """
    Return the network adapter type.

    adpater_type
        The adapter type from which to obtain the network adapter type.
    """
    if adapter_type == "vmxnet":
        return vim.vm.device.VirtualVmxnet()
    elif adapter_type == "vmxnet2":
        return vim.vm.device.VirtualVmxnet2()
    elif adapter_type == "vmxnet3":
        return vim.vm.device.VirtualVmxnet3()
    elif adapter_type == "e1000":
        return vim.vm.device.VirtualE1000()
    elif adapter_type == "e1000e":
        return vim.vm.device.VirtualE1000e()

    raise ValueError("An unknown network adapter object type name.")


def get_network_adapter_object_type(adapter_object):
    """
    Returns the network adapter type.

    adapter_object
        The adapter object from which to obtain the network adapter type.
    """
    if isinstance(adapter_object, vim.vm.device.VirtualVmxnet2):
        return "vmxnet2"
    if isinstance(adapter_object, vim.vm.device.VirtualVmxnet3):
        return "vmxnet3"
    if isinstance(adapter_object, vim.vm.device.VirtualVmxnet):
        return "vmxnet"
    if isinstance(adapter_object, vim.vm.device.VirtualE1000e):
        return "e1000e"
    if isinstance(adapter_object, vim.vm.device.VirtualE1000):
        return "e1000"

    raise ValueError("An unknown network adapter object type.")


def get_dvss(dc_ref, dvs_names=None, get_all_dvss=False):
    """
    Returns distributed virtual switches (DVSs) in a datacenter.

    dc_ref
        The parent datacenter reference.

    dvs_names
        The names of the DVSs to return. Default is None.

    get_all_dvss
        Return all DVSs in the datacenter. Default is False.
    """
    dc_name = utils_common.get_managed_object_name(dc_ref)
    log.trace(
        "Retrieving DVSs in datacenter '%s', dvs_names='%s', get_all_dvss=%s",
        dc_name,
        ",".join(dvs_names) if dvs_names else None,
        get_all_dvss,
    )
    properties = ["name"]
    traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(
        path="networkFolder",
        skip=True,
        type=vim.Datacenter,
        selectSet=[
            vmodl.query.PropertyCollector.TraversalSpec(
                path="childEntity", skip=False, type=vim.Folder
            )
        ],
    )
    service_instance = utils_common.get_service_instance_from_managed_object(dc_ref)
    items = [
        i["object"]
        for i in utils_common.get_mors_with_properties(
            service_instance,
            vim.DistributedVirtualSwitch,
            container_ref=dc_ref,
            property_list=properties,
            traversal_spec=traversal_spec,
        )
        if get_all_dvss or (dvs_names and i["name"] in dvs_names)
    ]
    return items


def get_network_folder(dc_ref):
    """
    Retrieves the network folder of a datacenter
    """
    dc_name = utils_common.get_managed_object_name(dc_ref)
    log.trace("Retrieving network folder in datacenter '%s'", dc_name)
    service_instance = utils_common.get_service_instance_from_managed_object(dc_ref)
    traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(
        path="networkFolder", skip=False, type=vim.Datacenter
    )
    entries = utils_common.get_mors_with_properties(
        service_instance,
        vim.Folder,
        container_ref=dc_ref,
        property_list=["name"],
        traversal_spec=traversal_spec,
    )
    if not entries:
        raise salt.exceptions.VMwareObjectRetrievalError(
            "Network folder in datacenter '{}' wasn't retrieved" "".format(dc_name)
        )
    return entries[0]["object"]


def create_dvs(dc_ref, dvs_name, dvs_create_spec=None):
    """
    Creates a distributed virtual switches (DVS) in a datacenter.
    Returns the reference to the newly created distributed virtual switch.

    dc_ref
        The parent datacenter reference.

    dvs_name
        The name of the DVS to create.

    dvs_create_spec
        The DVS spec (vim.DVSCreateSpec) to use when creating the DVS.
        Default is None.
    """
    dc_name = utils_common.get_managed_object_name(dc_ref)
    log.trace("Creating DVS '%s' in datacenter '%s'", dvs_name, dc_name)
    if not dvs_create_spec:
        dvs_create_spec = vim.DVSCreateSpec()
    if not dvs_create_spec.configSpec:
        dvs_create_spec.configSpec = vim.VMwareDVSConfigSpec()
        dvs_create_spec.configSpec.name = dvs_name
    netw_folder_ref = get_network_folder(dc_ref)
    try:
        task = netw_folder_ref.CreateDVS_Task(dvs_create_spec)
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    utils_common.wait_for_task(task, dvs_name, str(task.__class__))


def update_dvs(dvs_ref, dvs_config_spec):
    """
    Updates a distributed virtual switch with the config_spec.

    dvs_ref
        The DVS reference.

    dvs_config_spec
        The updated config spec (vim.VMwareDVSConfigSpec) to be applied to
        the DVS.
    """
    dvs_name = utils_common.get_managed_object_name(dvs_ref)
    log.trace("Updating dvs '%s'", dvs_name)
    try:
        task = dvs_ref.ReconfigureDvs_Task(dvs_config_spec)
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    utils_common.wait_for_task(task, dvs_name, str(task.__class__))


def update_dvs_version(dvs_ref, dvs_product_spec):
    """
    Updates a distributed virtual switch version with the product spec.

    dvs_ref
        The DVS reference.

    dvs_product_spec
        The updated config spec (vim.dvs.ProductSpec()) to be applied to
        the DVS.
    """
    dvs_name = utils_common.get_managed_object_name(dvs_ref)
    log.trace("Updating dvs '%s'", dvs_name)
    try:
        task = dvs_ref.PerformDvsProductSpecOperation_Task("upgrade", dvs_product_spec)
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    utils_common.wait_for_task(task, dvs_name, str(task.__class__))


def update_dvs_health(dvs_ref, dvs_health_spec):
    """
    Updates a distributed virtual switch health checks with the health spec.

    dvs_ref
        The DVS reference.

    dvs_health_spec
        The updated config spec to be applied to the DVS.
    """
    dvs_name = utils_common.get_managed_object_name(dvs_ref)
    log.trace("Updating dvs '%s'", dvs_name)
    try:
        task = dvs_ref.UpdateDVSHealthCheckConfig_Task(healthCheckConfig=dvs_health_spec)
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    utils_common.wait_for_task(task, dvs_name, str(task.__class__))


def set_dvs_network_resource_management_enabled(dvs_ref, enabled):
    """
    Sets whether NIOC is enabled on a DVS.

    dvs_ref
        The DVS reference.

    enabled
        Flag specifying whether NIOC is enabled.
    """
    dvs_name = utils_common.get_managed_object_name(dvs_ref)
    log.trace(
        "Setting network resource management enable to %s on " "dvs '%s'",
        enabled,
        dvs_name,
    )
    try:
        dvs_ref.EnableNetworkResourceManagement(enable=enabled)
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)


def get_dvportgroups(parent_ref, portgroup_names=None, get_all_portgroups=False):
    """
    Returns distributed virtual porgroups (dvportgroups).
    The parent object can be either a datacenter or a dvs.

    parent_ref
        The parent object reference. Can be either a datacenter or a dvs.

    portgroup_names
        The names of the dvss to return. Default is None.

    get_all_portgroups
        Return all portgroups in the parent. Default is False.
    """
    if not isinstance(parent_ref, (vim.Datacenter, vim.DistributedVirtualSwitch)):
        raise salt.exceptions.ArgumentValueError(
            "Parent has to be either a datacenter, " "or a distributed virtual switch"
        )
    parent_name = utils_common.get_managed_object_name(parent_ref)
    log.trace(
        "Retrieving portgroup in %s '%s', portgroups_names='%s', " "get_all_portgroups=%s",
        type(parent_ref).__name__,
        parent_name,
        ",".join(portgroup_names) if portgroup_names else None,
        get_all_portgroups,
    )
    properties = ["name"]
    if isinstance(parent_ref, vim.Datacenter):
        traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(
            path="networkFolder",
            skip=True,
            type=vim.Datacenter,
            selectSet=[
                vmodl.query.PropertyCollector.TraversalSpec(
                    path="childEntity", skip=False, type=vim.Folder
                )
            ],
        )
    else:  # parent is distributed virtual switch
        traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(
            path="portgroup", skip=False, type=vim.DistributedVirtualSwitch
        )

    service_instance = utils_common.get_service_instance_from_managed_object(parent_ref)
    items = [
        i["object"]
        for i in utils_common.get_mors_with_properties(
            service_instance,
            vim.DistributedVirtualPortgroup,
            container_ref=parent_ref,
            property_list=properties,
            traversal_spec=traversal_spec,
        )
        if get_all_portgroups or (portgroup_names and i["name"] in portgroup_names)
    ]
    return items


def get_uplink_dvportgroup(dvs_ref):
    """
    Returns the uplink distributed virtual portgroup of a distributed virtual
    switch (dvs)

    dvs_ref
        The dvs reference
    """
    dvs_name = utils_common.get_managed_object_name(dvs_ref)
    log.trace("Retrieving uplink portgroup of dvs '%s'", dvs_name)
    traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(
        path="portgroup", skip=False, type=vim.DistributedVirtualSwitch
    )
    service_instance = utils_common.get_service_instance_from_managed_object(dvs_ref)
    items = [
        entry["object"]
        for entry in utils_common.get_mors_with_properties(
            service_instance,
            vim.DistributedVirtualPortgroup,
            container_ref=dvs_ref,
            property_list=["tag"],
            traversal_spec=traversal_spec,
        )
        if entry["tag"] and [t for t in entry["tag"] if t.key == "SYSTEM/DVS.UPLINKPG"]
    ]
    if not items:
        raise salt.exceptions.VMwareObjectRetrievalError(
            "Uplink portgroup of DVS '{}' wasn't found".format(dvs_name)
        )
    return items[0]


def create_dvportgroup(dvs_ref, spec):
    """
    Creates a distributed virtual portgroup on a distributed virtual switch
    (dvs)

    dvs_ref
        The dvs reference

    spec
        Portgroup spec (vim.DVPortgroupConfigSpec)
    """
    dvs_name = utils_common.get_managed_object_name(dvs_ref)
    log.trace("Adding portgroup %s to dvs '%s'", spec.name, dvs_name)
    log.trace("spec = %s", spec)
    try:
        task = dvs_ref.CreateDVPortgroup_Task(spec)
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    utils_common.wait_for_task(task, dvs_name, str(task.__class__))


def update_dvportgroup(portgroup_ref, spec):
    """
    Updates a distributed virtual portgroup

    portgroup_ref
        The portgroup reference

    spec
        Portgroup spec (vim.DVPortgroupConfigSpec)
    """
    pg_name = utils_common.get_managed_object_name(portgroup_ref)
    log.trace("Updating portgrouo %s", pg_name)
    try:
        task = portgroup_ref.ReconfigureDVPortgroup_Task(spec)
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    utils_common.wait_for_task(task, pg_name, str(task.__class__))


def remove_dvportgroup(portgroup_ref):
    """
    Removes a distributed virtual portgroup

    portgroup_ref
        The portgroup reference
    """
    pg_name = utils_common.get_managed_object_name(portgroup_ref)
    log.trace("Removing portgroup %s", pg_name)
    try:
        task = portgroup_ref.Destroy_Task()
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    utils_common.wait_for_task(task, pg_name, str(task.__class__))


def get_networks(parent_ref, network_names=None, get_all_networks=False):
    """
    Returns networks of standard switches.
    The parent object can be a datacenter.

    parent_ref
        The parent object reference. A datacenter object.

    network_names
        The name of the standard switch networks. Default is None.

    get_all_networks
        Boolean indicates whether to return all networks in the parent.
        Default is False.
    """

    if not isinstance(parent_ref, vim.Datacenter):
        raise salt.exceptions.ArgumentValueError("Parent has to be a datacenter.")
    parent_name = utils_common.get_managed_object_name(parent_ref)
    log.trace(
        "Retrieving network from %s '%s', network_names='%s', " "get_all_networks=%s",
        type(parent_ref).__name__,
        parent_name,
        ",".join(network_names) if network_names else None,
        get_all_networks,
    )
    properties = ["name"]
    service_instance = utils_common.get_service_instance_from_managed_object(parent_ref)
    traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(
        path="networkFolder",
        skip=True,
        type=vim.Datacenter,
        selectSet=[
            vmodl.query.PropertyCollector.TraversalSpec(
                path="childEntity", skip=False, type=vim.Folder
            )
        ],
    )
    items = [
        i["object"]
        for i in utils_common.get_mors_with_properties(
            service_instance,
            vim.Network,
            container_ref=parent_ref,
            property_list=properties,
            traversal_spec=traversal_spec,
        )
        if get_all_networks or (network_names and i["name"] in network_names)
    ]
    return items


def get_license_manager(service_instance):
    """
    Returns the license manager.

    service_instance
        The Service Instance Object from which to obrain the license manager.
    """

    log.debug("Retrieving license manager")
    try:
        lic_manager = service_instance.content.licenseManager
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    return lic_manager


def get_license_assignment_manager(service_instance):
    """
    Returns the license assignment manager.

    service_instance
        The Service Instance Object from which to obrain the license manager.
    """

    log.debug("Retrieving license assignment manager")
    try:
        lic_assignment_manager = service_instance.content.licenseManager.licenseAssignmentManager
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    if not lic_assignment_manager:
        raise salt.exceptions.VMwareObjectRetrievalError(
            "License assignment manager was not retrieved"
        )
    return lic_assignment_manager


def get_licenses(service_instance, license_manager=None):
    """
    Returns the licenses on a specific instance.

    service_instance
        The Service Instance Object from which to obrain the licenses.

    license_manager
        The License Manager object of the service instance. If not provided it
        will be retrieved.
    """

    if not license_manager:
        license_manager = get_license_manager(service_instance)
    log.debug("Retrieving licenses")
    try:
        return license_manager.licenses
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)


def add_license(service_instance, key, description, license_manager=None):
    """
    Adds a license.

    service_instance
        The Service Instance Object.

    key
        The key of the license to add.

    description
        The description of the license to add.

    license_manager
        The License Manager object of the service instance. If not provided it
        will be retrieved.
    """
    if not license_manager:
        license_manager = get_license_manager(service_instance)
    label = vim.KeyValue()
    label.key = "VpxClientLicenseLabel"
    label.value = description
    log.debug("Adding license '%s'", description)
    try:
        vmware_license = license_manager.AddLicense(key, [label])
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    return vmware_license


def get_assigned_licenses(
    service_instance, entity_ref=None, entity_name=None, license_assignment_manager=None
):
    """
    Returns the licenses assigned to an entity. If entity ref is not provided,
    then entity_name is assumed to be the vcenter. This is later checked if
    the entity name is provided.

    service_instance
        The Service Instance Object from which to obtain the licenses.

    entity_ref
        VMware entity to get the assigned licenses for.
        If None, the entity is the vCenter itself.
        Default is None.

    entity_name
        Entity name used in logging.
        Default is None.

    license_assignment_manager
        The LicenseAssignmentManager object of the service instance.
        If not provided it will be retrieved.
        Default is None.
    """
    if not license_assignment_manager:
        license_assignment_manager = get_license_assignment_manager(service_instance)
    if not entity_name:
        raise salt.exceptions.ArgumentValueError("No entity_name passed")
    # If entity_ref is not defined, then interested in the vcenter
    entity_id = None
    entity_type = "moid"
    check_name = False
    if not entity_ref:
        if entity_name:
            check_name = True
        entity_type = "uuid"
        try:
            entity_id = service_instance.content.about.instanceUuid
        except vim.fault.NoPermission as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareApiError(
                "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
            )
        except vim.fault.VimFault as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareApiError(exc.msg)
        except vmodl.RuntimeFault as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareRuntimeError(exc.msg)
    else:
        entity_id = entity_ref._moId

    log.trace("Retrieving licenses assigned to '%s'", entity_name)
    try:
        assignments = license_assignment_manager.QueryAssignedLicenses(entity_id)
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)

    if entity_type == "uuid" and len(assignments) > 1:
        log.trace("Unexpectectedly retrieved more than one" " VCenter license assignment.")
        raise salt.exceptions.VMwareObjectRetrievalError(
            "Unexpected return. Expect only a single assignment"
        )

    if check_name:
        if entity_name != assignments[0].entityDisplayName:
            log.trace(
                "Getting license info for wrong vcenter: %s != %s",
                entity_name,
                assignments[0].entityDisplayName,
            )
            raise salt.exceptions.VMwareObjectRetrievalError(
                "Got license assignment info for a different vcenter"
            )

    return [a.assignedLicense for a in assignments]


def assign_license(
    service_instance,
    license_key,
    license_name,
    entity_ref=None,
    entity_name=None,
    license_assignment_manager=None,
):
    """
    Assigns a license to an entity.

    service_instance
        The Service Instance Object from which to obrain the licenses.

    license_key
        The key of the license to add.

    license_name
        The description of the license to add.

    entity_ref
        VMware entity to assign the license to.
        If None, the entity is the vCenter itself.
        Default is None.

    entity_name
        Entity name used in logging.
        Default is None.

    license_assignment_manager
        The LicenseAssignmentManager object of the service instance.
        If not provided it will be retrieved
        Default is None.
    """
    if not license_assignment_manager:
        license_assignment_manager = get_license_assignment_manager(service_instance)
    entity_id = None

    if not entity_ref:
        # vcenter
        try:
            entity_id = service_instance.content.about.instanceUuid
        except vim.fault.NoPermission as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareApiError(
                "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
            )
        except vim.fault.VimFault as exc:
            raise salt.exceptions.VMwareApiError(exc.msg)
        except vmodl.RuntimeFault as exc:
            raise salt.exceptions.VMwareRuntimeError(exc.msg)
        if not entity_name:
            entity_name = "vCenter"
    else:
        # e.g. vsan cluster or host
        entity_id = entity_ref._moId

    log.trace("Assigning license to '%s'", entity_name)
    try:
        vmware_license = license_assignment_manager.UpdateAssignedLicense(
            entity_id, license_key, license_name
        )
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    return vmware_license


def list_datastore_clusters(service_instance):
    """
    Returns a list of datastore clusters associated with a given service instance.

    service_instance
        The Service Instance Object from which to obtain datastore clusters.
    """
    return utils_common.list_objects(service_instance, vim.StoragePod)


def list_datastores(service_instance):
    """
    Returns a list of datastores associated with a given service instance.

    service_instance
        The Service Instance Object from which to obtain datastores.
    """
    return utils_common.list_objects(service_instance, vim.Datastore)


def get_datastore_files(service_instance, directory, datastores, container_object, browser_spec):
    """
    Get the files with a given browser specification from the datastore.

    service_instance
        The Service Instance Object from which to obtain datastores.

    directory
        The name of the directory where we would like to search

    datastores
        Name of the datastores

    container_object
        The base object for searches

    browser_spec
        BrowserSpec object which defines the search criteria

    return
        list of vim.host.DatastoreBrowser.SearchResults objects
    """

    files = []
    datastore_objects = utils_datastore.get_datastores_by_ref(
        service_instance, container_object, datastore_names=datastores
    )
    for datobj in datastore_objects:
        try:
            task = datobj.browser.SearchDatastore_Task(
                datastorePath="[{}] {}".format(datobj.name, directory),
                searchSpec=browser_spec,
            )
        except vim.fault.NoPermission as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareApiError(
                "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
            )
        except vim.fault.VimFault as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareApiError(exc.msg)
        except vmodl.RuntimeFault as exc:
            log.exception(exc)
            raise salt.exceptions.VMwareRuntimeError(exc.msg)
        try:
            files.append(
                salt.utils.vmware.utils_common.wait_for_task(
                    task, directory, "query virtual machine files"
                )
            )
        except salt.exceptions.VMwareFileNotFoundError:
            pass
    return files


def rename_datastore(datastore_ref, new_datastore_name):
    """
    Renames a datastore

    datastore_ref
        vim.Datastore reference to the datastore object to be changed

    new_datastore_name
        New datastore name
    """
    ds_name = utils_common.get_managed_object_name(datastore_ref)
    log.trace("Renaming datastore '%s' to '%s'", ds_name, new_datastore_name)
    try:
        datastore_ref.RenameDatastore(new_datastore_name)
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)


def _get_partition_info(storage_system, device_path):
    """
    Returns partition information for a device path, of type
    vim.HostDiskPartitionInfo
    """
    try:
        partition_infos = storage_system.RetrieveDiskPartitionInfo(devicePath=[device_path])
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    log.trace("partition_info = %s", partition_infos[0])
    return partition_infos[0]


def _get_new_computed_partition_spec(storage_system, device_path, partition_info):
    """
    Computes the new disk partition info when adding a new vmfs partition that
    uses up the remainder of the disk; returns a tuple
    (new_partition_number, vim.HostDiskPartitionSpec
    """
    log.trace(
        "Adding a partition at the end of the disk and getting the new " "computed partition spec"
    )
    # TODO implement support for multiple partitions
    # We support adding a partition add the end of the disk with partitions
    free_partitions = [p for p in partition_info.layout.partition if p.type == "none"]
    if not free_partitions:
        raise salt.exceptions.VMwareObjectNotFoundError(
            "Free partition was not found on device '{}'" "".format(partition_info.deviceName)
        )
    free_partition = free_partitions[0]

    # Create a layout object that copies the existing one
    layout = vim.HostDiskPartitionLayout(
        total=partition_info.layout.total, partition=partition_info.layout.partition
    )
    # Create a partition with the free space on the disk
    # Change the free partition type to vmfs
    free_partition.type = "vmfs"
    try:
        computed_partition_info = storage_system.ComputeDiskPartitionInfo(
            devicePath=device_path,
            partitionFormat=vim.HostDiskPartitionInfoPartitionFormat.gpt,
            layout=layout,
        )
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    log.trace("computed partition info = {0}", computed_partition_info)
    log.trace("Retrieving new partition number")
    partition_numbers = [
        p.partition
        for p in computed_partition_info.layout.partition
        if (
            p.start.block == free_partition.start.block
            or
            # XXX If the entire disk is free (i.e. the free
            # disk partition starts at block 0) the newily
            # created partition is created from block 1
            (free_partition.start.block == 0 and p.start.block == 1)
        )
        and p.end.block == free_partition.end.block
        and p.type == "vmfs"
    ]
    if not partition_numbers:
        raise salt.exceptions.VMwareNotFoundError(
            "New partition was not found in computed partitions of device "
            "'{}'".format(partition_info.deviceName)
        )
    log.trace("new partition number = %s", partition_numbers[0])
    return (partition_numbers[0], computed_partition_info.spec)


def create_vmfs_datastore(
    host_ref, datastore_name, disk_ref, vmfs_major_version, storage_system=None
):
    """
    Creates a VMFS datastore from a disk_id

    host_ref
        vim.HostSystem object referencing a host to create the datastore on

    datastore_name
        Name of the datastore

    disk_ref
        vim.HostScsiDislk on which the datastore is created

    vmfs_major_version
        VMFS major version to use
    """
    # TODO Support variable sized partitions
    hostname = utils_common.get_managed_object_name(host_ref)
    disk_id = disk_ref.canonicalName
    log.debug(
        "Creating datastore '%s' on host '%s', scsi disk '%s', " "vmfs v%s",
        datastore_name,
        hostname,
        disk_id,
        vmfs_major_version,
    )
    if not storage_system:
        si = utils_common.get_service_instance_from_managed_object(host_ref, name=hostname)
        storage_system = utils_datastore.get_storage_system(si, host_ref, hostname)

    target_disk = disk_ref
    partition_info = _get_partition_info(storage_system, target_disk.devicePath)
    log.trace("partition_info = %s", partition_info)
    new_partition_number, partition_spec = _get_new_computed_partition_spec(
        storage_system, target_disk.devicePath, partition_info
    )
    spec = vim.VmfsDatastoreCreateSpec(
        vmfs=vim.HostVmfsSpec(
            majorVersion=vmfs_major_version,
            volumeName=datastore_name,
            extent=vim.HostScsiDiskPartition(diskName=disk_id, partition=new_partition_number),
        ),
        diskUuid=target_disk.uuid,
        partition=partition_spec,
    )
    try:
        ds_ref = host_ref.configManager.datastoreSystem.CreateVmfsDatastore(spec)
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    log.debug("Created datastore '%s' on host '%s'", datastore_name, hostname)
    return ds_ref


def get_host_datastore_system(host_ref, hostname=None):
    """
    Returns a host's datastore system

    host_ref
        Reference to the ESXi host

    hostname
        Name of the host. This argument is optional.
    """

    if not hostname:
        hostname = utils_common.get_managed_object_name(host_ref)
    service_instance = utils_common.get_service_instance_from_managed_object(host_ref)
    traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(
        path="configManager.datastoreSystem", type=vim.HostSystem, skip=False
    )
    objs = utils_common.get_mors_with_properties(
        service_instance,
        vim.HostDatastoreSystem,
        property_list=["datastore"],
        container_ref=host_ref,
        traversal_spec=traversal_spec,
    )
    if not objs:
        raise salt.exceptions.VMwareObjectRetrievalError(
            "Host's '{}' datastore system was not retrieved" "".format(hostname)
        )
    log.trace("[%s] Retrieved datastore system", hostname)
    return objs[0]["object"]


def remove_datastore(service_instance, datastore_ref):
    """
    Creates a VMFS datastore from a disk_id

    service_instance
        The Service Instance Object containing the datastore

    datastore_ref
        The reference to the datastore to remove
    """
    ds_props = utils_common.get_properties_of_managed_object(
        datastore_ref, ["host", "info", "name"]
    )
    ds_name = ds_props["name"]
    log.debug("Removing datastore '%s'", ds_name)
    ds_hosts = ds_props.get("host")
    if not ds_hosts:
        raise salt.exceptions.VMwareApiError(
            "Datastore '{}' can't be removed. No " "attached hosts found".format(ds_name)
        )
    hostname = utils_common.get_managed_object_name(ds_hosts[0].key)
    host_ds_system = get_host_datastore_system(ds_hosts[0].key, hostname=hostname)
    try:
        host_ds_system.RemoveDatastore(datastore_ref)
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    log.trace("[%s] Removed datastore '%s'", hostname, ds_name)


def _get_scsi_address_to_lun_key_map(
    service_instance, host_ref, storage_system=None, hostname=None
):
    """
    Returns a map between the scsi addresses and the keys of all luns on an ESXi
    host.
        map[<scsi_address>] = <lun key>

    service_instance
        The Service Instance Object from which to obtain the hosts

    host_ref
        The vim.HostSystem object representing the host that contains the
        requested disks.

    storage_system
        The host's storage system. Default is None.

    hostname
        Name of the host. Default is None.
    """
    if not hostname:
        hostname = utils_common.get_managed_object_name(host_ref)
    if not storage_system:
        storage_system = utils_datastore.get_storage_system(service_instance, host_ref, hostname)
    try:
        device_info = storage_system.storageDeviceInfo
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    if not device_info:
        raise salt.exceptions.VMwareObjectRetrievalError(
            "Host's '{}' storage device " "info was not retrieved".format(hostname)
        )
    multipath_info = device_info.multipathInfo
    if not multipath_info:
        raise salt.exceptions.VMwareObjectRetrievalError(
            "Host's '{}' multipath info was not retrieved" "".format(hostname)
        )
    if multipath_info.lun is None:
        raise salt.exceptions.VMwareObjectRetrievalError(
            "No luns were retrieved from host '{}'".format(hostname)
        )
    lun_key_by_scsi_addr = {}
    for l in multipath_info.lun:
        # The vmware scsi_address may have multiple comma separated values
        # The first one is the actual scsi address
        lun_key_by_scsi_addr.update({p.name.split(",")[0]: l.lun for p in l.path})
    log.trace("Scsi address to lun id map on host '%s': %s", hostname, lun_key_by_scsi_addr)
    return lun_key_by_scsi_addr


def get_all_luns(host_ref, storage_system=None, hostname=None):
    """
    Returns a list of all vim.HostScsiDisk objects in a disk

    host_ref
        The vim.HostSystem object representing the host that contains the
        requested disks.

    storage_system
        The host's storage system. Default is None.

    hostname
        Name of the host. This argument is optional.
    """
    if not hostname:
        hostname = utils_common.get_managed_object_name(host_ref)
    if not storage_system:
        si = utils_common.get_service_instance_from_managed_object(host_ref, name=hostname)
        storage_system = utils_datastore.get_storage_system(si, host_ref, hostname)
        if not storage_system:
            raise salt.exceptions.VMwareObjectRetrievalError(
                "Host's '{}' storage system was not retrieved" "".format(hostname)
            )
    try:
        device_info = storage_system.storageDeviceInfo
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    if not device_info:
        raise salt.exceptions.VMwareObjectRetrievalError(
            "Host's '{}' storage device info was not retrieved" "".format(hostname)
        )

    scsi_luns = device_info.scsiLun
    if scsi_luns:
        log.trace(
            "Retrieved scsi luns in host '%s': %s",
            hostname,
            [l.canonicalName for l in scsi_luns],
        )
        return scsi_luns
    log.trace("Retrieved no scsi_luns in host '%s'", hostname)
    return []


def get_scsi_address_to_lun_map(host_ref, storage_system=None, hostname=None):
    """
    Returns a map of all vim.ScsiLun objects on a ESXi host keyed by their
    scsi address

    host_ref
        The vim.HostSystem object representing the host that contains the
        requested disks.

    storage_system
        The host's storage system. Default is None.

    hostname
        Name of the host. This argument is optional.
    """
    if not hostname:
        hostname = utils_common.get_managed_object_name(host_ref)
    si = utils_common.get_service_instance_from_managed_object(host_ref, name=hostname)
    if not storage_system:
        storage_system = utils_datastore.get_storage_system(si, host_ref, hostname)
    lun_ids_to_scsi_addr_map = _get_scsi_address_to_lun_key_map(
        si, host_ref, storage_system, hostname
    )
    luns_to_key_map = {d.key: d for d in get_all_luns(host_ref, storage_system, hostname)}
    return {
        scsi_addr: luns_to_key_map[lun_key]
        for scsi_addr, lun_key in lun_ids_to_scsi_addr_map.items()
    }


def get_disks(host_ref, disk_ids=None, scsi_addresses=None, get_all_disks=False):
    """
    Returns a list of vim.HostScsiDisk objects representing disks
    in a ESXi host, filtered by their cannonical names and scsi_addresses

    host_ref
        The vim.HostSystem object representing the host that contains the
        requested disks.

    disk_ids
        The list of canonical names of the disks to be retrieved. Default value
        is None

    scsi_addresses
        The list of scsi addresses of the disks to be retrieved. Default value
        is None

    get_all_disks
        Specifies whether to retrieve all disks in the host.
        Default value is False.
    """
    hostname = utils_common.get_managed_object_name(host_ref)
    if get_all_disks:
        log.trace("Retrieving all disks in host '%s'", hostname)
    else:
        log.trace(
            "Retrieving disks in host '%s': ids = (%s); scsi " "addresses = (%s)",
            hostname,
            disk_ids,
            scsi_addresses,
        )
        if not (disk_ids or scsi_addresses):
            return []
    si = utils_common.get_service_instance_from_managed_object(host_ref, name=hostname)
    storage_system = utils_datastore.get_storage_system(si, host_ref, hostname)
    disk_keys = []
    if scsi_addresses:
        # convert the scsi addresses to disk keys
        lun_key_by_scsi_addr = _get_scsi_address_to_lun_key_map(
            si, host_ref, storage_system, hostname
        )
        disk_keys = [
            key for scsi_addr, key in lun_key_by_scsi_addr.items() if scsi_addr in scsi_addresses
        ]
        log.trace("disk_keys based on scsi_addresses = %s", disk_keys)

    scsi_luns = get_all_luns(host_ref, storage_system)
    scsi_disks = [
        disk
        for disk in scsi_luns
        if isinstance(disk, vim.HostScsiDisk)
        and (
            get_all_disks
            or
            # Filter by canonical name
            (disk_ids and (disk.canonicalName in disk_ids))
            or
            # Filter by disk keys from scsi addresses
            (disk.key in disk_keys)
        )
    ]
    log.trace(
        "Retrieved disks in host '%s': %s",
        hostname,
        [d.canonicalName for d in scsi_disks],
    )
    return scsi_disks


def get_disk_partition_info(host_ref, disk_id, storage_system=None):
    """
    Returns all partitions on a disk

    host_ref
        The reference of the ESXi host containing the disk

    disk_id
        The canonical name of the disk whose partitions are to be removed

    storage_system
        The ESXi host's storage system. Default is None.
    """
    hostname = utils_common.get_managed_object_name(host_ref)
    service_instance = utils_common.get_service_instance_from_managed_object(host_ref)
    if not storage_system:
        storage_system = utils_datastore.get_storage_system(service_instance, host_ref, hostname)

    props = utils_common.get_properties_of_managed_object(
        storage_system, ["storageDeviceInfo.scsiLun"]
    )
    if not props.get("storageDeviceInfo.scsiLun"):
        raise salt.exceptions.VMwareObjectRetrievalError(
            "No devices were retrieved in host '{}'".format(hostname)
        )
    log.trace(
        "[%s] Retrieved %s devices: %s",
        hostname,
        len(props["storageDeviceInfo.scsiLun"]),
        ", ".join([l.canonicalName for l in props["storageDeviceInfo.scsiLun"]]),
    )
    disks = [
        l
        for l in props["storageDeviceInfo.scsiLun"]
        if isinstance(l, vim.HostScsiDisk) and l.canonicalName == disk_id
    ]
    if not disks:
        raise salt.exceptions.VMwareObjectRetrievalError(
            "Disk '{}' was not found in host '{}'" "".format(disk_id, hostname)
        )
    log.trace("[%s] device_path = %s", hostname, disks[0].devicePath)
    partition_info = _get_partition_info(storage_system, disks[0].devicePath)
    log.trace(
        "[%s] Retrieved %s partition(s) on disk '%s'",
        hostname,
        len(partition_info.spec.partition),
        disk_id,
    )
    return partition_info


def erase_disk_partitions(service_instance, host_ref, disk_id, hostname=None, storage_system=None):
    """
    Erases all partitions on a disk

    in a vcenter filtered by their names and/or datacenter, cluster membership

    service_instance
        The Service Instance Object from which to obtain all information

    host_ref
        The reference of the ESXi host containing the disk

    disk_id
        The canonical name of the disk whose partitions are to be removed

    hostname
        The ESXi hostname. Default is None.

    storage_system
        The ESXi host's storage system. Default is None.
    """

    if not hostname:
        hostname = utils_common.get_managed_object_name(host_ref)
    if not storage_system:
        storage_system = utils_datastore.get_storage_system(service_instance, host_ref, hostname)

    traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(
        path="configManager.storageSystem", type=vim.HostSystem, skip=False
    )
    results = utils_common.get_mors_with_properties(
        service_instance,
        vim.HostStorageSystem,
        ["storageDeviceInfo.scsiLun"],
        container_ref=host_ref,
        traversal_spec=traversal_spec,
    )
    if not results:
        raise salt.exceptions.VMwareObjectRetrievalError(
            "Host's '{}' devices were not retrieved".format(hostname)
        )
    log.trace(
        "[%s] Retrieved %s devices: %s",
        hostname,
        len(results[0].get("storageDeviceInfo.scsiLun", [])),
        ", ".join([l.canonicalName for l in results[0].get("storageDeviceInfo.scsiLun", [])]),
    )
    disks = [
        l
        for l in results[0].get("storageDeviceInfo.scsiLun", [])
        if isinstance(l, vim.HostScsiDisk) and l.canonicalName == disk_id
    ]
    if not disks:
        raise salt.exceptions.VMwareObjectRetrievalError(
            "Disk '{}' was not found in host '{}'" "".format(disk_id, hostname)
        )
    log.trace("[%s] device_path = %s", hostname, disks[0].devicePath)
    # Erase the partitions by setting an empty partition spec
    try:
        storage_system.UpdateDiskPartitions(disks[0].devicePath, vim.HostDiskPartitionSpec())
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    log.trace("[%s] Erased partitions on disk '%s'", hostname, disk_id)


def get_diskgroups(host_ref, cache_disk_ids=None, get_all_disk_groups=False):
    """
    Returns a list of vim.VsanHostDiskMapping objects representing disks
    in a ESXi host, filtered by their cannonical names.

    host_ref
        The vim.HostSystem object representing the host that contains the
        requested disks.

    cache_disk_ids
        The list of cannonical names of the cache disks to be retrieved. The
        canonical name of the cache disk is enough to identify the disk group
        because it is guaranteed to have one and only one cache disk.
        Default is None.

    get_all_disk_groups
        Specifies whether to retrieve all disks groups in the host.
        Default value is False.
    """
    hostname = utils_common.get_managed_object_name(host_ref)
    if get_all_disk_groups:
        log.trace("Retrieving all disk groups on host '%s'", hostname)
    else:
        log.trace(
            "Retrieving disk groups from host '%s', with cache disk " "ids : (%s)",
            hostname,
            cache_disk_ids,
        )
        if not cache_disk_ids:
            return []
    try:
        vsan_host_config = host_ref.config.vsanHostConfig
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)
    if not vsan_host_config:
        raise salt.exceptions.VMwareObjectRetrievalError(
            "No host config found on host '{}'".format(hostname)
        )
    vsan_storage_info = vsan_host_config.storageInfo
    if not vsan_storage_info:
        raise salt.exceptions.VMwareObjectRetrievalError(
            "No vsan storage info found on host '{}'".format(hostname)
        )
    vsan_disk_mappings = vsan_storage_info.diskMapping
    if not vsan_disk_mappings:
        return []
    disk_groups = [
        dm
        for dm in vsan_disk_mappings
        if (get_all_disk_groups or (dm.ssd.canonicalName in cache_disk_ids))
    ]
    log.trace(
        "Retrieved disk groups on host '%s', with cache disk ids : %s",
        hostname,
        [d.ssd.canonicalName for d in disk_groups],
    )
    return disk_groups


def _check_disks_in_diskgroup(disk_group, cache_disk_id, capacity_disk_ids):
    """
    Checks that the disks in a disk group are as expected and raises
    CheckError exceptions if the check fails
    """
    if not disk_group.ssd.canonicalName == cache_disk_id:
        raise salt.exceptions.ArgumentValueError(
            "Incorrect diskgroup cache disk; got id: '{}'; expected id: "
            "'{}'".format(disk_group.ssd.canonicalName, cache_disk_id)
        )
    non_ssd_disks = [d.canonicalName for d in disk_group.nonSsd]
    if sorted(non_ssd_disks) != sorted(capacity_disk_ids):
        raise salt.exceptions.ArgumentValueError(
            "Incorrect capacity disks; got ids: '{}'; expected ids: '{}'"
            "".format(sorted(non_ssd_disks), sorted(capacity_disk_ids))
        )
    log.trace("Checked disks in diskgroup with cache disk id '%s'", cache_disk_id)
    return True


# TODO Support host caches on multiple datastores
def get_host_cache(host_ref, host_cache_manager=None):
    """
    Returns a vim.HostScsiDisk if the host cache is configured on the specified
    host, other wise returns None

    host_ref
        The vim.HostSystem object representing the host that contains the
        requested disks.

    host_cache_manager
        The vim.HostCacheConfigurationManager object representing the cache
        configuration manager on the specified host. Default is None. If None,
        it will be retrieved in the method
    """
    hostname = utils_common.get_managed_object_name(host_ref)
    service_instance = utils_common.get_service_instance_from_managed_object(host_ref)
    log.trace("Retrieving the host cache on host '%s'", hostname)
    if not host_cache_manager:
        traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(
            path="configManager.cacheConfigurationManager",
            type=vim.HostSystem,
            skip=False,
        )
        results = utils_common.get_mors_with_properties(
            service_instance,
            vim.HostCacheConfigurationManager,
            ["cacheConfigurationInfo"],
            container_ref=host_ref,
            traversal_spec=traversal_spec,
        )
        if not results or not results[0].get("cacheConfigurationInfo"):
            log.trace("Host '%s' has no host cache", hostname)
            return None
        return results[0]["cacheConfigurationInfo"][0]
    else:
        results = utils_common.get_properties_of_managed_object(
            host_cache_manager, ["cacheConfigurationInfo"]
        )
        if not results:
            log.trace("Host '%s' has no host cache", hostname)
            return None
        return results["cacheConfigurationInfo"][0]


def list_resourcepools(service_instance):
    """
    Returns a list of resource pools associated with a given service instance.

    service_instance
        The Service Instance Object from which to obtain resource pools.
    """
    return utils_common.list_objects(service_instance, vim.ResourcePool)


def list_networks(service_instance):
    """
    Returns a list of networks associated with a given service instance.

    service_instance
        The Service Instance Object from which to obtain networks.
    """
    return utils_common.list_objects(service_instance, vim.Network)


def list_folders(service_instance):
    """
    Returns a list of folders associated with a given service instance.

    service_instance
        The Service Instance Object from which to obtain folders.
    """
    return utils_common.list_objects(service_instance, vim.Folder)


def list_dvs(service_instance, properties=None):
    """
    Returns a list of distributed virtual switches associated with a given service instance.
    service_instance
        The Service Instance Object from which to obtain distributed virtual switches.
    properties
        An optional list of object properties used to return reference results.
    """
    return utils_common.list_objects(service_instance, vim.DistributedVirtualSwitch, properties)


def list_vapps(service_instance):
    """
    Returns a list of vApps associated with a given service instance.

    service_instance
        The Service Instance Object from which to obtain vApps.
    """
    return utils_common.list_objects(service_instance, vim.VirtualApp)


def list_portgroups(service_instance):
    """
    Returns a list of distributed virtual portgroups associated with a given service instance.

    service_instance
        The Service Instance Object from which to obtain distributed virtual switches.
    """
    return utils_common.list_objects(service_instance, vim.dvs.DistributedVirtualPortgroup)


def convert_to_kb(unit, size):
    """
    Converts the given size to KB based on the unit, returns a long integer.

    unit
        Unit of the size eg. GB; Note: to VMware a GB is the same as GiB = 1024MiB
    size
        Number which represents the size
    """
    if unit.lower() == "gb":
        # vCenter needs long value
        target_size = int(size * 1024 * 1024)
    elif unit.lower() == "mb":
        target_size = int(size * 1024)
    elif unit.lower() == "kb":
        target_size = int(size)
    else:
        raise salt.exceptions.ArgumentValueError("The unit is not specified")
    return {"size": target_size, "unit": "KB"}


def get_proxy_target(service_instance):
    """
    Returns the target object of a proxy.

    If the object doesn't exist a VMwareObjectRetrievalError is raised

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
    """
    proxy_type = get_proxy_type()
    if not salt.utils.vmware.is_connection_to_a_vcenter(service_instance):
        raise CommandExecutionError(
            "'_get_proxy_target' not supported " "when connected via the ESXi host"
        )
    reference = None
    if proxy_type == "esxcluster":
        (
            host,
            username,
            password,
            protocol,
            port,
            mechanism,
            principal,
            domain,
            datacenter,
            cluster,
        ) = _get_esxcluster_proxy_details()

        dc_ref = utils_datacenter.utils_datacenter.get_datacenter(service_instance, datacenter)
        reference = utils_cluster.utils_cluster.get_cluster(dc_ref, cluster)
    elif proxy_type == "esxdatacenter":
        # esxdatacenter proxy
        (
            host,
            username,
            password,
            protocol,
            port,
            mechanism,
            principal,
            domain,
            datacenter,
        ) = _get_esxdatacenter_proxy_details()

        reference = utils_datacenter.utils_datacenter.get_datacenter(service_instance, datacenter)
    elif proxy_type == "vcenter":
        # vcenter proxy - the target is the root folder
        reference = utils_common.utils_common.get_root_folder(service_instance)
    elif proxy_type == "esxi":
        # esxi proxy
        details = __proxy__["esxi.get_details"]()
        if "vcenter" not in details:
            raise InvalidEntityError(
                "Proxies connected directly to ESXi " "hosts are not supported"
            )
        references = salt.utils.vmware.utils_esxi.get_hosts(
            service_instance, host_names=details["esxi_host"]
        )
        if not references:
            raise VMwareObjectRetrievalError(
                "ESXi host '{}' was not found".format(details["esxi_host"])
            )
        reference = references[0]
    log.trace("reference = {}".format(reference))
    return reference


def _get_esxdatacenter_proxy_details():
    """
    Returns the running esxdatacenter's proxy details
    """
    det = __salt__["esxdatacenter.get_details"]()
    return (
        det.get("vcenter"),
        det.get("username"),
        det.get("password"),
        det.get("protocol"),
        det.get("port"),
        det.get("mechanism"),
        det.get("principal"),
        det.get("domain"),
        det.get("datacenter"),
    )


def _get_esxcluster_proxy_details():
    """
    Returns the running esxcluster's proxy details
    """
    det = __salt__["esxcluster.get_details"]()
    return (
        det.get("vcenter"),
        det.get("username"),
        det.get("password"),
        det.get("protocol"),
        det.get("port"),
        det.get("mechanism"),
        det.get("principal"),
        det.get("domain"),
        det.get("datacenter"),
        det.get("cluster"),
    )


def _get_esxi_proxy_details():
    """
    Returns the running esxi's proxy details
    """
    det = __proxy__["esxi.get_details"]()
    host = det.get("host")
    if det.get("vcenter"):
        host = det["vcenter"]
    esxi_hosts = None
    if det.get("esxi_host"):
        esxi_hosts = [det["esxi_host"]]
    return (
        host,
        det.get("username"),
        det.get("password"),
        det.get("protocol"),
        det.get("port"),
        det.get("mechanism"),
        det.get("principal"),
        det.get("domain"),
        esxi_hosts,
    )


def _get_policy_dict(policy):
    """Returns a dictionary representation of a policy"""
    profile_dict = {
        "name": policy.name,
        "description": policy.description,
        "resource_type": policy.resourceType.resourceType,
    }
    subprofile_dicts = []
    if isinstance(policy, pbm.profile.CapabilityBasedProfile) and isinstance(
        policy.constraints, pbm.profile.SubProfileCapabilityConstraints
    ):

        for subprofile in policy.constraints.subProfiles:
            subprofile_dict = {
                "name": subprofile.name,
                "force_provision": subprofile.forceProvision,
            }
            cap_dicts = []
            for cap in subprofile.capability:
                cap_dict = {"namespace": cap.id.namespace, "id": cap.id.id}
                # We assume there is one constraint with one value set
                val = cap.constraint[0].propertyInstance[0].value
                if isinstance(val, pbm.capability.types.Range):
                    val_dict = {"type": "range", "min": val.min, "max": val.max}
                elif isinstance(val, pbm.capability.types.DiscreteSet):
                    val_dict = {"type": "set", "values": val.values}
                else:
                    val_dict = {"type": "scalar", "value": val}
                cap_dict["setting"] = val_dict
                cap_dicts.append(cap_dict)
            subprofile_dict["capabilities"] = cap_dicts
            subprofile_dicts.append(subprofile_dict)
    profile_dict["subprofiles"] = subprofile_dicts
    return profile_dict
