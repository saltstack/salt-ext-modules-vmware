# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import uuid

import pytest
import saltext.vmware.modules.esxi as esxi_mod
import saltext.vmware.states.esxi as esxi


@pytest.fixture
def dry_run():
    setattr(esxi, "__opts__", {"test": True})
    yield
    setattr(esxi, "__opts__", {"test": False})


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
    print(ret)
    assert ret["result"] is None
    assert not ret["changes"]
    assert "will be deleted on 0 host" in ret["comment"]
