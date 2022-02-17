# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pytest
import saltext.vmware.states.folder as folder


def test_create_folder_test(patch_salt_globals_folder_state_test):
    """
    test create folder in test mode
    """
    ret = folder.manage("test_folder_state", "create", "Datacenter", "vm")
    assert ret["result"] == True
    assert ret["comment"] == "These options are set to change."
    assert ret["changes"]["new"] == "folder test_folder_state will be created"


def test_create_folder(patch_salt_globals_folder_state):
    """
    test create folder
    """
    ret = folder.manage("test_folder_state", "create", "Datacenter", "vm")
    assert ret["result"] == True
    assert ret["comment"] == "created"
    assert ret["changes"]["new"] == "folder test_folder_state created"


def test_destroy_folder_test(patch_salt_globals_folder_state_test):
    """
    test destroy folder in test mode
    """
    ret = folder.manage("test_folder_state", "destroy", "Datacenter", "vm")
    assert ret["result"] == True
    assert ret["comment"] == "These options are set to change."
    assert ret["changes"]["new"] == "folder test_folder_state will be destroyed"


def test_destroy_folder(patch_salt_globals_folder_state):
    """
    test destroy folder
    """
    ret = folder.manage("test_folder_state", "destroy", "Datacenter", "vm")
    assert ret["result"] == True
    assert ret["comment"] == "destroyed"
    assert ret["changes"]["new"] == "folder test_folder_state destroyed"


def test_rename_folder_test(patch_salt_globals_folder_state_test):
    """
    test rename folder in test mode
    """
    ret = folder.rename("test_folder_state_rename", "test_folder_state_new", "Datacenter", "vm")
    assert ret["result"] == True
    assert ret["comment"] == "These options are set to change."
    assert (
        ret["changes"]["new"]
        == "folder test_folder_state_rename will be renamed test_folder_state_new"
    )


def test_rename_folder(patch_salt_globals_folder_state):
    """
    test rename folder
    """
    folder.manage("test_folder_state_rename", "create", "Datacenter", "vm")
    ret = folder.rename("test_folder_state_rename", "test_folder_state_new", "Datacenter", "vm")
    assert ret["result"] == True
    assert ret["comment"] == "renamed"
    assert ret["changes"]["new"] == "folder test_folder_state_rename renamed test_folder_state_new"


def test_move_folder_test(patch_salt_globals_folder_state_test):
    """
    test move folder in test mode
    """
    ret = folder.move("test_folder_state_new", "top_folder", "Datacenter", "vm")
    assert ret["result"] == True
    assert ret["comment"] == "These options are set to change."
    assert ret["changes"]["new"] == "folder test_folder_state_new will be moved to top_folder"


def test_move_folder(patch_salt_globals_folder_state):
    """
    test move folder
    """
    folder.manage("top_folder", "create", "Datacenter", "vm")
    ret = folder.move("test_folder_state_new", "top_folder", "Datacenter", "vm")
    assert ret["result"] == True
    assert ret["comment"] == "moved"
    assert ret["changes"]["new"] == "folder test_folder_state_new moved to top_folder"
    folder.manage("top_folder", "destroy", "Datacenter", "vm")
