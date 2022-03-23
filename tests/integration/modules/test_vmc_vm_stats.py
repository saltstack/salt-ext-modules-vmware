"""
    Integration Tests for vmc_vm_stats execution module
"""
import pytest


@pytest.fixture
def vm_id(salt_call_cli, vmc_vcenter_connect):
    ret = salt_call_cli.run("vmc_sddc.get_vms", **vmc_vcenter_connect)
    vm_obj = ret.json[0]
    return vm_obj["vm"]


def test_get_cpu_stats_for_vm_smoke_test(salt_call_cli, vmc_vcenter_connect, vm_id):
    ret = salt_call_cli.run(
        "vmc_vm_stats.get", vm_id=vm_id, stats_type="cpu", **vmc_vcenter_connect
    )
    assert ret is not None
    assert "error" not in ret.json


def test_get_memory_stats_for_vm_smoke_test(salt_call_cli, vmc_vcenter_connect, vm_id):
    ret = salt_call_cli.run(
        "vmc_vm_stats.get", vm_id=vm_id, stats_type="memory", **vmc_vcenter_connect
    )
    assert ret is not None
    assert "error" not in ret.json


def test_get_memory_stats_when_vm_does_not_exist(salt_call_cli, vmc_vcenter_connect):
    ret = salt_call_cli.run(
        "vmc_vm_stats.get", vm_id="vm-abc", stats_type="memory", **vmc_vcenter_connect
    )
    assert ret is not None
    result = ret.json
    assert "error" in result
    assert result["error"]["error_type"] == "NOT_FOUND"
