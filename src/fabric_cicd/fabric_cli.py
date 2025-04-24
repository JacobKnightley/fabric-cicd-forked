import sys

if sys.version_info < (3, 10):
    msg = "This module requires Python 3.10 or newer."
    raise RuntimeError(msg)

import os
import subprocess

from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential

import fabric_cicd.constants as constants
from fabric_cicd._common._fabric_auth import FabricAuth
from fabric_cicd._common._validate_input import (
    validate_token_credential,
)


class FabricCLI:
    """A class to handle the Fabric CLI commands and authentication."""

    def __init__(self, token_credential: TokenCredential = None) -> None:
        """
        Initializes the FabricCLI instance, sets up the authentication token.

        Args:
            token_credential: The token credential. If None, uses DefaultAzureCredential.
        """
        # Validate the token_credential if provided
        token_credential = (
            DefaultAzureCredential() if token_credential is None else validate_token_credential(token_credential)
        )
        self.fab_token = FabricAuth(token_credential, constants.SCOPE_FABRIC_DEFAULT, disable_print_identity=True)
        self.fab_token_storage = FabricAuth(
            token_credential, constants.SCOPE_ONELAKE_DEFAULT, disable_print_identity=True
        )
        self.fab_token_azure = FabricAuth(token_credential, constants.SCOPE_AZURE_DEFAULT, disable_print_identity=True)

        self.env = os.environ.copy()

        # self.env["FAB_TOKEN"] = self.fab_token.aad_token
        # self.env["FAB_TOKEN_ONELAKE"] = self.fab_token_storage.aad_token

    def call_fabric_cli(self, command: str) -> str:
        """
        Call the fabric CLI with the given command string and environment variables.
        This function sets the FAB_TOKEN and FAB_TOKEN_ONELAKE environment variables
        using the provided FabricEndpoint object.

        Args:
            command: The command string to be executed by the fabric CLI.
        """
        try:
            result = subprocess.run(
                ["fab", *command.split()],
                env=self.env,
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError as e:
            msg = "The 'fab' CLI is not installed or not in PATH."
            raise RuntimeError(msg) from e

        # print(result)

        if result.returncode > 0 or result.stderr:
            msg = f"Error running fab command. exit_code: '{result.returncode}'; stdout: '{result.stdout}'; stderr: '{result.stderr}'"
            raise Exception(msg)

        return result.stdout.strip()


# Example usage
if __name__ == "__main__":
    # Call the "auth login" subcommand programmatically
    local_fabric_cli = FabricCLI(DefaultAzureCredential())
    result = local_fabric_cli.call_fabric_cli("ls")
    print(result)  # Handle the result as needed
