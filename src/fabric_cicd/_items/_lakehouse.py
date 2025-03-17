# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Functions to process and deploy Lakehouse item."""

import json
import logging

from fabric_cicd import FabricWorkspace
from fabric_cicd._common._item import Item

logger = logging.getLogger(__name__)


def publish_lakehouses(fabric_workspace_obj: FabricWorkspace) -> None:
    """
    Publishes all lakehouse items from the repository.

    Args:
        fabric_workspace_obj: The FabricWorkspace object containing the items to be published
    """
    item_type = "Lakehouse"

    for item_name, item in fabric_workspace_obj.repository_items.get(item_type, {}).items():
        creation_payload = None

        for file in item.item_files:
            if file.name == "lakehouse.metadata.json" and "defaultSchema" in file.contents:
                creation_payload = {"enableSchemas": True}
                break

        fabric_workspace_obj._publish_item(item_name=item_name, item_type=item_type, creation_payload=creation_payload)
        publish_shortcuts(fabric_workspace_obj, item)


def publish_shortcuts(fabric_workspace_obj: FabricWorkspace, item_obj: Item) -> None:
    """
    Publishes all shortcuts for a lakehouse item.

    Args:
        fabric_workspace_obj: The FabricWorkspace object containing the items to be published
        item_obj: The item object to publish shortcuts for
    """
    deployed_shortcuts = list_deployed_shortcuts(fabric_workspace_obj, item_obj)

    new_deployed_shortcuts = []

    for file in item_obj.item_files:
        if file.name == "shortcuts.metadata.json":
            shortcuts = json.loads(file.contents)
            if len(shortcuts) == 0:
                logger.debug("No shortcuts found in shortcuts.metadata.json")
                return
            logger.info("Publishing Shortcuts")
            for shortcut in shortcuts:
                shortcut_path = f"{shortcut.path}/{shortcut.name}"
                new_deployed_shortcuts.append(shortcut_path)

                if shortcut_path in deployed_shortcuts:
                    # https://learn.microsoft.com/en-us/rest/api/fabric/core/onelake-shortcuts/update-shortcut
                    fabric_workspace_obj.endpoint.invoke(
                        method="PATCH",
                        url=f"{fabric_workspace_obj.base_api_url}/items/{item_obj.guid}/shortcuts/{shortcut_path}",
                        body=shortcut,
                    )
                else:
                    # https://learn.microsoft.com/en-us/rest/api/fabric/core/onelake-shortcuts/create-shortcut
                    fabric_workspace_obj.endpoint.invoke(
                        method="POST",
                        url=f"{fabric_workspace_obj.base_api_url}/items/{item_obj.guid}/shortcuts",
                        body=shortcut,
                    )

            logger.info("Published")
            break

    # for shortcuts that are in new list, but not in deployed_shortcuts, delete them
    for deployed_shortcut_path in deployed_shortcuts:
        if deployed_shortcut_path not in new_deployed_shortcuts:
            # https://learn.microsoft.com/en-us/rest/api/fabric/core/onelake-shortcuts/delete-shortcut
            fabric_workspace_obj.endpoint.invoke(
                method="DELETE",
                url=f"{fabric_workspace_obj.base_api_url}/items/{item_obj.guid}/shortcuts/{deployed_shortcut_path}",
            )


def list_deployed_shortcuts(fabric_workspace_obj: FabricWorkspace, item_obj: Item) -> list:
    """
    Lists all deployed shortcut paths

    Args:
        fabric_workspace_obj: The FabricWorkspace object containing the items to be published
        item_obj: The item object to list the shortcuts for
    """
    request_url = f"{fabric_workspace_obj.base_api_url}/items/{item_obj.guid}/shortcuts"
    deployed_shortcut_paths = []

    while request_url:
        # https://learn.microsoft.com/en-us/rest/api/fabric/core/onelake-shortcuts/list-shortcuts
        response = fabric_workspace_obj.endpoint.invoke(method="GET", url=request_url)

        shortcuts = response.json()["value"]
        for shortcut in shortcuts["value"]:
            deployed_shortcut_paths.append(f"{shortcut.path}/{shortcut.name}")
        request_url = shortcuts.get("continuationUri", None)

    return deployed_shortcut_paths
