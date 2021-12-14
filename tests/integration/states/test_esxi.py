# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import uuid
from unittest.mock import MagicMock

import pytest
import salt
import saltext.vmware.modules.esxi as esxi_mod
import saltext.vmware.states.esxi as esxi


@pytest.fixture
def dry_run():
    setattr(esxi, "__opts__", {"test": True})
    yield
    setattr(esxi, "__opts__", {"test": False})


@pytest.fixture
def user_add_error():
    esxi.__salt__["vmware_esxi.add_user"] = MagicMock(
        side_effect=salt.exceptions.SaltException("add error")
    )


@pytest.fixture
def user_update_error():
    esxi.__salt__["vmware_esxi.update_user"] = MagicMock(
        side_effect=salt.exceptions.SaltException("update error")
    )


@pytest.fixture
def user_remove_error():
    esxi.__salt__["vmware_esxi.remove_user"] = MagicMock(
        side_effect=salt.exceptions.SaltException("remove error")
    )


def test_user_present_absent(patch_salt_globals):
    """
    Test scenarios for user_present state run
    """
    user_name = "A{}".format(uuid.uuid4())
    random_user = "Random{}".format(uuid.uuid4())
    password = "Secret@123"

    # create a new user
    ret = esxi.user_present(name=user_name, password=password)
    assert ret["result"]
    for host in ret["changes"]:
        assert ret["changes"][host]["new"]["name"] == user_name

    # update the user
    ret = esxi.user_present(name=user_name, password=password, description="new desc")
    assert ret["result"]
    for host in ret["changes"]:
        assert ret["changes"][host]["new"]["name"] == user_name
        assert ret["changes"][host]["new"]["description"] == "new desc"

    # Remove the user
    ret = esxi.user_absent(name=user_name)
    assert ret["result"]
    for host in ret["changes"]:
        assert ret["changes"][host][user_name] is True

    # Remove a non-existent user
    ret = esxi.user_absent(name=random_user)
    assert ret["result"] is None
    assert not ret["changes"]


def test_user_add_error(patch_salt_globals, user_add_error):
    """
    Test scenarios for user add error
    """
    user_name = "A{}".format(uuid.uuid4())
    password = "Secret@123"
    ret = esxi.user_present(name=user_name, password=password)
    assert ret["result"] is False
    assert not ret["changes"]
    assert "add error" in ret["comment"]


def test_user_remove_error(patch_salt_globals, user_remove_error):
    """
    Test scenarios for user remove error
    """
    # Remove the user
    user_name = "A{}".format(uuid.uuid4())
    password = "Secret@123"
    ret = esxi.user_present(name=user_name, password=password)
    assert ret["result"] is True
    ret = esxi.user_absent(name=user_name)
    assert ret["result"] is False
    assert not ret["changes"]
    assert "remove error" in ret["comment"]


def test_user_update_error(patch_salt_globals, user_update_error):
    """
    Test scenarios for user remove error
    """
    # Remove the user
    user_name = "A{}".format(uuid.uuid4())
    password = "Secret@123"
    ret = esxi.user_present(name=user_name, password=password)
    assert ret["result"] is True
    ret = esxi.user_present(name=user_name, password=password)
    assert ret["result"] is False
    assert not ret["changes"]
    assert "update error" in ret["comment"]


def test_user_present_absent_dry_run(vmware_datacenter, service_instance, dry_run):
    """
    Test scenarios for vmware_esxi.user_present state run with test=True
    """

    user_name = "A{}".format(uuid.uuid4())
    random_user = "Random{}".format(uuid.uuid4())
    password = "Secret@123"

    # create a new user
    ret = esxi.user_present(name=user_name, password=password)
    assert ret["result"] is None
    assert not ret["changes"]
    assert ret["comment"].split()[6]

    # update the user
    ret = esxi.user_present(name=user_name, password=password, description="new desc")
    assert ret["result"] is None
    assert not ret["changes"]
    assert ret["comment"].split()[11]

    # Remove the user
    ret = esxi_mod.add_user(
        user_name=user_name, password=password, service_instance=service_instance
    )
    ret = esxi.user_absent(name=user_name)
    assert ret["result"] is None
    assert not ret["changes"]
    assert "will be deleted" in ret["comment"]

    # Remove a non-existent user
    ret = esxi.user_absent(name=random_user)
    assert ret["result"] is None
    assert not ret["changes"]
    assert "will be deleted on 0 host" in ret["comment"]
