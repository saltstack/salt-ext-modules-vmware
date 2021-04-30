# SPDX-License-Identifier: Apache-2.0
"""
Module used to access the vcenter proxy connection methods
"""
import logging

import salt.utils.platform

log = logging.getLogger(__name__)

__proxyenabled__ = ["vcenter"]
# Define the module's virtual name
__virtualname__ = "vcenter"


def __virtual__():
    """
    Only work on proxy
    """
    if salt.utils.platform.is_proxy():
        return __virtualname__
    return False


def get_details():
    return __proxy__["vcenter.get_details"]()


def _get_capability_definition_dict(cap_metadata):
    # We assume each capability definition has one property with the same id
    # as the capability so we display its type as belonging to the capability
    # The object model permits multiple properties
    return {
        "namespace": cap_metadata.id.namespace,
        "id": cap_metadata.id.id,
        "mandatory": cap_metadata.mandatory,
        "description": cap_metadata.summary.summary,
        "type": cap_metadata.propertyMetadata[0].type.typeName,
    }


def list_capability_definitions(service_instance=None):
    """
    Returns a list of the metadata of all capabilities in the vCenter.

    service_instance
        Service instance (vim.ServiceInstance) of the vCenter.
        Default is None.

    .. code-block:: bash

        salt '*' vsphere.list_capabilities
    """
    profile_manager = salt.utils.pbm.get_profile_manager(service_instance)
    ret_list = [
        _get_capability_definition_dict(c)
        for c in salt.utils.pbm.get_capability_definitions(profile_manager)
    ]
    return ret_list
