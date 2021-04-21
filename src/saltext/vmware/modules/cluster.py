# pylint: disable=C0302
"""
Manage VMware vCenter servers and ESXi hosts.

.. versionadded:: 2015.8.4

:codeauthor: Alexandru Bleotu <alexandru.bleotu@morganstaley.com>

Dependencies
============

- pyVmomi Python Module
- ESXCLI

pyVmomi
-------

PyVmomi can be installed via pip:

.. code-block:: bash

    pip install pyVmomi

.. note::

    Version 6.0 of pyVmomi has some problems with SSL error handling on certain
    versions of Python. If using version 6.0 of pyVmomi, Python 2.7.9,
    or newer must be present. This is due to an upstream dependency
    in pyVmomi 6.0 that is not supported in Python versions 2.7 to 2.7.8. If the
    version of Python is not in the supported range, you will need to install an
    earlier version of pyVmomi. See `Issue #29537`_ for more information.

.. _Issue #29537: https://github.com/saltstack/salt/issues/29537

Based on the note above, to install an earlier version of pyVmomi than the
version currently listed in PyPi, run the following:

.. code-block:: bash

    pip install pyVmomi==5.5.0.2014.1.1

The 5.5.0.2014.1.1 is a known stable version that this original vSphere Execution
Module was developed against.

vSphere Automation SDK
----------------------

vSphere Automation SDK can be installed via pip:

.. code-block:: bash

    pip install --upgrade pip setuptools
    pip install --upgrade git+https://github.com/vmware/vsphere-automation-sdk-python.git

.. note::

    The SDK also requires OpenSSL 1.0.1+ if you want to connect to vSphere 6.5+ in order to support
    TLS1.1 & 1.2.

    In order to use the tagging functions in this module, vSphere Automation SDK is necessary to
    install.

The module is currently in version 1.0.3
(as of 8/26/2019)

ESXCLI
------

Currently, about a third of the functions used in the vSphere Execution Module require
the ESXCLI package be installed on the machine running the Proxy Minion process.

The ESXCLI package is also referred to as the VMware vSphere CLI, or vCLI. VMware
provides vCLI package installation instructions for `vSphere 5.5`_ and
`vSphere 6.0`_.

.. _vSphere 5.5: http://pubs.vmware.com/vsphere-55/index.jsp#com.vmware.vcli.getstart.doc/cli_install.4.2.html
.. _vSphere 6.0: http://pubs.vmware.com/vsphere-60/index.jsp#com.vmware.vcli.getstart.doc/cli_install.4.2.html

Once all of the required dependencies are in place and the vCLI package is
installed, you can check to see if you can connect to your ESXi host or vCenter
server by running the following command:

.. code-block:: bash

    esxcli -s <host-location> -u <username> -p <password> system syslog config get

If the connection was successful, ESXCLI was successfully installed on your system.
You should see output related to the ESXi host's syslog configuration.

.. note::

    Be aware that some functionality in this execution module may depend on the
    type of license attached to a vCenter Server or ESXi host(s).

    For example, certain services are only available to manipulate service state
    or policies with a VMware vSphere Enterprise or Enterprise Plus license, while
    others are available with a Standard license. The ``ntpd`` service is restricted
    to an Enterprise Plus license, while ``ssh`` is available via the Standard
    license.

    Please see the `vSphere Comparison`_ page for more information.

.. _vSphere Comparison: https://www.vmware.com/products/vsphere/compare


About
=====

This execution module was designed to be able to handle connections both to a
vCenter Server, as well as to an ESXi host. It utilizes the pyVmomi Python
library and the ESXCLI package to run remote execution functions against either
the defined vCenter server or the ESXi host.

Whether or not the function runs against a vCenter Server or an ESXi host depends
entirely upon the arguments passed into the function. Each function requires a
``host`` location, ``username``, and ``password``. If the credentials provided
apply to a vCenter Server, then the function will be run against the vCenter
Server. For example, when listing hosts using vCenter credentials, you'll get a
list of hosts associated with that vCenter Server:

.. code-block:: bash

    # salt my-minion vsphere.list_hosts <vcenter-ip> <vcenter-user> <vcenter-password>
    my-minion:
    - esxi-1.example.com
    - esxi-2.example.com

However, some functions should be used against ESXi hosts, not vCenter Servers.
Functionality such as getting a host's coredump network configuration should be
performed against a host and not a vCenter server. If the authentication
information you're using is against a vCenter server and not an ESXi host, you
can provide the host name that is associated with the vCenter server in the
command, as a list, using the ``host_names`` or ``esxi_host`` kwarg. For
example:

.. code-block:: bash

    # salt my-minion vsphere.get_coredump_network_config <vcenter-ip> <vcenter-user> \
        <vcenter-password> esxi_hosts='[esxi-1.example.com, esxi-2.example.com]'
    my-minion:
    ----------
        esxi-1.example.com:
            ----------
            Coredump Config:
                ----------
                enabled:
                    False
        esxi-2.example.com:
            ----------
            Coredump Config:
                ----------
                enabled:
                    True
                host_vnic:
                    vmk0
                ip:
                    coredump-location.example.com
                port:
                    6500

You can also use these functions against an ESXi host directly by establishing a
connection to an ESXi host using the host's location, username, and password. If ESXi
connection credentials are used instead of vCenter credentials, the ``host_names`` and
``esxi_hosts`` arguments are not needed.

.. code-block:: bash

    # salt my-minion vsphere.get_coredump_network_config esxi-1.example.com root <host-password>
    local:
    ----------
        10.4.28.150:
            ----------
            Coredump Config:
                ----------
                enabled:
                    True
                host_vnic:
                    vmk0
                ip:
                    coredump-location.example.com
                port:
                    6500
"""
import logging
import sys

import salt.utils.platform
import saltext.vmware.utils.vmware
from salt.exceptions import InvalidConfigError
from salt.utils.decorators import depends
from salt.utils.dictdiffer import recursive_diff
from salt.utils.listdiffer import list_diff
from saltext.vmware.config.schemas.esxvm import ESXVirtualMachineDeleteSchema
from saltext.vmware.config.schemas.esxvm import ESXVirtualMachineUnregisterSchema

log = logging.getLogger(__name__)

try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

try:
    # pylint: disable=no-name-in-module
    from pyVmomi import (
        vim,
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

__virtualname__ = "vmware_cluster"


def __virtual__():
    return __virtualname__


def _get_cluster_dict(cluster_name, cluster_ref):
    """
    Returns a cluster dict representation from
    a vim.ClusterComputeResource object.

    cluster_name
        Name of the cluster

    cluster_ref
        Reference to the cluster
    """

    log.trace("Building a dictionary representation of cluster " "'{}'".format(cluster_name))
    props = salt.utils.vmware.get_properties_of_managed_object(
        cluster_ref, properties=["configurationEx"]
    )
    res = {
        "ha": {"enabled": props["configurationEx"].dasConfig.enabled},
        "drs": {"enabled": props["configurationEx"].drsConfig.enabled},
    }
    # Convert HA properties of interest
    ha_conf = props["configurationEx"].dasConfig
    log.trace("ha_conf = {}".format(ha_conf))
    res["ha"]["admission_control_enabled"] = ha_conf.admissionControlEnabled
    if ha_conf.admissionControlPolicy and isinstance(
        ha_conf.admissionControlPolicy,
        vim.ClusterFailoverResourcesAdmissionControlPolicy,
    ):
        pol = ha_conf.admissionControlPolicy
        res["ha"]["admission_control_policy"] = {
            "cpu_failover_percent": pol.cpuFailoverResourcesPercent,
            "memory_failover_percent": pol.memoryFailoverResourcesPercent,
        }
    if ha_conf.defaultVmSettings:
        def_vm_set = ha_conf.defaultVmSettings
        res["ha"]["default_vm_settings"] = {
            "isolation_response": def_vm_set.isolationResponse,
            "restart_priority": def_vm_set.restartPriority,
        }
    res["ha"]["hb_ds_candidate_policy"] = ha_conf.hBDatastoreCandidatePolicy
    if ha_conf.hostMonitoring:
        res["ha"]["host_monitoring"] = ha_conf.hostMonitoring
    if ha_conf.option:
        res["ha"]["options"] = [{"key": o.key, "value": o.value} for o in ha_conf.option]
    res["ha"]["vm_monitoring"] = ha_conf.vmMonitoring
    # Convert DRS properties
    drs_conf = props["configurationEx"].drsConfig
    log.trace("drs_conf = {}".format(drs_conf))
    res["drs"]["vmotion_rate"] = 6 - drs_conf.vmotionRate
    res["drs"]["default_vm_behavior"] = drs_conf.defaultVmBehavior
    # vm_swap_placement
    res["vm_swap_placement"] = props["configurationEx"].vmSwapPlacement
    # Convert VSAN properties
    si = salt.utils.vmware.get_service_instance_from_managed_object(cluster_ref)

    if salt.utils.vsan.vsan_supported(si):
        # XXX The correct way of retrieving the VSAN data (on the if branch)
        #  is not supported before 60u2 vcenter
        vcenter_info = salt.utils.vmware.get_service_info(si)
        if int(vcenter_info.build) >= 3634794:  # 60u2
            # VSAN API is fully supported by the VC starting with 60u2
            vsan_conf = salt.utils.vsan.get_cluster_vsan_info(cluster_ref)
            log.trace("vsan_conf = {}".format(vsan_conf))
            res["vsan"] = {
                "enabled": vsan_conf.enabled,
                "auto_claim_storage": vsan_conf.defaultConfig.autoClaimStorage,
            }
            if vsan_conf.dataEfficiencyConfig:
                data_eff = vsan_conf.dataEfficiencyConfig
                res["vsan"].update(
                    {
                        # We force compression_enabled to be True/False
                        "compression_enabled": data_eff.compressionEnabled or False,
                        "dedup_enabled": data_eff.dedupEnabled,
                    }
                )
        else:  # before 60u2 (no advanced vsan info)
            if props["configurationEx"].vsanConfigInfo:
                default_config = props["configurationEx"].vsanConfigInfo.defaultConfig
                res["vsan"] = {
                    "enabled": props["configurationEx"].vsanConfigInfo.enabled,
                    "auto_claim_storage": default_config.autoClaimStorage,
                }
    return res


def _apply_cluster_dict(cluster_spec, cluster_dict, vsan_spec=None, vsan_61=True):
    """
    Applies the values of cluster_dict dictionary to a cluster spec
    (vim.ClusterConfigSpecEx).

    All vsan values (cluster_dict['vsan']) will be applied to
    vsan_spec (vim.vsan.cluster.ConfigInfoEx). Can be not omitted
    if not required.

    VSAN 6.1 config needs to be applied differently than the post VSAN 6.1 way.
    The type of configuration desired is dictated by the flag vsan_61.
    """
    log.trace("Applying cluster dict {}".format(cluster_dict))
    if cluster_dict.get("ha"):
        ha_dict = cluster_dict["ha"]
        if not cluster_spec.dasConfig:
            cluster_spec.dasConfig = vim.ClusterDasConfigInfo()
        das_config = cluster_spec.dasConfig
        if "enabled" in ha_dict:
            das_config.enabled = ha_dict["enabled"]
            if ha_dict["enabled"]:
                # Default values when ha is enabled
                das_config.failoverLevel = 1
        if "admission_control_enabled" in ha_dict:
            das_config.admissionControlEnabled = ha_dict["admission_control_enabled"]
        if "admission_control_policy" in ha_dict:
            adm_pol_dict = ha_dict["admission_control_policy"]
            if not das_config.admissionControlPolicy or not isinstance(
                das_config.admissionControlPolicy,
                vim.ClusterFailoverResourcesAdmissionControlPolicy,
            ):

                das_config.admissionControlPolicy = (
                    vim.ClusterFailoverResourcesAdmissionControlPolicy(
                        cpuFailoverResourcesPercent=adm_pol_dict["cpu_failover_percent"],
                        memoryFailoverResourcesPercent=adm_pol_dict["memory_failover_percent"],
                    )
                )
        if "default_vm_settings" in ha_dict:
            vm_set_dict = ha_dict["default_vm_settings"]
            if not das_config.defaultVmSettings:
                das_config.defaultVmSettings = vim.ClusterDasVmSettings()
            if "isolation_response" in vm_set_dict:
                das_config.defaultVmSettings.isolationResponse = vm_set_dict["isolation_response"]
            if "restart_priority" in vm_set_dict:
                das_config.defaultVmSettings.restartPriority = vm_set_dict["restart_priority"]
        if "hb_ds_candidate_policy" in ha_dict:
            das_config.hBDatastoreCandidatePolicy = ha_dict["hb_ds_candidate_policy"]
        if "host_monitoring" in ha_dict:
            das_config.hostMonitoring = ha_dict["host_monitoring"]
        if "options" in ha_dict:
            das_config.option = []
            for opt_dict in ha_dict["options"]:
                das_config.option.append(vim.OptionValue(key=opt_dict["key"]))
                if "value" in opt_dict:
                    das_config.option[-1].value = opt_dict["value"]
        if "vm_monitoring" in ha_dict:
            das_config.vmMonitoring = ha_dict["vm_monitoring"]
        cluster_spec.dasConfig = das_config
    if cluster_dict.get("drs"):
        drs_dict = cluster_dict["drs"]
        drs_config = vim.ClusterDrsConfigInfo()
        if "enabled" in drs_dict:
            drs_config.enabled = drs_dict["enabled"]
        if "vmotion_rate" in drs_dict:
            drs_config.vmotionRate = 6 - drs_dict["vmotion_rate"]
        if "default_vm_behavior" in drs_dict:
            drs_config.defaultVmBehavior = vim.DrsBehavior(drs_dict["default_vm_behavior"])
        cluster_spec.drsConfig = drs_config
    if cluster_dict.get("vm_swap_placement"):
        cluster_spec.vmSwapPlacement = cluster_dict["vm_swap_placement"]
    if cluster_dict.get("vsan"):
        vsan_dict = cluster_dict["vsan"]
        if not vsan_61:  # VSAN is 6.2 and above
            if "enabled" in vsan_dict:
                if not vsan_spec.vsanClusterConfig:
                    vsan_spec.vsanClusterConfig = vim.vsan.cluster.ConfigInfo()
                vsan_spec.vsanClusterConfig.enabled = vsan_dict["enabled"]
            if "auto_claim_storage" in vsan_dict:
                if not vsan_spec.vsanClusterConfig:
                    vsan_spec.vsanClusterConfig = vim.vsan.cluster.ConfigInfo()
                if not vsan_spec.vsanClusterConfig.defaultConfig:
                    vsan_spec.vsanClusterConfig.defaultConfig = (
                        vim.VsanClusterConfigInfoHostDefaultInfo()
                    )
                elif vsan_spec.vsanClusterConfig.defaultConfig.uuid:
                    # If this remains set it caused an error
                    vsan_spec.vsanClusterConfig.defaultConfig.uuid = None
                vsan_spec.vsanClusterConfig.defaultConfig.autoClaimStorage = vsan_dict[
                    "auto_claim_storage"
                ]
            if "compression_enabled" in vsan_dict:
                if not vsan_spec.dataEfficiencyConfig:
                    vsan_spec.dataEfficiencyConfig = vim.vsan.DataEfficiencyConfig()
                vsan_spec.dataEfficiencyConfig.compressionEnabled = vsan_dict["compression_enabled"]
            if "dedup_enabled" in vsan_dict:
                if not vsan_spec.dataEfficiencyConfig:
                    vsan_spec.dataEfficiencyConfig = vim.vsan.DataEfficiencyConfig()
                vsan_spec.dataEfficiencyConfig.dedupEnabled = vsan_dict["dedup_enabled"]
        # In all cases we need to configure the vsan on the cluster
        # directly so not to have a mismatch between vsan_spec and
        # cluster_spec
        if not cluster_spec.vsanConfig:
            cluster_spec.vsanConfig = vim.VsanClusterConfigInfo()
        vsan_config = cluster_spec.vsanConfig
        if "enabled" in vsan_dict:
            vsan_config.enabled = vsan_dict["enabled"]
        if "auto_claim_storage" in vsan_dict:
            if not vsan_config.defaultConfig:
                vsan_config.defaultConfig = vim.VsanClusterConfigInfoHostDefaultInfo()
            elif vsan_config.defaultConfig.uuid:
                # If this remains set it caused an error
                vsan_config.defaultConfig.uuid = None
            vsan_config.defaultConfig.autoClaimStorage = vsan_dict["auto_claim_storage"]
    log.trace("cluster_spec = {}".format(cluster_spec))


@depends(HAS_PYVMOMI)
def list_clusters(host=None,
                  vcenter=None,
                  username=None,
                  password=None,
                  protocol=None,
                  port=None,
                  verify_ssl=True):
    """
    Returns a list of clusters for the specified host.

    host
        The location of the host.

    vcenter
        The location of the host if using VCenter.

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

        salt '*' vsphere.list_clusters 1.2.3.4 root bad-password

    """
    if salt.utils.platform.is_proxy():
        details = __salt__["vmware_info.get_proxy_connection_details"]()
    else:
        details = __salt__["vmware_info.get_connection_details"](
            host=host,
            vcenter=vcenter,
            username=username,
            password=password,
            protocol=protocol,
            port=port,
            verify_ssl=verify_ssl,
        )
    service_instance = saltext.vmware.utils.vmware.get_service_instance(**details)
    return saltext.vmware.utils.vmware.list_clusters(service_instance)


@depends(HAS_PYVMOMI)
def list_cluster(datacenter=None,
                 cluster=None,
                 host=None,
                 vcenter=None,
                 username=None,
                 password=None,
                 protocol=None,
                 port=None,
                 verify_ssl=None):

    """
    Returns a dict representation of an ESX cluster.

    datacenter
        Name of datacenter containing the cluster.
        Ignored if already contained by proxy details.
        Default value is None.

    cluster
        Name of cluster.
        Ignored if already contained by proxy details.
        Default value is None.

    host
        The location of the host.

    vcenter
        The location of the host if using VCenter.

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

    .. code-block:: bash

        # vcenter proxy
        salt '*' vsphere.list_cluster datacenter=dc1 cluster=cl1

        # esxdatacenter proxy
        salt '*' vsphere.list_cluster cluster=cl1

        # esxcluster proxy
        salt '*' vsphere.list_cluster
    """
    if salt.utils.platform.is_proxy():
        details = __salt__["vmware_info.get_proxy_connection_details"]()
    else:
        details = __salt__["vmware_info.get_connection_details"](
            host=host,
            vcenter=vcenter,
            username=username,
            password=password,
            protocol=protocol,
            port=port,
            verify_ssl=verify_ssl,
        )
    service_instance = saltext.vmware.utils.vmware.get_service_instance(**details)

    proxy_type = __salt__["vmware_info.get_proxy_type"]()
    if proxy_type == "esxdatacenter":
        dc_ref = _get_proxy_target(service_instance)
        if not cluster:
            raise ArgumentValueError("'cluster' needs to be specified")
        cluster_ref = saltext.vmware.utils.vmware.get_cluster(dc_ref, cluster)
    elif proxy_type == "esxcluster":
        cluster_ref = _get_proxy_target(service_instance)
        cluster = __salt__["esxcluster.get_details"]()["cluster"]
    log.trace(
        "Retrieving representation of cluster '%s' in a "
        "%s proxy",cluster, proxy_type
    )
    return _get_cluster_dict(cluster, cluster_ref)


@depends(HAS_PYVMOMI)
@depends(HAS_JSONSCHEMA)
def create_cluster(cluster_dict, datacenter=None, cluster=None, service_instance=None):
    """
    Creates a cluster.

    Note: cluster_dict['name'] will be overridden by the cluster param value

    config_dict
        Dictionary with the config values of the new cluster.

    datacenter
        Name of datacenter containing the cluster.
        Ignored if already contained by proxy details.
        Default value is None.

    cluster
        Name of cluster.
        Ignored if already contained by proxy details.
        Default value is None.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.
        Default is None.

    .. code-block:: bash

        # esxdatacenter proxy
        salt '*' vsphere.create_cluster cluster_dict=$cluster_dict cluster=cl1

        # esxcluster proxy
        salt '*' vsphere.create_cluster cluster_dict=$cluster_dict
    """
    # Validate cluster dictionary
    schema = ESXClusterConfigSchema.serialize()
    try:
        jsonschema.validate(cluster_dict, schema)
    except jsonschema.exceptions.ValidationError as exc:
        raise InvalidConfigError(exc)
    # Get required details from the proxy
    proxy_type = get_proxy_type()
    if proxy_type == "esxdatacenter":
        datacenter = __salt__["esxdatacenter.get_details"]()["datacenter"]
        dc_ref = _get_proxy_target(service_instance)
        if not cluster:
            raise ArgumentValueError("'cluster' needs to be specified")
    elif proxy_type == "esxcluster":
        datacenter = __salt__["esxcluster.get_details"]()["datacenter"]
        dc_ref = saltext.vmware.utils.vmware.get_datacenter(service_instance, datacenter)
        cluster = __salt__["esxcluster.get_details"]()["cluster"]

    if cluster_dict.get("vsan") and not salt.utils.vsan.vsan_supported(
        service_instance
    ):

        raise VMwareApiError("VSAN operations are not supported")
    si = service_instance
    cluster_spec = vim.ClusterConfigSpecEx()
    vsan_spec = None
    ha_config = None
    vsan_61 = None
    if cluster_dict.get("vsan"):
        # XXX The correct way of retrieving the VSAN data (on the if branch)
        #  is not supported before 60u2 vcenter
        vcenter_info = saltext.vmware.utils.vmware.get_service_info(si)
        if (
            float(vcenter_info.apiVersion) >= 6.0 and int(vcenter_info.build) >= 3634794
        ):  # 60u2
            vsan_spec = vim.vsan.ReconfigSpec(modify=True)
            vsan_61 = False
            # We need to keep HA disabled and enable it afterwards
            if cluster_dict.get("ha", {}).get("enabled"):
                enable_ha = True
                ha_config = cluster_dict["ha"]
                del cluster_dict["ha"]
        else:
            vsan_61 = True
    # If VSAN is 6.1 the configuration of VSAN happens when configuring the
    # cluster via the regular endpoint
    _apply_cluster_dict(cluster_spec, cluster_dict, vsan_spec, vsan_61)
    saltext.vmware.utils.vmware.create_cluster(dc_ref, cluster, cluster_spec)
    if not vsan_61:
        # Only available after VSAN 61
        if vsan_spec:
            cluster_ref = saltext.vmware.utils.vmware.get_cluster(dc_ref, cluster)
            salt.utils.vsan.reconfigure_cluster_vsan(cluster_ref, vsan_spec)
        if enable_ha:
            # Set HA after VSAN has been configured
            _apply_cluster_dict(cluster_spec, {"ha": ha_config})
            saltext.vmware.utils.vmware.update_cluster(cluster_ref, cluster_spec)
            # Set HA back on the object
            cluster_dict["ha"] = ha_config
    return {"create_cluster": True}


@depends(HAS_PYVMOMI)
@depends(HAS_JSONSCHEMA)
def update_cluster(cluster_dict, datacenter=None, cluster=None, service_instance=None):
    """
    Updates a cluster.

    config_dict
        Dictionary with the config values of the new cluster.

    datacenter
        Name of datacenter containing the cluster.
        Ignored if already contained by proxy details.
        Default value is None.

    cluster
        Name of cluster.
        Ignored if already contained by proxy details.
        Default value is None.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.
        Default is None.

    .. code-block:: bash

        # esxdatacenter proxy
        salt '*' vsphere.update_cluster cluster_dict=$cluster_dict cluster=cl1

        # esxcluster proxy
        salt '*' vsphere.update_cluster cluster_dict=$cluster_dict

    """
    # Validate cluster dictionary
    schema = ESXClusterConfigSchema.serialize()
    try:
        jsonschema.validate(cluster_dict, schema)
    except jsonschema.exceptions.ValidationError as exc:
        raise InvalidConfigError(exc)
    # Get required details from the proxy
    proxy_type = get_proxy_type()
    if proxy_type == "esxdatacenter":
        datacenter = __salt__["esxdatacenter.get_details"]()["datacenter"]
        dc_ref = _get_proxy_target(service_instance)
        if not cluster:
            raise ArgumentValueError("'cluster' needs to be specified")
    elif proxy_type == "esxcluster":
        datacenter = __salt__["esxcluster.get_details"]()["datacenter"]
        dc_ref = saltext.vmware.utils.vmware.get_datacenter(service_instance, datacenter)
        cluster = __salt__["esxcluster.get_details"]()["cluster"]

    if cluster_dict.get("vsan") and not salt.utils.vsan.vsan_supported(
        service_instance
    ):

        raise VMwareApiError("VSAN operations are not supported")

    cluster_ref = saltext.vmware.utils.vmware.get_cluster(dc_ref, cluster)
    cluster_spec = vim.ClusterConfigSpecEx()
    props = saltext.vmware.utils.vmware.get_properties_of_managed_object(
        cluster_ref, properties=["configurationEx"]
    )
    # Copy elements we want to update to spec
    for p in ["dasConfig", "drsConfig"]:
        setattr(cluster_spec, p, getattr(props["configurationEx"], p))
    if props["configurationEx"].vsanConfigInfo:
        cluster_spec.vsanConfig = props["configurationEx"].vsanConfigInfo
    vsan_spec = None
    vsan_61 = None
    if cluster_dict.get("vsan"):
        # XXX The correct way of retrieving the VSAN data (on the if branch)
        #  is not supported before 60u2 vcenter
        vcenter_info = saltext.vmware.utils.vmware.get_service_info(service_instance)
        if (
            float(vcenter_info.apiVersion) >= 6.0 and int(vcenter_info.build) >= 3634794
        ):  # 60u2
            vsan_61 = False
            vsan_info = salt.utils.vsan.get_cluster_vsan_info(cluster_ref)
            vsan_spec = vim.vsan.ReconfigSpec(modify=True)
            # Only interested in the vsanClusterConfig and the
            # dataEfficiencyConfig
            # vsan_spec.vsanClusterConfig = vsan_info
            vsan_spec.dataEfficiencyConfig = vsan_info.dataEfficiencyConfig
            vsan_info.dataEfficiencyConfig = None
        else:
            vsan_61 = True

    _apply_cluster_dict(cluster_spec, cluster_dict, vsan_spec, vsan_61)
    # We try to reconfigure vsan first as it fails if HA is enabled so the
    # command will abort not having any side-effects
    # also if HA was previously disabled it can be enabled automatically if
    # desired
    if vsan_spec:
        log.trace("vsan_spec = {}".format(vsan_spec))
        salt.utils.vsan.reconfigure_cluster_vsan(cluster_ref, vsan_spec)

        # We need to retrieve again the properties and reapply them
        # As the VSAN configuration has changed
        cluster_spec = vim.ClusterConfigSpecEx()
        props = saltext.vmware.utils.vmware.get_properties_of_managed_object(
            cluster_ref, properties=["configurationEx"]
        )
        # Copy elements we want to update to spec
        for p in ["dasConfig", "drsConfig"]:
            setattr(cluster_spec, p, getattr(props["configurationEx"], p))
        if props["configurationEx"].vsanConfigInfo:
            cluster_spec.vsanConfig = props["configurationEx"].vsanConfigInfo
        # We only need to configure the cluster_spec, as if it were a vsan_61
        # cluster
        _apply_cluster_dict(cluster_spec, cluster_dict)
    saltext.vmware.utils.vmware.update_cluster(cluster_ref, cluster_spec)
    return {"update_cluster": True}
