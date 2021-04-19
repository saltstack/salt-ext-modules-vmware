import json
import os
import ssl
from pathlib import Path

import pytest
from pyVim import connect


@pytest.fixture(scope="package")
def master(master):
    with master.started():
        yield master


@pytest.fixture(scope="package")
def minion(minion):
    with minion.started():
        yield minion


@pytest.fixture
def salt_run_cli(master):
    return master.get_salt_run_cli()


@pytest.fixture
def salt_cli(master):
    return master.get_salt_cli()


@pytest.fixture
def salt_call_cli(minion):
    return minion.get_salt_call_cli()


@pytest.fixture(scope="session")
def integration_test_config():
    default_path = Path().parent.parent / "local" / "vcenter.conf"
    config_path = os.environ.get("VCENTER_CONFIG", default_path)
    try:
        with config_path.open() as f:
            return json.load(f)
    except Exception as e:  # pylint: disable=broad-except
        pytest.skip(f"Unable to load config from {config_path} - {e}")


@pytest.fixture(scope="session")
def service_instance(integration_test_config):
    config = integration_test_config
    if config.get("skip_ssl_verify", True):
        ctx = ssl._create_unverified_context()
    else:
        ctx = ssl.create_default_context()
    si = connect.SmartConnect(  # pylint: disable=invalid-name
        host=config["host"], user=config["user"], pwd=config["password"], sslContext=ctx
    )
    return si
