# Copyright 2021 VMware, Inc.
# SPDX-License: Apache-2.0
import logging

import salt.exceptions
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.connect as connect

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_tag"
__func_alias__ = {"list_": "list"}


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def create(tag_name, category_id, description=""):
    """
    Create a new tag.

    tag_name
        Name of tag.

    category_id
        (string) Category ID of type: com.vmware.cis.tagging.Tag.

    description
        (optional) Description for the tag being created.
    """
    data = {
        "create_spec": {"category_id": category_id, "description": description, "name": tag_name}
    }
    response = connect.request(
        "/rest/com/vmware/cis/tagging/tag", "POST", body=data, opts=__opts__, pillar=__pillar__
    )
    response = response["response"].json()
    return response["value"]


def get(tag_id):
    """
    Returns info on given tag.

    tag_id
        (string) Tag ID of type: com.vmware.cis.tagging.Tag.
    """
    url = f"/rest/com/vmware/cis/tagging/tag/id:{tag_id}"
    response = connect.request(url, "GET", opts=__opts__, pillar=__pillar__)
    response = response["response"].json()
    return response["value"]


def update(tag_id, tag_name=None, description=None):
    """
    Updates give tag.

    tag_id
        (string) Tag ID of type: com.vmware.cis.tagging.Tag.

    tag_name
        Name of tag.

    description
        (optional) Description for the tag being created.
    """
    spec = {"update_spec": {}}
    if tag_name:
        spec["update_spec"]["name"] = tag_name
    if description:
        spec["update_spec"]["description"] = description
    url = f"/rest/com/vmware/cis/tagging/tag/id:{tag_id}"
    response = connect.request(url, "PATCH", body=spec, opts=__opts__, pillar=__pillar__)
    if response["response"].status_code == 200:
        return "updated"
    return {
        "tag": "failed to update",
        "status_code": response["response"].status_code,
        "reason": response["response"].reason,
    }


def delete(tag_id):
    """
    Delete given tag.

    tag_id
        (string) Tag ID of type: com.vmware.cis.tagging.Tag.
    """
    url = f"/rest/com/vmware/cis/tagging/tag/id:{tag_id}"
    response = connect.request(url, "DELETE", opts=__opts__, pillar=__pillar__)
    if response["response"].status_code == 200:
        return "deleted"
    return {
        "tag": "failed to update",
        "status_code": response.status_code,
        "reason": response.reason,
    }


def list_():
    """
    Lists IDs for all the tags on a given vCenter.
    """
    response = connect.request(
        "/rest/com/vmware/cis/tagging/tag", "GET", opts=__opts__, pillar=__pillar__
    )
    response = response["response"].json()
    return response["value"]


def list_category():
    """
    Lists IDs for all the categories on a given vCenter.
    """
    response = connect.request(
        "/rest/com/vmware/cis/tagging/category", "GET", opts=__opts__, pillar=__pillar__
    )
    response = response["response"].json()
    return response["value"]


def get_category(category_id):
    """
    Returns info on given category.

    category_id
        (string) Category ID of type: com.vmware.cis.tagging.Category.
    """
    url = f"/rest/com/vmware/cis/tagging/category/id:{category_id}"
    response = connect.request(url, "GET", opts=__opts__, pillar=__pillar__)
    response = response["response"].json()
    return response["value"]


def create_category(category_name, associable_types, cardinality, description=""):
    """
    Create a new category.

    category_name
        The display name of the category.

    associable_types
        (list) Object types to which this category’s tags can be attached.

    cardinality
        The CategoryModel.Cardinality enumerated type defines the number of tags in a category that can be assigned to an object. SINGLE, MULTIPLE

    description
        (optional) The description of the category.
    """
    data = {
        "create_spec": {
            "associable_types": associable_types,
            "cardinality": cardinality,
            "description": description,
            "name": category_name,
        }
    }
    response = connect.request(
        "/rest/com/vmware/cis/tagging/category", "POST", body=data, opts=__opts__, pillar=__pillar__
    )
    response = response["response"].json()
    return response["value"]


def update_category(
    category_id, category_name=None, associable_types=None, cardinality=None, description=""
):
    """
    Update a new category.

    category_id
        The identifier of the category to be updated. The parameter must be an identifier for the resource type: com.vmware.cis.tagging.Category.

    category_name
        The display name of the category.

    associable_types
        (list) Object types to which this categorys tags can be attached.

    cardinality
        The CategoryModel.Cardinality enumerated type defines the number of tags in a category that can be assigned to an object. SINGLE, MULTIPLE

    description
        (optional) The description of the category.
    """
    spec = {"update_spec": {}}
    if category_name:
        spec["update_spec"]["name"] = category_name
    if associable_types:
        spec["update_spec"]["associable_types"] = associable_types
    if cardinality:
        spec["update_spec"]["cardinality"] = cardinality
    if description:
        spec["update_spec"]["description"] = description
    url = f"/rest/com/vmware/cis/tagging/category/id:{category_id}"
    response = connect.request(url, "PATCH", body=spec, opts=__opts__, pillar=__pillar__)
    if response["response"].status_code == 200:
        return "updated"
    return {
        "category": "failed to update",
        "status_code": response["response"].status_code,
        "reason": response["response"].reason,
    }


def delete_category(category_id):
    """
    Delete given category.

    category_id
        The identifier of category to be deleted. The parameter must be an identifier for the resource type: com.vmware.cis.tagging.Category.
    """
    url = f"/rest/com/vmware/cis/tagging/category/id:{category_id}"
    response = connect.request(url, "DELETE", opts=__opts__, pillar=__pillar__)
    if response["response"].status_code == 200:
        return "deleted"
    return {
        "category": "failed to update",
        "status_code": response.status_code,
        "reason": response.reason,
    }
