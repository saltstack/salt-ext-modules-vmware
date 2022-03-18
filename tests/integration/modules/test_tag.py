# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pytest
import saltext.vmware.modules.tag as tagging


def test_category_list(vmware_category):
    """
    Test category list functionality
    """
    cats = tagging.list_category()
    for cat in cats:
        assert "urn:vmomi:InventoryServiceCategory" in cat


def test_category_get(vmware_category):
    """
    Test category get functionality
    """

    cat = tagging.get_category(vmware_category)
    assert "urn:vmomi:InventoryServiceCategory" in cat["id"]


def test_tag_list(vmware_tag):
    """
    Test list tags functionality
    """
    tags = tagging.list_()
    for tag in tags:
        assert "urn:vmomi:InventoryServiceTag:" in tag


def test_tag_create(vmware_tag_name_c):
    """
    Test create tag functionality
    """
    tag_name, cat_id = vmware_tag_name_c
    res = tagging.create(tag_name, cat_id, description="testy test tester")
    assert "urn:vmomi:InventoryServiceTag:" in res


def test_tag_get(vmware_tag):
    """
    Test get tag functionality
    """
    res = tagging.get(vmware_tag)
    assert "urn:vmomi:InventoryServiceTag:" in res["id"]


def test_tag_update(vmware_tag):
    """
    Test update tag functionality
    """
    update_res = tagging.update(vmware_tag, description="new discription")
    assert "updated" in update_res


def test_tag_delete(vmware_category):
    """
    Test delete tag functionality
    """
    res = tagging.create("test-tag", vmware_category, description="test tag")
    update_res = tagging.delete(res)
    assert "deleted" in update_res


def test_cat_create(vmware_cat_name_c):
    """
    Test create category functionality
    """
    res = tagging.create_category(vmware_cat_name_c, ["string"], "SINGLE", "test category")
    assert "urn:vmomi:InventoryServiceCategory:" in res


def test_cat_update(vmware_category):
    """
    Test update category functionality
    """

    res = tagging.get_category(vmware_category)
    update_res = tagging.update_category(
        res["id"],
        res["name"],
        res["associable_types"],
        res["cardinality"],
        "new description",
    )
    assert "updated" in update_res


def test_cat_delete(patch_salt_globals_tag):
    """
    Test update category functionality
    """
    res = tagging.create_category("test cat", ["string"], "SINGLE", "test category")
    delete_res = tagging.delete_category(res)
    assert "deleted" in delete_res
