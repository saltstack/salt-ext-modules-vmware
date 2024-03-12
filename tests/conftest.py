# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
import tempfile

import pytest
from saltext.vmware import PACKAGE_ROOT
from saltfactories.utils import random_string


@pytest.fixture(scope="session")
def session_temp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield pathlib.Path(d).resolve()


@pytest.fixture(scope="session")
def salt_factories_config():
    """
    Return a dictionary with the keyworkd arguments for FactoriesManager
    """
    return {
        "code_dir": str(PACKAGE_ROOT),
        "inject_coverage": "COVERAGE_PROCESS_START" in os.environ,
        "inject_sitecustomize": "COVERAGE_PROCESS_START" in os.environ,
        "start_timeout": 120 if os.environ.get("CI") else 60,
    }


@pytest.fixture(scope="session")
def master(salt_factories):
    return salt_factories.salt_master_daemon(
        random_string("master-"), defaults={"enable_fqdns_grains": False}
    )


@pytest.fixture(scope="session")
def minion(master):
    return master.salt_minion_daemon(
        random_string("minion-"), defaults={"enable_fqdns_grains": False}
    )
