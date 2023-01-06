# SPDX-License-Identifier: Apache-2.0
import logging

import salt.utils.data

log = logging.getLogger(__name__)

__virtualname__ = "vsphere_content_library"


def __virtual__():
    return __virtualname__


def _transform_libraries_to_state(libraries):
    result = {}
    for name, library in libraries.items():
        library_state = {}
        library_state["description"] = library["description"]
        library_state["published"] = library["publish_info"]["published"]
        library_state["authentication"] = library["publish_info"]["authentication_method"]
        library_state["datastore"] = library["storage_backings"][0]["datastore_id"]
        result[name] = library_state
    return result


def _transform_config_to_state(config):
    result = {}
    for library in config:
        if "name" not in library:
            raise ValueError("Every library configuration should have a name")
        library_state = {}
        if "description" in library:
            library_state["description"] = library["description"]
        if "published" in library:
            library_state["published"] = library["published"]
        if "authentication" in library:
            library_state["authentication"] = library["authentication"]
        if "datastore" in library:
            library_state["datastore"] = library["datastore"]
        result[library["name"]] = library_state
    return result


def local(name, config):
    """
    Set local content libraries based on configuration.

    name
        Name of configuration. (required).

    libraries
        List of libraries with configuration values. (required).

        Example:

        content_library_example:
          vsphere_content_library.local:
            name: local_example
            config:
              - name: publish
                published: true
                authentication: NONE
                datastore: datastore-00001
              - name: local
                datastore: datastore-00001
    """

    current_libraries = __salt__["vsphere_content_library.list_detailed"]()
    old_state = _transform_libraries_to_state(current_libraries)
    new_state = _transform_config_to_state(config)
    changes = salt.utils.data.recursive_diff(old_state, new_state)
    changes_required = any(changes["new"].values())
    if not __opts__["test"] and changes_required:
        for name, library in changes["new"].items():
            if name in changes["old"]:
                library_id = current_libraries[name]["id"]
                __salt__["vsphere_content_library.update"](library_id, library)
            else:
                if "datastore" not in library:
                    raise ValueError(
                        "Non existing libraries must be provided with a datastore ID for creation"
                    )
                new_library = {
                    "name": name,
                    "datastore": library["datastore"],
                    "published": library.get("published") or False,
                    "authentication": library.get("authentication") or "NONE",
                }
                __salt__["vsphere_content_library.create"](new_library)
    return {"name": name, "result": True, "comment": "", "changes": changes}
