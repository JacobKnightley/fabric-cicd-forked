import sys

if sys.version_info < (3, 10):
    msg = "This module requires Python 3.10 or newer."
    raise RuntimeError(msg)

import os
import subprocess

from azure.identity import DefaultAzureCredential

from fabric_cicd._common._fabric_endpoint import FabricEndpoint


def call_fabric_cli(fabric_endpoint, command_str):
    env = os.environ.copy()
    env["FAB_TOKEN"] = fabric_endpoint.fab_token.aad_token
    env["FAB_TOKEN_ONELAKE"] = fabric_endpoint.fab_token_storage.aad_token

    result = subprocess.run(
        ["fab", *command_str.split()],
        env=env,
        capture_output=True,
        text=True,
    )

    if result.returncode > 0 or result.stderr:
        msg = f"Error running fab command. exit_code: '{result.returncode}'; stderr: '{result.stderr}'"
        raise Exception(msg)

    return result.stdout.strip()


# Example usage
if __name__ == "__main__":
    # Call the "auth login" subcommand programmatically
    result = call_fabric_cli(FabricEndpoint(DefaultAzureCredential()), "ls")
    print(result)  # Handle the result as needed
