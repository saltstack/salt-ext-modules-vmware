"""
    :codeauthor: VMware
"""
import logging
from unittest.mock import patch

import pytest
import salt.exceptions
import saltext.vmware.modules.controller_metadata as controller_metadata

log = logging.getLogger(__name__)


@pytest.fixture
def tgz_file(session_temp_dir):
    tgz = session_temp_dir / "vmware.tgz"
    tgz.write_bytes(b"1")
    yield tgz


@pytest.fixture
def configure_loader_modules():
    return {controller_metadata: {"__opts__": {}, "__pillar__": {}}}


@pytest.fixture(autouse=True)
def patch_salt_loaded_objects():
    # This needs to be the same as the module we're importing
    with patch(
        "saltext.vmware.modules.controller_metadata.__opts__",
        {
            "cachedir": ".",
            "saltext.vmware": {"host": "test.vcenter.local", "user": "test", "password": "test"},
        },
        create=True,
    ), patch.object(controller_metadata, "__pillar__", {}, create=True), patch.object(
        controller_metadata, "__salt__", {}, create=True
    ):
        yield


@pytest.mark.parametrize(
    "exception",
    [False, True],
)
def test_validate(exception):
    patch_validate_exception = patch(
        "config_modules_vmware.interfaces.metadata_interface.ControllerMetadataInterface.validate_custom_metadata",
        autospec=True,
        side_effect=Exception("Testing"),
    )
    mock_controller_metadata = {
        "vcenter": {
            "backup_schedule_config": {
                "metadata": {
                    "global_key": "global_value",
                    "configuration_id": "1112",
                    "instance_metadata_1": True,
                    "metadata_2": {"nested_key_1": "nested_key_1_value"},
                }
            }
        }
    }
    if exception:
        with patch_validate_exception:
            with pytest.raises(salt.exceptions.VMwareRuntimeError):
                controller_metadata.validate(mock_controller_metadata)
    else:
        controller_metadata.validate(mock_controller_metadata)
