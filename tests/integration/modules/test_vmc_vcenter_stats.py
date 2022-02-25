"""
    Integration Tests for vmc_vcenter_stats execution module
"""


def test_list_monitored_items_smoke_test(salt_call_cli, vmc_vcenter_admin_connect):
    ret = salt_call_cli.run("vmc_vcenter_stats.list_monitored_items", **vmc_vcenter_admin_connect)
    assert ret is not None
    assert "error" not in ret.json


def test_query_monitored_items_smoke_test(salt_call_cli, vmc_vcenter_admin_connect):
    query_kwargs = {
        "start_time": "2022-02-20T22:13:05.651Z",
        "end_time": "2022-02-21T22:13:05.651Z",
        "interval": "HOURS2",
        "aggregate_function": "COUNT",
        "monitored_items": "cpu.util,mem.util".split(","),
    }
    ret = salt_call_cli.run(
        "vmc_vcenter_stats.query_monitored_items", **query_kwargs, **vmc_vcenter_admin_connect
    )
    assert ret is not None
    assert "error" not in ret.json
