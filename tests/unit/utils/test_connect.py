import os
import unittest.mock as mock

import pytest
import saltext.vmware.utils.connect as connect


@pytest.mark.parametrize(
    "environ_values",
    [
        # Nothing
        {},
        # Missing host
        {"SALTEXT_VMWARE_USER": "fnord", "SALTEXT_VMWARE_PASSWORD": "fnord"},
        # Missing user
        {"SALTEXT_VMWARE_HOST": "fnord", "SALTEXT_VMWARE_PASSWORD": "fnord"},
        # Missing password
        {"SALTEXT_VMWARE_HOST": "fnord", "SALTEXT_VMWARE_USER": "fnord"},
    ],
)
def test_when_no_config_and_environ_is_missing_conf_values_get_service_instance_should_raise_error(
    environ_values,
):
    with pytest.raises(
        ValueError,
        match="Cannot create service instance, VMware credentials incomplete.",
    ), mock.patch.dict(os.environ, environ_values):
        connect.get_service_instance()


@pytest.mark.parametrize(
    "config_values",
    [
        # Nothing
        {},
        # saltext.vmware is emtpy
        {"saltext.vmware": {}},
        # Missing host
        {"saltext.vmware": {"user": "fnord user", "password": "fnord password"}},
        # Missing user
        {"saltext.vmware": {"host": "fnord host", "password": "fnord password"}},
        # Missing password
        {"saltext.vmware": {"host": "fnord host", "user": "fnord user"}},
    ],
)
def test_when_no_environ_values_and_config_is_missing_conf_values_get_service_instance_should_raise_error(
    config_values,
):
    with pytest.raises(
        ValueError,
        match="Cannot create service instance, VMware credentials incomplete.",
    ), mock.patch.dict(os.environ, {}):
        connect.get_service_instance(config=config_values)


@pytest.mark.xfail
@pytest.mark.parametrize(
    "expected_values,esxi_host,profile,conf_values,environ_values",
    [
        # No environ config, simple config in config
        (
            {"host": "blerp", "user": "whatever", "pwd": "coolguy"},
            None,
            None,
            {"saltext.vmware": {"host": "blerp", "user": "whatever", "password": "coolguy"}},
            {},
        ),
        # No environ config, simple profile config
        (
            {"host": "profile host", "user": "profile user", "pwd": "profile password"},
            None,
            "fnordy_profile",
            {
                "saltext.vmware": {
                    "host": "blerp",
                    "user": "whatever",
                    "password": "coolguy",
                    "fnordy_profile": {
                        "host": "profile host",
                        "user": "profile user",
                        "password": "profile password",
                    },
                }
            },
            {},
        ),
        # No environ config, get esxi host values from config
        (
            {"host": "some esxi host", "user": "esxi user", "pwd": "esxi password"},
            "some esxi host",
            None,
            {
                "saltext.vmware": {
                    "host": "blerp",
                    "user": "whatever",
                    "password": "coolguy",
                    "esxi_host": {
                        "some esxi host": {
                            "user": "esxi user",
                            "password": "esxi password",
                        },
                    },
                }
            },
            {},
        ),
        # No environ config, get esxi host values from profile in config
        (
            {"host": "some esxi host", "user": "esxi user", "pwd": "esxi password"},
            "some esxi host",
            "some cool profile",
            {
                "saltext.vmware": {
                    "host": "blerp",
                    "user": "whatever",
                    "password": "coolguy",
                    "esxi_host": {
                        "some esxi host": {
                            "user": "bad user - not from profile",
                            "password": "bad password - not from profile",
                        },
                    },
                    "some cool profile": {
                        "esxi_host": {
                            "some esxi host": {
                                "user": "esxi user",
                                "password": "esxi password",
                            },
                        },
                    },
                },
            },
            {},
        ),
        # environ config with esxi host and profile should still get esxi_host values
        (
            {"host": "some esxi host", "user": "esxi user", "pwd": "esxi password"},
            "some esxi host",
            "some cool profile",
            {
                "saltext.vmware": {
                    "host": "blerp",
                    "user": "whatever",
                    "password": "coolguy",
                    "esxi_host": {
                        "some esxi host": {
                            "user": "bad user - not from profile",
                            "password": "bad password - not from profile",
                        },
                    },
                    "some cool profile": {
                        "esxi_host": {
                            "some esxi host": {
                                "user": "esxi user",
                                "password": "esxi password",
                            },
                        },
                    },
                },
            },
            {
                "SALTEXT_VMWARE_HOST": "bad environ host",
                "SALTEXT_VMWARE_USER": "bad environ user",
                "SALTEXT_VMWARE_PASSWORD": "bad environ password",
            },
        ),
        # Environ config only
        (
            {"host": "indessed.example.com", "user": "roscivs", "pwd": "bottia"},
            None,
            None,
            {},
            {
                "SALTEXT_VMWARE_HOST": "indessed.example.com",
                "SALTEXT_VMWARE_USER": "roscivs",
                "SALTEXT_VMWARE_PASSWORD": "bottia",
            },
        ),
        # Environ config overrides
        (
            {"host": "indessed.example.com", "user": "roscivs", "pwd": "bottia"},
            None,
            None,
            {"saltext.vmware": {"host": "blerp", "user": "whatever", "password": "coolguy"}},
            {
                "SALTEXT_VMWARE_HOST": "indessed.example.com",
                "SALTEXT_VMWARE_USER": "roscivs",
                "SALTEXT_VMWARE_PASSWORD": "bottia",
            },
        ),
        # Environ config overrides host only
        (
            {"host": "indessed.example.com", "user": "whatever", "pwd": "coolguy"},
            None,
            None,
            {"saltext.vmware": {"host": "blerp", "user": "whatever", "password": "coolguy"}},
            {
                "SALTEXT_VMWARE_HOST": "indessed.example.com",
            },
        ),
        # Environ config overrides user only
        (
            {"host": "blerp", "user": "roscivs", "pwd": "coolguy"},
            None,
            None,
            {"saltext.vmware": {"host": "blerp", "user": "whatever", "password": "coolguy"}},
            {
                "SALTEXT_VMWARE_USER": "roscivs",
            },
        ),
        # Environ config overrides password only
        (
            {"host": "blerp", "user": "whatever", "pwd": "bottia"},
            None,
            None,
            {"saltext.vmware": {"host": "blerp", "user": "whatever", "password": "coolguy"}},
            {
                "SALTEXT_VMWARE_PASSWORD": "bottia",
            },
        ),
        # Environ config replaces missing host
        (
            {"host": "indessed.example.com", "user": "whatever", "pwd": "coolguy"},
            None,
            None,
            {"saltext.vmware": {"user": "whatever", "password": "coolguy"}},
            {
                "SALTEXT_VMWARE_HOST": "indessed.example.com",
            },
        ),
        # Environ config replaces missing user
        (
            {"host": "blerp", "user": "roscivs", "pwd": "coolguy"},
            None,
            None,
            {"saltext.vmware": {"host": "blerp", "password": "coolguy"}},
            {
                "SALTEXT_VMWARE_USER": "roscivs",
            },
        ),
        # Environ config replaces missing password
        (
            {"host": "blerp", "user": "whatever", "pwd": "bottia"},
            None,
            None,
            {
                "saltext.vmware": {
                    "host": "blerp",
                    "user": "whatever",
                }
            },
            {
                "SALTEXT_VMWARE_PASSWORD": "bottia",
            },
        ),
    ],
)
def test_get_service_instance_should_correctly_pass_config_values_to_SmartConnect(
    expected_values, esxi_host, profile, conf_values, environ_values
):
    fake_ssl_ctx = object()
    with mock.patch.dict(os.environ, environ_values), mock.patch(
        "pyVim.connect.SmartConnect", autospec=True
    ) as fake_pyvimconnect, mock.patch(
        "ssl._create_unverified_context", autospec=True, return_value=fake_ssl_ctx
    ):
        connect.get_service_instance(config=conf_values, esxi_host=esxi_host, profile=profile)
        fake_pyvimconnect.assert_called_with(**expected_values, sslContext=fake_ssl_ctx)
