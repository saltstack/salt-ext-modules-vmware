# SPDX-License-Identifier: Apache-2.0
import logging

import saltext.vmware.utils.connect as connect

log = logging.getLogger(__name__)

__virtualname__ = "vsphere_storage_policy"


def __virtual__():
    return __virtualname__


def storage_policy(name, storagePolicies):
    """
    Checks state of storage policy of each host
    policies
        Policy list to set state to
    """

    res = connect.request(
        "/api/vcenter/storage/policies", "GET", opts=__opts__, pillar=__pillar__
    )
    response = res["response"].json()
    current_policies = list(map(lambda p: p['name'], response))
    changes = []
    for policy in storagePolicies:
        if policy['policyName'] not in current_policies:
            changes.append(policy['policyName'])

    ret = {"name": name, "result": True, "comment": "",
           "changes": {"new": changes}}
    return ret