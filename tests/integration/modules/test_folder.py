# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import tarfile

import pytest
import salt.exceptions
import saltext.vmware.modules.folder as folder


def test_create(patch_salt_globals_folder):
    """
    Test folder create
    """
    ret = folder.create("test_folder", "Datacenter", "vm")
    assert ret["status"] == "created"


def test_rename(patch_salt_globals_folder):
    """
    Test folder rename
    """
    ret = folder.rename("test_folder", "new_test_folder", "Datacenter", "vm")
    assert ret["status"] == "renamed"


def test_move(patch_salt_globals_folder):
    """
    Test folder move
    """
    ret = folder.create("test_folder", "Datacenter", "vm")
    ret = folder.move("test_folder", "new_test_folder", "Datacenter", "vm")
    assert ret["status"] == "moved"


def test_destoryed(patch_salt_globals_folder):
    """
    Test folder destoryed
    """
    ret = folder.destroy("new_test_folder", "Datacenter", "vm")
    assert ret["status"] == "destroyed"
