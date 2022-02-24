# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import pytest
import saltext.vmware.modules.folder as folder


@pytest.fixture
def test_folder_name():
    yield 'test_folder'
    try:
        folder.destroy("test_folder", "Datacenter", "vm")
    except Exception:
        pass


@pytest.fixture
def rename_test_folder_names():
    try:
        folder.create("test_folder", "Datacenter", "vm")
        yield ['test_folder', "new_test_folder"]
    finally:
        folder.destroy("new_test_folder", "Datacenter", "vm")


@pytest.fixture
def move_test_folder_names():
    try:
        folder.create("test_folder_top", "Datacenter", "vm")
        folder.create("test_folder", "Datacenter", "vm")
        yield ['test_folder_top', "test_folder"]
    finally:
        folder.destroy("test_folder_top", "Datacenter", "vm")


def test_create(patch_salt_globals_folder, test_folder_name):
    """
    Test folder create
    """
    ret = folder.create(test_folder_name, "Datacenter", "vm")
    assert ret["status"] == "created"


def test_rename(patch_salt_globals_folder, rename_test_folder_names):
    """
    Test folder rename
    """
    ret = folder.rename(rename_test_folder_names[0], rename_test_folder_names[1], "Datacenter", "vm")
    assert ret["status"] == "renamed"


def test_move(patch_salt_globals_folder, move_test_folder_names):
    """
    Test folder move
    """
    ret = folder.move(move_test_folder_names[1], move_test_folder_names[0], "Datacenter", "vm")
    assert ret["status"] == "moved"


def test_destoryed(patch_salt_globals_folder):
    """
    Test folder destoryed
    """
    folder.create("test_folder", "Datacenter", "vm")
    ret = folder.destroy("test_folder", "Datacenter", "vm")
    assert ret["status"] == "destroyed"
