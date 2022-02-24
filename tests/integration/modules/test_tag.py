# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pytest
import saltext.vmware.modules.tag as tagging


def test_category_list(patch_salt_globals_tag, vmware_category):
    """
    Test category list functionality
    """
    cats = tagging.list_category()
    assert "urn:vmomi:InventoryServiceCategory" in cats["categories"][0]


def test_category_get(patch_salt_globals_tag, vmware_category):
    """
    Test category get functionality
    """

    cat = tagging.get_category(vmware_category)
    assert "urn:vmomi:InventoryServiceCategory" in cat["category"]["id"]


def test_tag_list(patch_salt_globals_tag, vmware_tag):
    """
    Test list tags functionality
    """
    tags = tagging.list_()
    assert "urn:vmomi:InventoryServiceTag:" in tags["tags"][0]


def test_tag_create(patch_salt_globals_tag, vmware_tag_name_c):
    """
    Test create tag functionality
    """
    res = tagging.create(
        vmware_tag_name_c[0], vmware_tag_name_c[1], description="testy test tester"
    )
    assert "urn:vmomi:InventoryServiceTag:" in res["tag"]


def test_tag_get(patch_salt_globals_tag, vmware_tag):
    """
    Test get tag functionality
    """
    res = tagging.get(vmware_tag)
    assert "urn:vmomi:InventoryServiceTag:" in res["tag"]["id"]


def test_tag_update(patch_salt_globals_tag, vmware_tag):
    """
    Test update tag functionality
    """
    update_res = tagging.update(vmware_tag, description="new discription")
    assert "updated" in update_res["tag"]


def test_tag_delete(patch_salt_globals_tag, vmware_category):
    """
    Test delete tag functionality
    """
    res = tagging.create("test-tag", vmware_category, description="test tag")
    update_res = tagging.delete(res["tag"])
    assert "deleted" in update_res["tag"]


def test_cat_create(patch_salt_globals_tag, vmware_cat_name_c):
    """
    Test create category functionality
    """
    res = tagging.create_category(vmware_cat_name_c, ["string"], "SINGLE", "test category")
    assert "urn:vmomi:InventoryServiceCategory:" in res["category"]


def test_cat_update(patch_salt_globals_tag, vmware_category):
    """
    Test update category functionality
    """

    res = tagging.get_category(vmware_category)
    update_res = tagging.update_category(
        res["category"]["id"],
        res["category"]["name"],
        res["category"]["associable_types"],
        res["category"]["cardinality"],
        "new description",
    )
    assert "updated" in update_res["category"]


def test_cat_delete(patch_salt_globals_tag):
    """
    Test update category functionality
    """
    res = tagging.create_category("test cat", ["string"], "SINGLE", "test category")
    delete_res = tagging.delete_category(res["category"])
    assert "deleted" in delete_res["category"]
