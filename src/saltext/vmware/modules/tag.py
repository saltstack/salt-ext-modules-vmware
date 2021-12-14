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
    return {"tag": response["value"]}


def get(tag_id):
    """
    Returns info on given tag.

    tag_id
        (string) Tag ID of type: com.vmware.cis.tagging.Tag.
    """
    url = f"/rest/com/vmware/cis/tagging/tag/id:{tag_id}"
    response = connect.request(url, "GET", opts=__opts__, pillar=__pillar__)
    response = response["response"].json()
    return {"tag": response["value"]}


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
        return {"tag": "updated"}
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
        return {"tag": "deleted"}
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
    return {"tags": response["value"]}


def list_category():
    """
    Lists IDs for all the categories on a given vCenter.
    """
    response = connect.request(
        "/rest/com/vmware/cis/tagging/category", "GET", opts=__opts__, pillar=__pillar__
    )
    response = response["response"].json()
    return {"categories": response["value"]}


def get_category(category_id):
    """
    Returns info on given category.

    category_id
        (string) Category ID of type: com.vmware.cis.tagging.Category.
    """
    url = f"/rest/com/vmware/cis/tagging/category/id:{category_id}"
    response = connect.request(url, "GET", opts=__opts__, pillar=__pillar__)
    response = response["response"].json()
    return {"category": response["value"]}