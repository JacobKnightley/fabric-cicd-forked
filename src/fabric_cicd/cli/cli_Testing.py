import sys

if sys.version_info < (3, 10):
    msg = "This module requires Python 3.10 or newer."
    raise RuntimeError(msg)


import os

from azure.identity import DefaultAzureCredential

# from fabric_cli.core.fab_auth import FabAuth
from fabric_cicd._common._fabric_endpoint import FabricEndpoint

fe = FabricEndpoint(DefaultAzureCredential())

# set these os environment variables
os.environ["FAB_TOKEN"] = fe.fab_token.aad_token
os.environ["FAB_TOKEN_ONELAKE"] = fe.fab_token_storage.aad_token


import fabric_cli.core.fab_constant as fab_constant
from fabric_cli.core.fab_hiearchy import Tenant
from fabric_cli.utils.fab_mem_store import get_workspace_items, get_workspaces  # , get_workspaces

tenant = Tenant(name="Microsoft", id="72f988bf-86f1-41af-91ab-2d7cd011db47")


# print(FabAuth()._is_token_defined())
fab_constant.FAB_CACHE_ENABLED = "false"

workspaces = get_workspaces(tenant)
workspace = next((ws for ws in workspaces if ws.get_id() == "f7436f0f-b175-4421-b9ab-1f6de4175b63"), None)

# print(get_workspace_id(tenant, "HelixFabric-Insights.Workspace"))


items = get_workspace_items(workspace)
for item in items:
    print(item.get_id(), item.get_name(), item.get_type(), item.get_mutable_properties())
