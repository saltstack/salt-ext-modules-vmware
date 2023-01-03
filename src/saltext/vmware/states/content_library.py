# SPDX-License-Identifier: Apache-2.0
import json
import logging

import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.connect as connect

log = logging.getLogger(__name__)

__virtualname__ = "content_library"


def __virtual__():
    return __virtualname__


def local(name, config):
    """
    Set local content libraries based on configuration.

    name
        Name of configuration. (required).

    libraries
        List of libraries with configuration values. (required).

        Example:

        content_library_example:
          content_library.local:
            name: local_example
            config:
              - name: publish
                published: true
                authentication: NONE
                datastore: datastore-00001
              - name: local
                datastore: datastore-00001
    """

    current_state = __salt__["content_library.list_detailed"]()
    changes = {}
    return {"name": name, "result": True, "comment": "", "changes": changes}
