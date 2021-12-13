# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pytest
import saltext.vmware.modules.tag as tagging
import saltext.vmware.states.tag as tagging_state


def test_manage_create(patch_salt_globals_tag_state, patch_salt_globals_tag):
    """
    test tag manage create
    """
    cats = tagging.list_category()
    if len(cats["categories"]) > 0:
        res = tagging_state.manage(
            "create",
            tag_name="state tag",
            tag_description="testing state tag create",
            category_id=cats["categories"][0],
        )
        assert "created" in res["comment"]
    else:
        pytest.skip("test requires at least one category")


def test_manage_update(patch_salt_globals_tag_state, patch_salt_globals_tag):
    """
    test tag manage update
    """
    tags = tagging.list_()
    if len(tags["tags"]) > 0:
        for tag in tags["tags"]:
            res = tagging.get(tag)
            if res["tag"]["name"] == "state tag":
                update_res = tagging_state.manage(
                    "update", tag_description="new discription", tag_id=res["tag"]["id"]
                )
                assert "updated" in update_res["comment"]
                break
    else:
        pytest.skip("test requires at least one tag")


def test_manage_delete(patch_salt_globals_tag_state, patch_salt_globals_tag):
    """
    test tag manage delete
    """
    tags = tagging.list_()
    if len(tags["tags"]) > 0:
        for tag in tags["tags"]:
            res = tagging.get(tag)
            if res["tag"]["name"] == "state tag":
                update_res = tagging_state.manage("delete", tag_id=res["tag"]["id"])
                assert "deleted" in update_res["comment"]
                break
    else:
        pytest.skip("test requires at least one tag")
