# SPDX-License-Identifier: Apache-2.0
"""
Generate baseline proxy minion grains for ESXi hosts.

.. versionadded:: 2015.8.4

"""
import logging

import salt.utils.proxy
from salt.exceptions import SaltSystemExit

__proxyenabled__ = ["esxi"]
__virtualname__ = "esxi"

log = logging.getLogger(__file__)

GRAINS_CACHE = {}


def __virtual__():

    # import salt.utils.proxy again
    # so it is available for tests.
    import salt.utils.proxy

    try:
        if salt.utils.proxy.is_proxytype(__opts__, "esxi"):
            return __virtualname__
    except KeyError:
        pass

    return False


def esxi():
    return _grains()


def kernel():
    return {"kernel": "proxy"}


def os():
    if not GRAINS_CACHE:
        GRAINS_CACHE.update(_grains())

    try:
        return {"os": GRAINS_CACHE.get("fullName")}
    except AttributeError:
        return {"os": "Unknown"}


def os_family():
    return {"os_family": "proxy"}


def foo():
    return {"foo": "bar"}


def _find_credentials(host):
    """
    Cycle through all the possible credentials and return the first one that
    works.
    """
    log.debug("=== in _find_credentials ===")
    user_names = [__pillar__["proxy"].get("username", "root")]
    passwords = __pillar__["proxy"]["passwords"]
    verify_ssl = __pillar__["proxy"].get("verify_ssl")
    for user in user_names:
        for password in passwords:
            try:
                # Try to authenticate with the given user/password combination
                ret = __salt__["vmware_info.system_info"](
                    host=host, username=user, password=password, verify_ssl=verify_ssl
                )
            except SaltSystemExit:
                # If we can't authenticate, continue on to try the next password.
                continue
            # If we have data returned from above, we've successfully authenticated.
            if ret:
                return user, password
    # We've reached the end of the list without successfully authenticating.
    raise SaltSystemExit("Cannot complete login due to an incorrect user name or password.")


def _grains():
    """
    Get the grains from the proxied device.
    """
    try:
        host = __pillar__["proxy"]["host"]
        if host:
            username, password = _find_credentials(host)
            protocol = __pillar__["proxy"].get("protocol")
            port = __pillar__["proxy"].get("port")
            verify_ssl = __pillar__["proxy"].get("verify_ssl")
            ret = __salt__["vmware_info.system_info"](
                host=host,
                username=username,
                password=password,
                protocol=protocol,
                port=port,
                verify_ssl=verify_ssl,
            )
            GRAINS_CACHE.update(ret)
    except KeyError:
        pass

    return GRAINS_CACHE
