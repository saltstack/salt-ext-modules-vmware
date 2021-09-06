"""
    :codeauthor: VMware
"""
import logging
from unittest.mock import MagicMock

import pytest
import saltext.vmware.modules.esxi as esxi
import saltext.vmware.utils.connect

log = logging.getLogger(__name__)


def get_host():
    HOST = MagicMock()
    HOST.RebootHost_Task.return_value = MagicMock()
    HOST.PowerDownHostToStandBy_Task.return_value = MagicMock()
    HOST.PowerUpHostFromStandBy_Task.return_value = MagicMock()
    HOST.ShutdownHost_Task.return_value = MagicMock()
    return HOST


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
