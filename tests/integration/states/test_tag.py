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
        res = tagging_state.present(
            "state tag",
            description="testing state tag create",
            category_id=cats["categories"][0],
        )
        assert "created" in res["comment"]
    else:
        pytest.skip("test requires at least one category")


def test_manage_update(patch_salt_globals_tag_state, patch_salt_globals_tag):
    """
    test tag manage update
    """

    update_res = tagging_state.present("state tag", description="new discription")
    assert "updated" in update_res["comment"]


def test_manage_delete(patch_salt_globals_tag_state, patch_salt_globals_tag):
    """
    test tag manage delete
    """
    update_res = tagging_state.absent("state tag")
    assert "deleted" in update_res["comment"]
