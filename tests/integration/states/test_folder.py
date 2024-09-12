# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import patch

import pytest
import saltext.vmware.states.folder as folder


@pytest.fixture
def patch_salt_globals_folder_state(vmware_conf):
    """
    Patch __opts__ and __pillar__
    """
    with (
        patch.object(folder, "__opts__", {"test": False}, create=True),
        patch.object(folder, "__pillar__", vmware_conf, create=True),
    ):
        yield


@pytest.fixture
def patch_salt_globals_folder_state_test(patch_salt_globals_folder_state):
    """
    Patch __opts__ and __pillar__
    """

    with patch.dict(folder.__opts__, {"test": True}):
        yield


@pytest.fixture
def test_folder_name():
    yield "test_folder"
    try:
        folder.manage("test_folder", "destroy", "Datacenter", "vm")
    except Exception:
        pass


@pytest.fixture
def test_folder_name_c():
    try:
        folder.manage("test_folder", "create", "Datacenter", "vm")
        yield "test_folder"
    finally:
        folder.manage("test_folder", "destroy", "Datacenter", "vm")


@pytest.fixture
def test_folder_name_rename():
    try:
        folder.manage("test_folder", "create", "Datacenter", "vm")
        yield "test_folder", "test_folder_new"
    finally:
        folder.manage("test_folder_new", "destroy", "Datacenter", "vm")


@pytest.fixture
def test_folder_name_move():
    try:
        folder.manage("test_folder", "create", "Datacenter", "vm")
        folder.manage("test_folder_top", "create", "Datacenter", "vm")
        yield "test_folder", "test_folder_top"
    finally:
        folder.manage("test_folder", "destroy", "Datacenter", "vm")
        folder.manage("test_folder_top", "destroy", "Datacenter", "vm")


def test_create_folder_test(patch_salt_globals_folder_state_test):
    """
    test create folder in test mode
    """
    ret = folder.manage("test_folder", "create", "Datacenter", "vm")
    assert ret["result"] == True
    assert ret["comment"] == "These options are set to change."
    assert ret["changes"]["new"] == "folder test_folder will be created"


def test_create_folder(patch_salt_globals_folder_state, test_folder_name):
    """
    test create folder
    """
    ret = folder.manage(test_folder_name, "create", "Datacenter", "vm")
    assert ret["result"] == True
    assert ret["comment"] == "created"
    assert ret["changes"]["new"] == "folder test_folder created"


def test_destroy_folder_test(patch_salt_globals_folder_state_test, test_folder_name_c):
    """
    test destroy folder in test mode
    """
    ret = folder.manage(test_folder_name_c, "destroy", "Datacenter", "vm")
    assert ret["result"] == True
    assert ret["comment"] == "These options are set to change."
    assert ret["changes"]["new"] == "folder test_folder will be destroyed"


def test_destroy_folder(patch_salt_globals_folder_state):
    """
    test destroy folder
    """
    folder.manage("test_folder", "create", "Datacenter", "vm")
    ret = folder.manage("test_folder", "destroy", "Datacenter", "vm")
    assert ret["result"] == True
    assert ret["comment"] == "destroyed"
    assert ret["changes"]["new"] == "folder test_folder destroyed"


def test_rename_folder_test(patch_salt_globals_folder_state_test, test_folder_name_c):
    """
    test rename folder in test mode
    """
    ret = folder.rename(test_folder_name_c, "test_folder_state_new", "Datacenter", "vm")
    assert ret["result"] == True
    assert ret["comment"] == "These options are set to change."
    assert ret["changes"]["new"] == "folder test_folder will be renamed test_folder_state_new"


def test_rename_folder(patch_salt_globals_folder_state, test_folder_name_rename):
    """
    test rename folder
    """
    old_folder, new_folder = test_folder_name_rename
    ret = folder.rename(old_folder, new_folder, "Datacenter", "vm")
    assert ret["result"] == True
    assert ret["comment"] == "renamed"
    assert ret["changes"]["new"] == "folder test_folder renamed test_folder_new"


def test_move_folder_test(patch_salt_globals_folder_state_test, test_folder_name_move):
    """
    test move folder in test mode
    """
    inside_folder, outside_folder = test_folder_name_move
    ret = folder.move(inside_folder, outside_folder, "Datacenter", "vm")
    assert ret["result"] == True
    assert ret["comment"] == "These options are set to change."
    assert ret["changes"]["new"] == "folder test_folder will be moved to test_folder_top"


def test_move_folder(patch_salt_globals_folder_state, test_folder_name_move):
    """
    test move folder
    """
    inside_folder, outside_folder = test_folder_name_move
    ret = folder.move(inside_folder, outside_folder, "Datacenter", "vm")
    assert ret["result"] == True
    assert ret["comment"] == "moved"
    assert ret["changes"]["new"] == "folder test_folder moved to test_folder_top"
