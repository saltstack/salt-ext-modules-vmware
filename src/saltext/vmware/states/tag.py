# SPDX-License-Identifier: Apache-2.0
import logging

import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.connect as connect
import saltext.vmware.utils.vm as utils_vm

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


def manage(name, tag_name=None, tag_description=None, tag_id=None, category_id=None):
    """
    Manage tag instance.

    name
        Name of task to be preformed (create, update, delete)

    tag_name
        (integer, optional) Boot delay. When powering on or resetting, delay boot order by given milliseconds. Defaults to 0.

    tag_description
        (boolean, optional) During the next boot, force entry into the BIOS setup screen. Defaults to False.

    tag_id
        Tag ID of string of type: com.vmware.cis.tagging.Tag.

    category_id
        (string) Category ID of type: com.vmware.cis.tagging.Tag.
    """
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}
    response = None
    if tag_id:
        url = f"/rest/com/vmware/cis/tagging/tag/id:{tag_id}"
        response = connect.request(url, "GET", opts=__opts__, pillar=__pillar__)
        response = response.json()

    if name == "update":
        if (
            response["value"]["name"] == tag_name
            and response["value"]["description"] == tag_description
        ):
            ret["comment"] = "already configured this way"
            return ret
        else:
            ret["changes"]["new"] = {}
            ret["changes"]["old"] = {}
            spec = {"update_spec": {}}
            if tag_name:
                ret["changes"]["old"]["name"] = response["value"]["name"]
                spec["update_spec"]["name"] = tag_name
                ret["changes"]["new"]["name"] = tag_name
            if tag_description:
                ret["changes"]["old"]["description"] = response["value"]["description"]
                spec["update_spec"]["description"] = tag_description
                ret["changes"]["new"]["description"] = tag_description
            url = f"/rest/com/vmware/cis/tagging/tag/id:{tag_id}"
            response = connect.request(url, "PATCH", body=spec, opts=__opts__, pillar=__pillar__)
            ret["comment"] = "updated"
            return ret

    elif name == "create":
        spec = {
            "create_spec": {
                "category_id": category_id,
                "description": tag_description,
                "name": tag_name,
            }
        }
        response = connect.request(
            "/rest/com/vmware/cis/tagging/tag", "POST", body=spec, opts=__opts__, pillar=__pillar__
        )
        response = response.json()
        ret["changes"]["tag_id"] = response["value"]
        ret["comment"] = "created"
        return ret

    elif name == "delete":
        url = f"/rest/com/vmware/cis/tagging/tag/id:{tag_id}"
        response = connect.request(url, "DELETE", opts=__opts__, pillar=__pillar__)
        ret["comment"] = "deleted"
        return ret

    else:
        ret[
            "comment"
        ] = "Name not reconized, please choose one of the following: create, update, delete"
        return ret
