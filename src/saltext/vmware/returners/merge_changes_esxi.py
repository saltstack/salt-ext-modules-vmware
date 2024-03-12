"""
Take changes data from salt and merge different sections in single one

Add the following to the minion or master configuration file.

.. code-block:: yaml

    merge_changes.filename: <path_to_output_file>

Default is ``/var/log/salt/changes``.
"""
import logging

import salt.returners
import salt.utils.files
import salt.utils.json

log = logging.getLogger(__name__)

# Define the module's virtual name
__virtualname__ = "merge_changes_esxi"


def __virtual__():
    return __virtualname__


def _get_options(ret):
    """
    Returns options used for the merge_changes returner.
    """
    defaults = {"filename": "/var/log/salt/changes"}
    attrs = {"filename": "filename"}
    _options = salt.returners.get_returner_options(
        __virtualname__,
        ret,
        attrs,
        __salt__=__salt__,
        __opts__=__opts__,
        defaults=defaults,
    )

    return _options


def returner(ret):
    """
    Write the return data to a file on the minion.
    """
    opts = _get_options(ret)
    return_value = ret["return"]
    changes = {}
    for key in return_value:
        state = return_value[key]
        if key.startswith("vmware_esxi_"):
            if "esxi" not in changes:
                changes["esxi"] = {}
            for host in state["changes"]:
                if host not in changes["esxi"]:
                    changes["esxi"][host] = {}
                changes["esxi"][host][state["__id__"]] = state["changes"][host]["old"]
        else:
            changes[state["__id__"]] = state["changes"]
    with salt.utils.files.flopen(opts["filename"], "a") as logfile:
        salt.utils.json.dump(changes, logfile)
        logfile.write("\n")
