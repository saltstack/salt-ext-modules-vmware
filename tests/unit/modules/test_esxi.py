"""
    :codeauthor: VMware
"""
import logging
import os
import uuid
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import saltext.vmware.modules.esxi as esxi
import saltext.vmware.utils.connect

log = logging.getLogger(__name__)


@pytest.fixture
def tgz_file(session_temp_dir):
    tgz = session_temp_dir / "vmware.tgz"
    tgz.write_bytes(b"1")
    yield tgz


@pytest.fixture(autouse=True)
def patch_salt_loaded_objects():
    # This esxi needs to be the same as the module we're importing
    with patch.object(esxi, "__opts__", {"cachedir": "."}, create=True), patch.object(
        esxi, "__pillar__", {}, create=True
    ), patch.object(esxi, "__salt__", {}, create=True):
        yield


def get_host(in_maintenance_mode=None):
    host = MagicMock()
    host.name = uuid.uuid4().hex
    host.RebootHost_Task.return_value = MagicMock()
    host.PowerDownHostToStandBy_Task.return_value = MagicMock()
    host.PowerUpHostFromStandBy_Task.return_value = MagicMock()
    host.ShutdownHost_Task.return_value = MagicMock()
    host.ShutdownHost_Task.return_value = MagicMock()
    host.configManager.firmwareSystem.BackupFirmwareConfiguration = MagicMock(
        return_value="http://vmware.tgz"
    )
    host.configManager.firmwareSystem.QueryFirmwareConfigUploadURL = MagicMock(
        return_value="http://vmware.tgz"
    )
    host.runtime.inMaintenanceMode = in_maintenance_mode
    host.EnterMaintenanceMode_Task.return_value = MagicMock()
    host.configManager.firmwareSystem.RestoreFirmwareConfiguration.return_value = MagicMock()
    host.configManager.firmwareSystem.ResetFirmwareToFactoryDefaults.return_value = MagicMock()
    host.ExitMaintenanceMode_Task.return_value = MagicMock()
    return host


@pytest.mark.parametrize(
    ["hosts", "fn_calls", "expected"],
    [
        [[], 0, None],
        [[get_host()], 1, True],
        [[get_host(), get_host()], 2, True],
    ],
)
@pytest.mark.parametrize(
    ["state", "fn"],
    [
        ["reboot", "RebootHost_Task"],
        ["standby", "PowerDownHostToStandBy_Task"],
        ["poweron", "PowerUpHostFromStandBy_Task"],
        ["shutdown", "ShutdownHost_Task"],
    ],
)
def test_esxi_power_state(monkeypatch, hosts, state, fn, fn_calls, expected):
    setattr(saltext.vmware.modules.esxi, "__opts__", MagicMock())
    setattr(saltext.vmware.modules.esxi, "__pillar__", MagicMock())
    monkeypatch.setattr(saltext.vmware.modules.esxi, "get_service_instance", MagicMock())
    monkeypatch.setattr(saltext.vmware.utils.esxi, "get_hosts", MagicMock(return_value=hosts))
    monkeypatch.setattr(saltext.vmware.utils.common, "wait_for_task", MagicMock())
    ret = esxi.power_state(state=state)
    cnt = 0
    for h in hosts:
        cnt += getattr(h, fn).call_count
    assert cnt == fn_calls
    assert ret is expected


@pytest.mark.parametrize(
    ["hosts", "push_file_to_master"],
    [
        [[get_host(), get_host()], False],
        [[get_host(), get_host()], True],
    ],
)
def test_esxi_backup_config(monkeypatch, hosts, push_file_to_master):
    setattr(saltext.vmware.modules.esxi, "__opts__", {"cachedir": "."})
    setattr(saltext.vmware.modules.esxi, "__pillar__", MagicMock())
    setattr(
        saltext.vmware.modules.esxi,
        "__salt__",
        {
            "http.query": MagicMock(return_value={"body": b"1"}),
            "cp.push": MagicMock(return_value=True),
        },
    )
    monkeypatch.setattr(saltext.vmware.modules.esxi, "get_service_instance", MagicMock())
    monkeypatch.setattr(saltext.vmware.utils.esxi, "get_hosts", MagicMock(return_value=hosts))
    monkeypatch.setattr(saltext.vmware.utils.common, "wait_for_task", MagicMock())
    ret = esxi.backup_config(push_file_to_master=push_file_to_master)
    assert ret
    for host in hosts:
        assert ret[host.name]["file_name"] == os.path.join(".", "vmware.tgz")
        assert ret[host.name]["url"] == "http://vmware.tgz"
    assert push_file_to_master == (saltext.vmware.modules.esxi.__salt__["cp.push"].call_count > 0)


@pytest.mark.parametrize(
    ["hosts", "source_file"],
    [
        [[get_host(), get_host()], None],
        [[get_host(), get_host()], "http://vmware.tgz"],
        [[get_host(), get_host()], "salt://vmware.tgz"],
    ],
)
def test_esxi_restore_config(hosts, source_file, tgz_file):
    if source_file is None:
        source_file = str(tgz_file)
    patch_salt = patch.dict(
        esxi.__salt__,
        {
            "http.query": MagicMock(return_value={"body": b"1"}),
            "cp.cache_file": MagicMock(return_value=str(tgz_file)),
        },
        update=True,
    )
    patch_get_hosts = patch(
        "saltext.vmware.utils.esxi.get_hosts", autospec=True, return_value=hosts
    )
    patch_wait_for_task = patch("saltext.vmware.utils.common.wait_for_task", autospec=True)
    with patch_get_hosts, patch_wait_for_task, patch_salt:
        ret = esxi.restore_config(source_file=source_file, service_instance=MagicMock())
    assert ret
    for host in hosts:
        assert ret[host.name] is True


@pytest.mark.parametrize(
    ["hosts"],
    [
        [[get_host(), get_host()]],
    ],
)
def test_esxi_reset_config(monkeypatch, hosts):
    setattr(saltext.vmware.modules.esxi, "__opts__", {"cachedir": "."})
    setattr(saltext.vmware.modules.esxi, "__pillar__", MagicMock())
    setattr(
        saltext.vmware.modules.esxi,
        "__salt__",
        {
            "http.query": MagicMock(return_value={"body": b"1"}),
            "cp.cache_file": MagicMock(return_value="vmware.tgz"),
        },
    )
    monkeypatch.setattr(saltext.vmware.modules.esxi, "get_service_instance", MagicMock())
    monkeypatch.setattr(saltext.vmware.utils.esxi, "get_hosts", MagicMock(return_value=hosts))
    monkeypatch.setattr(saltext.vmware.utils.common, "wait_for_task", MagicMock())
    ret = esxi.reset_config()
    assert ret
    for host in hosts:
        assert ret[host.name]
