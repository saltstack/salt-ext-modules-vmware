# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pytest
import saltext.vmware.modules.tag as tagging


def test_category_list(patch_salt_globals_tag):
    """
    Test create tag functionality
    """
    cats = tagging.list_category()
    if len(cats['categories']) > 0:
        assert 'urn:vmomi:InventoryServiceCategory' in cats["categories"][0]
    else:
        pytest.skip("test requires at least one category")


def test_tag_list(patch_salt_globals_tag):
    """
    Test list tags functionality
    """
    tags = tagging.list_()
    if len(tags['tags']) > 0:
        assert 'urn:vmomi:InventoryServiceTag:' in tags["tags"][0]
    else:
        pytest.skip("test requires at least one tag")


def test_tag_create(patch_salt_globals_tag):
    """
    Test create tag functionality
    """
    cats = tagging.list_category()
    if len(cats['categories']) > 0:
        res = tagging.create("test tag", cats['categories'][0], description="testy test tester")
        assert 'urn:vmomi:InventoryServiceTag:' in res["tag"]
    else:
        pytest.skip("test requires at least one category")


def test_tag_get(patch_salt_globals_tag):
    """
    Test get tag functionality
    """
    tags = tagging.list_()
    if len(tags['tags']) > 0:
        res = tagging.get(tags['tags'][0])
        assert 'urn:vmomi:InventoryServiceTag:' in res["tag"]["id"]
    else:
        pytest.skip("test requires at least one tag")


def test_tag_update(patch_salt_globals_tag):
    """
    Test update tag functionality
    """
    tags = tagging.list_()
    if len(tags['tags']) > 0:
        for tag in tags['tags']:
            res = tagging.get(tag)
            if res["tag"]["name"] == 'test tag':
                update_res = tagging.update(res["tag"]["id"], description='new discription')
                assert 'updated' in update_res["tag"]
                break
    else:
        pytest.skip("test requires at least one tag")


def test_tag_delete(patch_salt_globals_tag):
    """
    Test delete tag functionality
    """
    tags = tagging.list_()
    if len(tags['tags']) > 0:
        for tag in tags['tags']:
            res = tagging.get(tag)
            if res["tag"]["name"] == 'test tag':
                update_res = tagging.delete(res["tag"]["id"])
                assert 'deleted' in update_res["tag"]
                break
    else:
        pytest.skip("test requires at least one tag")
