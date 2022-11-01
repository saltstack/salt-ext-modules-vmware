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


@pytest.fixture
def configure_loader_modules():
    return {esxi: {"__opts__": {}, "__pillar__": {}}}


@pytest.fixture(autouse=True)
def patch_salt_loaded_objects():
    # This esxi needs to be the same as the module we're importing
    with patch(
        "saltext.vmware.modules.esxi.__opts__",
        {
            "cachedir": ".",
            "saltext.vmware": {"host": "fnord.example.com", "user": "fnord", "password": "fnord"},
        },
        create=True,
    ), patch.object(esxi, "__pillar__", {}, create=True), patch.object(
        esxi, "__salt__", {}, create=True
    ):
        yield


@pytest.fixture
def fake_hosts():
    hosts = [MagicMock()]
    hosts[0].name = "blerp"
    hosts[
        0
    ].configManager.firmwareSystem.QueryFirmwareConfigUploadURL.return_value = "something/cool/*"

    with patch("saltext.vmware.utils.esxi.get_hosts", autospec=True, return_value=hosts):
        yield hosts


@pytest.fixture
def fake_http_query():
    fake_query = MagicMock()
    with patch.dict(esxi.__salt__, {"http.query": fake_query}):
        yield fake_query


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
def test_esxi_power_state(hosts, state, fn, fn_calls, expected, fake_service_instance):
    _, service_instance = fake_service_instance

    patch_get_hosts = patch(
        "saltext.vmware.utils.esxi.get_hosts", autospec=True, return_value=hosts
    )
    patch_wait_for_task = patch(
        "saltext.vmware.utils.common.wait_for_task", autospec=True, return_value=None
    )

    with patch_get_hosts, patch_wait_for_task:
        ret = esxi.power_state(state=state, service_instance=service_instance)

    cnt = 0
    for h in hosts:
        mock_func = getattr(h, fn)
        cnt += mock_func.call_count
        # the get_host() fixtures are shared between other test runs
        mock_func.reset_mock()
    assert cnt == fn_calls
    assert ret is expected


@pytest.mark.parametrize(
    ["hosts", "push_file_to_master"],
    [
        [[get_host(), get_host()], False],
        [[get_host(), get_host()], True],
    ],
)
def test_esxi_backup_config(hosts, push_file_to_master, session_temp_dir, fake_service_instance):
    _, service_instance = fake_service_instance
    patch_get_hosts = patch(
        "saltext.vmware.utils.esxi.get_hosts", autospec=True, return_value=hosts
    )
    patch_wait_for_task = patch(
        "saltext.vmware.utils.common.wait_for_task", autospec=True, return_value=None
    )
    fake_http_query = MagicMock(return_value={"body": b"1"})
    patch_salt = patch.dict(
        esxi.__salt__,
        {
            "http.query": fake_http_query,
            "cp.push": MagicMock(return_value=True),
            "cp.cache_file": MagicMock(return_value=str(tgz_file)),
        },
        update=True,
    )
    patch_opts = patch.dict(esxi.__opts__, {"cachedir": str(session_temp_dir)})
    with patch_get_hosts, patch_wait_for_task, patch_salt, patch_opts:
        ret = esxi.backup_config(
            push_file_to_master=push_file_to_master, service_instance=service_instance
        )
        assert ret
        for host in hosts:
            assert ret[host.name]["file_name"] == str(session_temp_dir / "vmware.tgz")
            assert ret[host.name]["url"] == "http://vmware.tgz"
        assert push_file_to_master == (esxi.__salt__["cp.push"].call_count > 0)


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
    esxi.__opts__["saltext.vmware"]["esxi_host"] = esxi.__opts__["saltext.vmware"].get(
        "esxi_host", {}
    )
    for host in hosts:
        esxi.__opts__["saltext.vmware"]["esxi_host"][host.name] = {
            "user": esxi.__opts__["saltext.vmware"]["user"],
            "password": esxi.__opts__["saltext.vmware"]["password"],
        }
    fake_http_query = MagicMock(return_value={"body": b"1"})
    patch_salt = patch.dict(
        esxi.__salt__,
        {
            "http.query": fake_http_query,
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
    "expected_kwargs, host_name",
    [
        ({"host_names": None, "get_all_hosts": True}, None),
        ({"host_names": ["roscivs.example.com"], "get_all_hosts": False}, "roscivs.example.com"),
    ],
)
def test_esxi_restore_config_should_request_correct_hosts(expected_kwargs, host_name):
    # host_names should be a list or None, and get_all_hosts should be True or
    # False depending on if a host_name was provided
    fake_si = MagicMock()
    with patch(
        "saltext.vmware.utils.esxi.get_hosts", autospec=True, return_value=[]
    ) as fake_get_hosts:
        esxi.restore_config(host_name=host_name, source_file=None, service_instance=fake_si)
    fake_get_hosts.assert_called_with(
        service_instance=fake_si,
        cluster_name=None,
        datacenter_name=None,
        **expected_kwargs,
    )


def test_esxi_restore_config_should_send_correct_data_to_config_api_endpoint(
    fake_hosts, session_temp_dir, fake_http_query
):
    expected_url = "something/cool/blerp"
    expected_username = "roscivs"
    expected_password = "bottia"
    expected_data = b"hello world!"
    opts = {
        "saltext.vmware": {
            "user": "wrong username",
            "password": "wrong password",
            "esxi_host": {
                fake_hosts[0].name: {"user": expected_username, "password": expected_password},
            },
        },
    }
    sfile = session_temp_dir / "fnord"
    sfile.write_bytes(expected_data)
    with patch.dict(esxi.__opts__, opts):
        esxi.restore_config(source_file=str(sfile), service_instance=MagicMock())
    fake_http_query.assert_called_with(
        expected_url,
        data=expected_data,
        method="PUT",
        username=expected_username,
        password=expected_password,
    )


@pytest.mark.parametrize(
    ["hosts"],
    [
        [[get_host(), get_host()]],
    ],
)
def test_esxi_reset_config(hosts, fake_service_instance):
    _, service_instance = fake_service_instance
    patch_get_hosts = patch(
        "saltext.vmware.utils.esxi.get_hosts", autospec=True, return_value=hosts
    )
    patch_wait_for_task = patch(
        "saltext.vmware.utils.common.wait_for_task", autospec=True, return_value=None
    )
    patch_opts = patch.dict(esxi.__opts__, {"cachedir": "."})
    fake_http_query = MagicMock(return_value={"body": b"1"})
    patch_salt = patch.dict(
        esxi.__salt__,
        {
            "http.query": fake_http_query,
            "cp.cache_file": MagicMock(return_value="vmware.tgz"),
        },
        update=True,
    )
    with patch_get_hosts, patch_wait_for_task, patch_salt, patch_opts:
        ret = esxi.reset_config(service_instance=service_instance)
        assert ret
        for host in hosts:
            assert ret[host.name]
