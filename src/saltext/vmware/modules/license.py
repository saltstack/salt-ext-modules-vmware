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


__virtualname__ = "vmware_licenses"


def __virtual__():
    return __virtualname__


def _get_entity(service_instance, entity):
    """
    Returns the entity associated with the entity dict representation

    Supported entities: cluster, vcenter

    Expected entity format:

    .. code-block:: python

        cluster:
            {'type': 'cluster',
             'datacenter': <datacenter_name>,
             'cluster': <cluster_name>}
        vcenter:
            {'type': 'vcenter'}

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.

    entity
        Entity dict in the format above
    """

    log.trace("Retrieving entity: {}".format(entity))
    if entity["type"] == "cluster":
        dc_ref = salt.utils.vmware.get_datacenter(service_instance, entity["datacenter"])
        return salt.utils.vmware.get_cluster(dc_ref, entity["cluster"])
    elif entity["type"] == "vcenter":
        return None
    raise ArgumentValueError("Unsupported entity type '{}'" "".format(entity["type"]))


def _validate_entity(entity):
    """
    Validates the entity dict representation

    entity
        Dictionary representation of an entity.
        See ``_get_entity`` docstrings for format.
    """

    # Validate entity:
    if entity["type"] == "cluster":
        schema = ESXClusterEntitySchema.serialize()
    elif entity["type"] == "vcenter":
        schema = VCenterEntitySchema.serialize()
    else:
        raise ArgumentValueError("Unsupported entity type '{}'" "".format(entity["type"]))
    try:
        jsonschema.validate(entity, schema)
    except jsonschema.exceptions.ValidationError as exc:
        raise InvalidEntityError(exc)


def list_licenses(service_instance=None):
    """
    Lists all licenses on a vCenter.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.list_licenses
    """
    log.trace("Retrieving all licenses")
    licenses = saltext.vmware.utils.vmware.get_licenses(service_instance)
    ret_dict = [
        {
            "key": l.licenseKey,
            "name": l.name,
            "description": l.labels[0].value if l.labels else None,
            # VMware handles unlimited capacity as 0
            "capacity": l.total if l.total > 0 else sys.maxsize,
            "used": l.used if l.used else 0,
        }
        for l in licenses
    ]
    return ret_dict


def add_license(key, description, safety_checks=True, service_instance=None):
    """
    Adds a license to the vCenter or ESXi host

    key
        License key.

    description
        License description added in as a label.

    safety_checks
        Specify whether to perform safety check or to skip the checks and try
        performing the required task

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.add_license key=<license_key> desc='License desc'
    """
    log.trace("Adding license '{}'".format(key))
    saltext.vmware.utils.vmware.add_license(service_instance, key, description)
    return True


def list_assigned_licenses(entity, entity_display_name, license_keys=None, service_instance=None):
    """
    Lists the licenses assigned to an entity

    entity
        Dictionary representation of an entity.
        See ``_get_entity`` docstrings for format.

    entity_display_name
        Entity name used in logging

    license_keys:
        List of license keys to be retrieved. Default is None.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.list_assigned_licenses
            entity={type:cluster,datacenter:dc,cluster:cl}
            entiy_display_name=cl
    """
    log.trace("Listing assigned licenses of entity {}" "".format(entity))
    _validate_entity(entity)

    assigned_licenses = saltext.vmware.utils.vmware.get_assigned_licenses(
        service_instance,
        entity_ref=_get_entity(service_instance, entity),
        entity_name=entity_display_name,
    )

    return [
        {
            "key": l.licenseKey,
            "name": l.name,
            "description": l.labels[0].value if l.labels else None,
            # VMware handles unlimited capacity as 0
            "capacity": l.total if l.total > 0 else sys.maxsize,
        }
        for l in assigned_licenses
        if (license_keys is None) or (l.licenseKey in license_keys)
    ]


def assign_license(
    license_key,
    license_name,
    entity,
    entity_display_name,
    safety_checks=True,
    service_instance=None,
):
    """
    Assigns a license to an entity

    license_key
        Key of the license to assign
        See ``_get_entity`` docstrings for format.

    license_name
        Display name of license

    entity
        Dictionary representation of an entity

    entity_display_name
        Entity name used in logging

    safety_checks
        Specify whether to perform safety check or to skip the checks and try
        performing the required task. Default is False.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter/ESXi host.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.assign_license license_key=00000:00000
            license name=test entity={type:cluster,datacenter:dc,cluster:cl}
    """
    log.trace("Assigning license {} to entity {}" "".format(license_key, entity))
    _validate_entity(entity)
    if safety_checks:
        licenses = saltext.vmware.utils.vmware.get_licenses(service_instance)
        if not [l for l in licenses if l.licenseKey == license_key]:
            raise VMwareObjectRetrievalError("License '{}' wasn't found" "".format(license_name))
    saltext.vmware.utils.vmware.assign_license(
        service_instance,
        license_key,
        license_name,
        entity_ref=_get_entity(service_instance, entity),
        entity_name=entity_display_name,
    )
