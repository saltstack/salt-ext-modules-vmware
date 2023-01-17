import json
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import saltext.vmware.modules.esxi as esxi_module
import saltext.vmware.states.esxi as esxi
from pyVmomi import vim


def mock_with_name(name, *args, **kwargs):
    # Can't mock name via constructor: https://docs.python.org/3/library/unittest.mock.html#mock-names-and-the-name-attribute
    mock = Mock(*args, **kwargs)
    mock.name = name
    return mock


sshClientMockObject = mock_with_name(
    name="sshClient",
    service="sshClient",
    spec=vim.host.Ruleset,
    dynamicProperty=[],
    key="sshClient",
    label="SSH Client",
    required=False,
    rule=[
        Mock(
            spec=vim.host.Ruleset.Rule,
            dynamicProperty=[],
            port=22,
            endPort=24,
            direction="outbound",
            portType="dst",
            protocol="tcp",
        )
    ],
    enabled=True,
    allowedHosts=Mock(
        spec=vim.host.Ruleset.IpList,
        dynamicProperty=[],
        ipAddress=["3.3.3.3"],
        ipNetwork=[
            Mock(
                spec=vim.host.Ruleset.IpNetwork,
                dynamicProperty=[],
                network="1.1.1.1",
                prefixLength=24,
            ),
            Mock(
                spec=vim.host.Ruleset.IpNetwork,
                dynamicProperty=[],
                network="2.2.2.2",
                prefixLength=24,
            ),
        ],
        allIp=False,
    ),
)

sshServerMockObject = mock_with_name(
    name="sshServer",
    service="sshServer",
    spec=vim.host.Ruleset,
    dynamicProperty=[],
    key="sshServer",
    label="SSH Server",
    required=True,
    rule=[
        Mock(
            spec=vim.host.Ruleset.Rule,
            dynamicProperty=[],
            port=22,
            endPort=24,
            direction="inbound",
            portType="dst",
            protocol="tcp",
        )
    ],
    enabled=True,
    allowedHosts=Mock(
        spec=vim.host.Ruleset.IpList,
        dynamicProperty=[],
        ipAddress=["192.168.110.90"],
        ipNetwork=[],
        allIp=False,
    ),
)


def mock_firewall_rules_object(name):
    if name == "sshServer":
        return sshServerMockObject
    elif name == "sshClient":
        return sshClientMockObject
    else:
        return None


@pytest.fixture
def configure_loader_modules():
    return {esxi: {}}


@pytest.fixture(
    params=(
        [
            {
                "test_name": "Test case 1",
                "rules": [
                    {
                        "name": "sshServer",
                        "enabled": True,
                        "allowed_host": {
                            "all_ip": False,
                            "ip_address": ["192.168.110.90"],
                            "ip_network": [],
                        },
                    },
                    {
                        "name": "sshClient",
                        "enabled": True,
                        "allowed_host": {
                            "all_ip": False,
                            "ip_address": ["3.3.3.3"],
                            "ip_network": ["1.1.1.1/24", "2.2.2.2/24"],
                        },
                    },
                ],
                "updates": [
                    {
                        "name": "sshServer",
                        "enabled": True,
                        "allowed_host": {
                            "all_ip": False,
                            "ip_address": ["192.168.0.253", "192.168.10.1"],
                            "ip_network": ["192.168.0.0/24"],
                        },
                    },
                    {"name": "sshClient", "enabled": True},
                ],
                "expected_changes": {
                    "name": "Test case 1",
                    "changes": {
                        "esxi-01a.corp.local": {
                            "old": {
                                "sshServer": {
                                    "allowed_host": {
                                        "ip_address": ["192.168.110.90"],
                                        "ip_network": [],
                                    }
                                },
                                "sshClient": {
                                    "allowed_host": {
                                        "ip_address": ["3.3.3.3"],
                                        "all_ip": False,
                                        "ip_network": ["1.1.1.1/24", "2.2.2.2/24"],
                                    }
                                },
                            },
                            "new": {
                                "sshServer": {
                                    "allowed_host": {
                                        "ip_address": ["192.168.0.253", "192.168.10.1"],
                                        "ip_network": ["192.168.0.0/24"],
                                    }
                                },
                                "sshClient": {
                                    "allowed_host": {
                                        "ip_address": [],
                                        "all_ip": True,
                                        "ip_network": [],
                                    }
                                },
                            },
                        },
                    },
                    "result": None,
                    "comment": "",
                },
                "vmomi_content": [
                    mock_firewall_rules_object("sshServer"),
                    mock_firewall_rules_object("sshClient"),
                ],
            }
        ]
    )
)
def mocked_firewall_rules_data(request, fake_service_instance):
    service_instance, _ = fake_service_instance

    vmomi_content = request.param["vmomi_content"]

    hosts = [MagicMock()]
    hosts[0].name = "esxi-01a.corp.local"
    hosts[0].configManager.firewallSystem.firewallInfo.ruleset = vmomi_content

    with patch("saltext.vmware.utils.esxi.get_hosts", autospec=True, return_value=hosts):
        service_instance.return_value.configManager.firewallSystem.firewallInfo.ruleset = (
            vmomi_content
        )
        service_instance.return_value.viewManager.CreateContainerView.return_value = hosts

        yield request.param["test_name"], request.param["rules"], request.param[
            "updates"
        ], json.loads(json.dumps(request.param["expected_changes"]))


@pytest.mark.parametrize("test_run", [True, False])
def test_drift_report_firewall_rules(mocked_firewall_rules_data, fake_service_instance, test_run):
    service_instance, _ = fake_service_instance
    config_name, rules, update, expected_change = mocked_firewall_rules_data

    if not test_run:
        if config_name == "Test case 1":
            expected_change["result"] = True
            expected_change["comment"] = {
                "esxi-01a.corp.local sshServer": {
                    "status": "SUCCESS",
                    "message": f"Rule 'sshServer' has been changed successfully for host esxi-01a.corp.local.",
                },
                "esxi-01a.corp.local sshClient": {
                    "status": "SUCCESS",
                    "message": f"Rule 'sshClient' has been changed successfully for host esxi-01a.corp.local.",
                },
            }

    with patch.dict(esxi.__opts__, {"test": test_run}):
        ret = esxi.firewall_configs(
            name=config_name,
            configs=update,
            service_instance=service_instance,
            profile="vcenter",
        )
        assert ret == expected_change
