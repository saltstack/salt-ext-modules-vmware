# SPDX-License-Identifier: Apache-2.0
import logging

import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.connect as connect
import saltext.vmware.utils.vm as utils_vm
from saltext.vmware.modules.tag import update

log = logging.getLogger(__name__)

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_tag"
__proxyenabled__ = ["vmware_tag"]


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def present(name, description=None, category_id=None):
    """
    Create and update a tag instance.

    name
        Name of tag.

    description
        Description of tag.

    category_id
        (string) Category ID of type: com.vmware.cis.tagging.Tag. Only optional when updating
    """
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}
    res = connect.request(
        "/rest/com/vmware/cis/tagging/tag", "GET", opts=__opts__, pillar=__pillar__
    )
    response = res["response"].json()
    token = res["token"]
    found = None
    for tag in response["value"]:
        url = f"/rest/com/vmware/cis/tagging/tag/id:{tag}"
        tag_ref = connect.request(url, "GET", token=token, opts=__opts__, pillar=__pillar__)
        tag_ref = tag_ref["response"].json()
        if tag_ref["value"]["name"] == name:
            found = tag_ref["value"]
            break
    if found:
        if description == found["description"]:
            ret["comment"] = "tag exists"
            return ret
        else:
            id = found["id"]
            spec = {"update_spec": {"description": description}}
            url = f"/rest/com/vmware/cis/tagging/tag/id:{id}"
            updated = connect.request(
                url, "PATCH", body=spec, token=token, opts=__opts__, pillar=__pillar__
            )
            if updated["response"].status_code == 200:
                ret["changes"]["new"] = {}
                ret["changes"]["old"] = {}
                ret["changes"]["old"]["description"] = found["description"]
                ret["changes"]["new"]["description"] = description
                ret["comment"] = "updated"
                return ret
            ret["status_code"] = updated["response"].status_code
            ret["reason"] = updated["response"].reason
            ret["comment"] = "failed to update"
            ret["result"] = False
            return ret
    else:
        if category_id:
            data = {
                "create_spec": {
                    "category_id": category_id,
                    "description": description,
                    "name": name,
                }
            }
            create = connect.request(
                "/rest/com/vmware/cis/tagging/tag",
                "POST",
                body=data,
                token=token,
                opts=__opts__,
                pillar=__pillar__,
            )
            response = create["response"].json()
            ret["changes"]["tag_id"] = response["value"]
            ret["comment"] = "created"
            return ret
        else:
            ret["result"] = False
            ret["comment"] = "category_id required to create a tag"
            return ret


def absent(name):
    """
    Delete tag.

    name
        Name of tag.
    """
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}
    res = connect.request(
        "/rest/com/vmware/cis/tagging/tag", "GET", opts=__opts__, pillar=__pillar__
    )
    response = res["response"].json()
    token = res["token"]
    found = None
    for tag in response["value"]:
        url = f"/rest/com/vmware/cis/tagging/tag/id:{tag}"
        tag_ref = connect.request(url, "GET", token=token, opts=__opts__, pillar=__pillar__)
        tag_ref = tag_ref["response"].json()
        if tag_ref["value"]["name"] == name:
            found = tag_ref["value"]
            break
    if found:
        id = found["id"]
        url = f"/rest/com/vmware/cis/tagging/tag/id:{id}"
        delete = connect.request(url, "DELETE", token=token, opts=__opts__, pillar=__pillar__)
        if delete["response"].status_code == 200:
            ret["comment"] = "deleted"
            return ret
        ret["status_code"] = delete["response"].status_code
        ret["reason"] = delete["response"].reason
        ret["comment"] = "failed to delete"
        ret["result"] = False
        return ret
    else:
        ret["comment"] = "Tag does not exist"
        return ret
