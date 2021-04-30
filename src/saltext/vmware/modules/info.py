# SPDX-License-Identifier: Apache-2.0
import logging
import sys

import salt.config
import salt.modules.pillar
import salt.utils.dictupdate as dictupdate
import salt.utils.platform
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


__virtualname__ = "vmware_info"


def __virtual__():
    return __virtualname__


def _get_host_ssds(host_reference):
    """
    Helper function that returns a list of ssd objects for a given host.
    """
    return _get_host_disks(host_reference).get("SSDs")


def _get_host_non_ssds(host_reference):
    """
    Helper function that returns a list of Non-SSD objects for a given host.
    """
    return _get_host_disks(host_reference).get("Non-SSDs")


def _get_host_disks(host_reference):
    """
    Helper function that returns a dictionary containing a list of SSD and Non-SSD disks.
    """
    storage_system = host_reference.configManager.storageSystem
    disks = storage_system.storageDeviceInfo.scsiLun
    ssds = []
    non_ssds = []

    for disk in disks:
        try:
            has_ssd_attr = disk.ssd
        except AttributeError:
            has_ssd_attr = False
        if has_ssd_attr:
            ssds.append(disk)
        else:
            non_ssds.append(disk)

    return {"SSDs": ssds, "Non-SSDs": non_ssds}


def get_proxy_type():
    """
    Returns the proxy type retrieved either from the pillar of from the proxy
    minion's config.  Returns ``<undefined>`` otherwise.

    CLI Example:

    .. code-block:: bash

        salt '*' vsphere.get_proxy_type
    """
    if __pillar__.get("proxy", {}).get("proxytype"):
        return __pillar__["proxy"]["proxytype"]

    if __opts__.get("proxy", {}).get("proxytype"):
        return __opts__["proxy"]["proxytype"]
    return "<undefined>"


def get_proxy_connection_details():
    """
    Returns the connection details of the following proxies: esxi
    """
    proxytype = get_proxy_type()
    if proxytype == "esxi":
        details = __salt__["esxi.get_details"]()
    elif proxytype == "esxcluster":
        details = __salt__["esxcluster.get_details"]()
    elif proxytype == "esxdatacenter":
        details = __salt__["esxdatacenter.get_details"]()
    elif proxytype == "vcenter":
        details = __salt__["vcenter.get_details"]()
    elif proxytype == "esxvm":
        details = __salt__["esxvm.get_details"]()
    else:
        raise CommandExecutionError("'{}' proxy is not supported" "".format(proxytype))

    proxy_details = {
        "username": details.get("username"),
        "password": details.get("password"),
        "protocol": details.get("protocol"),
        "port": details.get("port"),
        "mechanism": details.get("mechanism", "userpass"),
        "principal": details.get("principal"),
        "domain": details.get("domain"),
        "verify_ssl": details.get("verify_ssl", True),
    }
    if "vcenter" in details:
        proxy_details["host"] = details.get("vcenter")

    if "host" in details:
        proxy_details["host"] = details.get("host")

    return proxy_details


def get_connection_details(
    host=None,
    vcenter=None,
    username=None,
    password=None,
    protocol=None,
    port=None,
    mechanism=None,
    principal=None,
    domain=None,
    verify_ssl=None,
):
    """
    Returns the connection details of the following proxies: esxi
    """
    if not host:
        host = (
            __salt__["config.get"]("vmware.host")
            or __salt__["config.get"]("vmware:host")
            or __salt__["pillar.get"]("vmware.host")
            or None
        )

    if not vcenter:
        vcenter = (
            __salt__["config.get"]("vmware.vcenter")
            or __salt__["config.get"]("vmware:vcenter")
            or __salt__["pillar.get"]("vmware.vcenter")
            or None
        )

    if not username:
        username = (
            __salt__["config.get"]("vmware.username")
            or __salt__["config.get"]("vmware:username")
            or __salt__["pillar.get"]("vmware.username")
            or None
        )

    if not password:
        password = (
            __salt__["config.get"]("vmware.password")
            or __salt__["config.get"]("vmware:password")
            or __salt__["pillar.get"]("vmware.password")
            or None
        )

    if not protocol:
        protocol = (
            __salt__["config.get"]("vmware.protocol")
            or __salt__["config.get"]("vmware:protocol")
            or __salt__["pillar.get"]("vmware.protocol")
            or None
        )

    if not port:
        port = (
            __salt__["config.get"]("vmware.port")
            or __salt__["config.get"]("vmware:port")
            or __salt__["pillar.get"]("vmware.port")
            or None
        )

    if not mechanism:
        mechanism = (
            __salt__["config.get"]("vmware.mechanism")
            or __salt__["config.get"]("vmware:mechanism")
            or __salt__["pillar.get"]("vmware.mechanism")
            or "userpass"
        )

    if not principal:
        principal = (
            __salt__["config.get"]("vmware.principal")
            or __salt__["config.get"]("vmware:principal")
            or __salt__["pillar.get"]("vmware.principal")
            or None
        )

    if not domain:
        domain = (
            __salt__["config.get"]("vmware.domain")
            or __salt__["config.get"]("vmware:domain")
            or __salt__["pillar.get"]("vmware.domain")
            or None
        )

    if verify_ssl == None:
        verify_ssl = (
            __salt__["config.get"]("vmware.verify_ssl", True)
            and __salt__["config.get"]("vmware:verify_ssl", True)
            and __salt__["pillar.get"]("vmware.verify_ssl", True)
        )

    proxy_details = {
        "username": username,
        "password": password,
        "protocol": protocol,
        "port": port,
        "mechanism": mechanism,
        "principal": principal,
        "domain": domain,
        "verify_ssl": verify_ssl,
    }
    if vcenter:
        proxy_details["vcenter"] = vcenter

    if host:
        proxy_details["host"] = host

    return proxy_details


def system_info(
    host=None,
    vcenter=None,
    username=None,
    password=None,
    protocol=None,
    port=None,
    verify_ssl=None,
):
    """
    Return system information about a VMware environment.

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

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        salt '*' vsphere.system_info 1.2.3.4 root bad-password
    """
    # If we have at least host, username and password, just get the details
    # the request is coming from grains.
    if salt.utils.platform.is_proxy():
        if not username and not password:
            details = get_proxy_connection_details()
        else:
            details = {}
            details["host"] = host
            # details["vcenter"] = vcenter
            details["username"] = username
            details["password"] = password
            details["protocol"] = protocol
            details["port"] = port
            details["verify_ssl"] = verify_ssl
    else:
        details = get_connection_details(
            host=host,
            vcenter=vcenter,
            username=username,
            password=password,
            protocol=protocol,
            port=port,
            verify_ssl=verify_ssl,
        )
    service_instance = saltext.vmware.utils.vmware.get_service_instance(**details)

    ret = saltext.vmware.utils.vmware.get_inventory(service_instance).about.__dict__
    if "apiType" in ret:
        if ret["apiType"] == "HostAgent":
            ret = dictupdate.update(
                ret, saltext.vmware.utils.vmware.get_hardware_grains(service_instance)
            )
    return ret


def get_host_datetime(
    host, username, password, protocol=None, port=None, host_names=None, verify_ssl=True
):
    """
    Get the date/time information for a given host or list of host_names.

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
        are provided for a vCenter Server, the host_names argument is required to tell
        vCenter the hosts for which to get date/time information.

        If host_names is not provided, the date/time information will be retrieved for the
        ``host`` location instead. This is useful for when service instance connection
        information is used for a single ESXi host.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        # Used for single ESXi host connection information
        salt '*' vsphere.get_host_datetime my.esxi.host root bad-password

        # Used for connecting to a vCenter Server
        salt '*' vsphere.get_host_datetime my.vcenter.location root bad-password \
        host_names='[esxi-1.host.com, esxi-2.host.com]'
    """
    service_instance = salt.utils.vmware.get_service_instance(
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
        date_time_manager = _get_date_time_mgr(host_ref)
        date_time = date_time_manager.QueryDateTime()
        ret.update({host_name: date_time})

    return ret


def list_hosts(host, username, password, protocol=None, port=None, verify_ssl=True):
    """
    Returns a list of hosts for the specified VMware environment.

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

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        salt '*' vsphere.list_hosts 1.2.3.4 root bad-password
    """
    service_instance = salt.utils.vmware.get_service_instance(
        host=host,
        username=username,
        password=password,
        protocol=protocol,
        port=port,
        verify_ssl=verify_ssl,
    )
    return salt.utils.vmware.list_hosts(service_instance)


def list_hosts_via_proxy(hostnames=None, datacenter=None, cluster=None, service_instance=None):
    """
    Returns a list of hosts for the specified VMware environment. The list
    of hosts can be filtered by datacenter name and/or cluster name

    hostnames
        Hostnames to filter on.

    datacenter_name
        Name of datacenter. Only hosts in this datacenter will be retrieved.
        Default is None.

    cluster_name
        Name of cluster. Only hosts in this cluster will be retrieved. If a
        datacenter is not specified the first cluster with this name will be
        considerred. Default is None.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
        Default is None.

    CLI Example:

    .. code-block:: bash

        salt '*' vsphere.list_hosts_via_proxy

        salt '*' vsphere.list_hosts_via_proxy hostnames=[esxi1.example.com]

        salt '*' vsphere.list_hosts_via_proxy datacenter=dc1 cluster=cluster1
    """
    if cluster:
        if not datacenter:
            raise salt.exceptions.ArgumentValueError(
                "Datacenter is required when cluster is specified"
            )
    get_all_hosts = False
    if not hostnames:
        get_all_hosts = True
    hosts = salt.utils.vmware.get_hosts(
        service_instance,
        datacenter_name=datacenter,
        host_names=hostnames,
        cluster_name=cluster,
        get_all_hosts=get_all_hosts,
    )
    return [salt.utils.vmware.get_managed_object_name(h) for h in hosts]


def list_resourcepools(host, username, password, protocol=None, port=None, verify_ssl=True):
    """
    Returns a list of resource pools for the specified host.

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

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        salt '*' vsphere.list_resourcepools 1.2.3.4 root bad-password
    """
    service_instance = salt.utils.vmware.get_service_instance(
        host=host,
        username=username,
        password=password,
        protocol=protocol,
        port=port,
        verify_ssl=verify_ssl,
    )
    return salt.utils.vmware.list_resourcepools(service_instance)


def list_networks(host, username, password, protocol=None, port=None, verify_ssl=True):
    """
    Returns a list of networks for the specified host.

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

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        salt '*' vsphere.list_networks 1.2.3.4 root bad-password
    """
    service_instance = salt.utils.vmware.get_service_instance(
        host=host,
        username=username,
        password=password,
        protocol=protocol,
        port=port,
        verify_ssl=verify_ssl,
    )
    return salt.utils.vmware.list_networks(service_instance)


def list_folders(host, username, password, protocol=None, port=None, verify_ssl=True):
    """
    Returns a list of folders for the specified host.

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

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        salt '*' vsphere.list_folders 1.2.3.4 root bad-password
    """
    service_instance = salt.utils.vmware.get_service_instance(
        host=host,
        username=username,
        password=password,
        protocol=protocol,
        port=port,
        verify_ssl=verify_ssl,
    )
    return salt.utils.vmware.list_folders(service_instance)


def list_vapps(host, username, password, protocol=None, port=None, verify_ssl=True):
    """
    Returns a list of vApps for the specified host.

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

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        # List vapps from all minions
        salt '*' vsphere.list_vapps 1.2.3.4 root bad-password
    """
    service_instance = salt.utils.vmware.get_service_instance(
        host=host,
        username=username,
        password=password,
        protocol=protocol,
        port=port,
        verify_ssl=verify_ssl,
    )
    return salt.utils.vmware.list_vapps(service_instance)


def list_ssds(host, username, password, protocol=None, port=None, host_names=None, verify_ssl=True):
    """
    Returns a list of SSDs for the given host or list of host_names.

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
        tell vCenter the hosts for which to retrieve SSDs.

        If host_names is not provided, SSDs will be retrieved for the
        ``host`` location instead. This is useful for when service instance
        connection information is used for a single ESXi host.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        # Used for single ESXi host connection information
        salt '*' vsphere.list_ssds my.esxi.host root bad-password

        # Used for connecting to a vCenter Server
        salt '*' vsphere.list_ssds my.vcenter.location root bad-password \
        host_names='[esxi-1.host.com, esxi-2.host.com]'
    """
    service_instance = salt.utils.vmware.get_service_instance(
        host=host,
        username=username,
        password=password,
        protocol=protocol,
        port=port,
        verify_ssl=verify_ssl,
    )
    host_names = _check_hosts(service_instance, host, host_names)
    ret = {}
    names = []
    for host_name in host_names:
        host_ref = _get_host_ref(service_instance, host, host_name=host_name)
        disks = _get_host_ssds(host_ref)
        for disk in disks:
            names.append(disk.canonicalName)
        ret.update({host_name: names})

    return ret


def list_non_ssds(
    host, username, password, protocol=None, port=None, host_names=None, verify_ssl=True
):
    """
    Returns a list of Non-SSD disks for the given host or list of host_names.

    .. note::

        In the pyVmomi StorageSystem, ScsiDisks may, or may not have an ``ssd`` attribute.
        This attribute indicates if the ScsiDisk is SSD backed. As this option is optional,
        if a relevant disk in the StorageSystem does not have ``ssd = true``, it will end
        up in the ``non_ssds`` list here.

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
        tell vCenter the hosts for which to retrieve Non-SSD disks.

        If host_names is not provided, Non-SSD disks will be retrieved for the
        ``host`` location instead. This is useful for when service instance
        connection information is used for a single ESXi host.

    verify_ssl
        Verify the SSL certificate. Default: True

    CLI Example:

    .. code-block:: bash

        # Used for single ESXi host connection information
        salt '*' vsphere.list_non_ssds my.esxi.host root bad-password

        # Used for connecting to a vCenter Server
        salt '*' vsphere.list_non_ssds my.vcenter.location root bad-password \
        host_names='[esxi-1.host.com, esxi-2.host.com]'
    """
    service_instance = salt.utils.vmware.get_service_instance(
        host=host,
        username=username,
        password=password,
        protocol=protocol,
        port=port,
        verify_ssl=verify_ssl,
    )
    host_names = _check_hosts(service_instance, host, host_names)
    ret = {}
    names = []
    for host_name in host_names:
        host_ref = _get_host_ref(service_instance, host, host_name=host_name)
        disks = _get_host_non_ssds(host_ref)
        for disk in disks:
            names.append(disk.canonicalName)
        ret.update({host_name: names})

    return ret


def get_proxy_target(service_instance):
    """
    Returns the target object of a proxy.

    If the object doesn't exist a VMwareObjectRetrievalError is raised

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
    """
    proxy_type = get_proxy_type()
    if not saltext.vmware.utils.vmware.is_connection_to_a_vcenter(service_instance):
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

        dc_ref = saltext.vmware.utils.vmware.get_datacenter(service_instance, datacenter)
        reference = salt.utils.vmware.get_cluster(dc_ref, cluster)
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

        reference = saltext.vmware.utils.vmware.get_datacenter(service_instance, datacenter)
    elif proxy_type == "vcenter":
        # vcenter proxy - the target is the root folder
        reference = saltext.vmware.utils.vmware.get_root_folder(service_instance)
    elif proxy_type == "esxi":
        # esxi proxy
        details = __proxy__["esxi.get_details"]()
        if "vcenter" not in details:
            raise InvalidEntityError(
                "Proxies connected directly to ESXi " "hosts are not supported"
            )
        references = saltext.vmware.utils.vmware.get_hosts(
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


def get_policy_dict(policy):
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
