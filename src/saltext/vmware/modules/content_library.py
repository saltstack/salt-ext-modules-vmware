# Copyright 2021 VMware, Inc.
# SPDX-License: Apache-2.0
import logging

import saltext.vmware.utils.connect as connect

log = logging.getLogger(__name__)

__virtualname__ = "vsphere_content_library"


def __virtual__():
    return __virtualname__


def list():
    """
    Lists IDs for all the content libraries on a given vCenter.
    """
    response = connect.request(
        "/api/content/local-library", "GET", opts=__opts__, pillar=__pillar__
    )
    return response["response"].json()


def list_detailed():
    """
    Lists all the content libraries on a given vCenter with all their details.
    """
    result = {}
    library_ids = list()
    for library_id in library_ids:
        response = get(library_id)
        name = response["name"]
        result[name] = response
    return result


def get(id):
    """
    Returns info on given content library.

    id
        (string) Content Library ID.
    """
    url = f"/api/content/local-library/{id}"
    response = connect.request(url, "GET", opts=__opts__, pillar=__pillar__)
    return response["response"].json()


def create(library):
    """
    Creates a new content library.

    library
        Dictionary having values for library, as following:

        name
            Name of the content library.

        description
            (optional) Description for the content library being created.

        datastore
            Datastore ID where library will store its contents.

        published
            (optional) Whether the content library should be published or not.

        authentication
            (optional) The authentication method when the content library is published.
    """

    publish_info = {
        "published": library["published"],
        "authentication_method": library["authentication"],
    }
    storage_backings = {"datastore_id": library["datastore"], "type": "DATASTORE"}

    data = {
        "name": library["name"],
        "publish_info": publish_info,
        "storage_backings": storage_backings,
        "type": "LOCAL",
    }
    if "description" in library:
        data["description"] = library["description"]

    response = connect.request(
        "/api/content/local-library", "POST", body=data, opts=__opts__, pillar=__pillar__
    )
    return response["response"].json()


def update(id, library):
    """
    Updates content library with given id.

    id
        (string) Content library ID .

    library
        Dictionary having values for library, as following:

        name
            (optional) Name of the content library.

        description
            (optional) Description for the content library being updated.

        published
            (optional) Whether the content library should be published or not.

        authentication
            (optional) The authentication method when the content library is published.

        datastore
            (optional) Datastore ID where library will store its contents.
    """

    publish_info = {"published": published, "authentication_method": authentication}
    storage_backings = {"datastore_id": datastore, "type": "DATASTORE"}

    data = {}
    if name is not None:
        data["name"] = name
    if description is not None:
        data["name"] = description
    if published is not None:
        data["publish_info"] = publish_info
    if datastore is not None:
        data["storage_backings"] = storage_backings

    url = f"/api/content/local-library/{id}"
    response = connect.request(url, "PATCH", body=data, opts=__opts__, pillar=__pillar__)
    return response["response"].json()


def delete(id):
    """
    Delete content library having corresponding id.

    id
        (string) Content library ID to delete.
    """
    url = f"/api/content/local-library/{id}"
    response = connect.request(url, "DELETE", opts=__opts__, pillar=__pillar__)
    return response["response"].json()
