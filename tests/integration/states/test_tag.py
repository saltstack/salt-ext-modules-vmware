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


def test_manage_update(patch_salt_globals_tag_state):
    """
    test tag manage update
    """
    res = tagging_state.present("state tag", description="new discription")
    assert "updated" in res["comment"]


def test_manage_delete(patch_salt_globals_tag_state):
    """
    test tag manage delete
    """
    res = tagging_state.absent("state tag")
    assert "deleted" in res["comment"]


def test_manage_create_cat_test(patch_salt_globals_tag_state_test):
    """
    test category manage create test = true
    """
    res = tagging_state.present_category(
            "state test cat",
            ['string'],
            'SINGLE', 
            "test category"
        )
    assert "state test cat category will be created" in res["comment"]


def test_manage_create_cat(patch_salt_globals_tag_state):
    """
    test category manage create
    """
    res = tagging_state.present_category(
            "state test cat",
            ['string'],
            'SINGLE', 
            "test category"
        )
    assert "created" in res["comment"]


def test_manage_update_cat_test(patch_salt_globals_tag_state_test):
    """
    test tag manage update test = true
    """

    res = tagging_state.present_category(
            "state test cat",
            ['string'],
            'SINGLE', 
            "new description"
        )
    assert "state test cat category will be updated" in res["comment"]


def test_manage_update_cat(patch_salt_globals_tag_state):
    """
    test tag manage update
    """

    res = tagging_state.present_category(
            "state test cat",
            ['string'],
            'SINGLE', 
            "new description"
        )
    assert "updated" in res["comment"]


def test_manage_delete_cat_test(patch_salt_globals_tag_state_test):
    """
    test tag manage delete test = true
    """
    res = tagging_state.absent_category("state test cat")
    assert "state test cat category will be deleted" in res["comment"]


def test_manage_delete_cat(patch_salt_globals_tag_state):
    """
    test tag manage delete
    """
    res = tagging_state.absent_category("state test cat")
    assert "deleted" in res["comment"]