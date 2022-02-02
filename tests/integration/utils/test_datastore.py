# Copyright 2022 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import saltext.vmware.utils.datastore as utils_datastore
from pyVmomi import vim


def _validate_datastores(datastores, max_datastores=None):
    assert len(datastores) > 0
    if max_datastores:
        assert len(datastores) <= max_datastores
    for datastore in datastores:
        assert isinstance(datastore, vim.Datastore)


def test_get_datastores(service_instance, integration_test_config):
    host = integration_test_config["esxi_host_name"]

    all_datastores = utils_datastore.get_datastores(service_instance)
    _validate_datastores(all_datastores)
    datastore_name = all_datastores[0].name

    one_datastore = utils_datastore.get_datastores(service_instance, datastore_name=datastore_name)
    _validate_datastores(one_datastore, max_datastores=len(all_datastores))

    host_datastores = utils_datastore.get_datastores(
        service_instance, host_name=host, datastore_name=datastore_name
    )
    _validate_datastores(host_datastores, max_datastores=len(all_datastores))
