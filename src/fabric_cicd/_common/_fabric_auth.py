# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Handles interactions with the Fabric API, including authentication and request management."""

import datetime
import logging

import jwt
from azure.core.credentials import TokenCredential
from azure.core.exceptions import (
    ClientAuthenticationError,
)

import fabric_cicd.constants as constants
from fabric_cicd._common._exceptions import TokenError

logger = logging.getLogger(__name__)


class FabricAuth:
    """Handles authentication with Fabric known APIs"""

    def __init__(self, token_credential: TokenCredential, scope: str, disable_print_identity: bool = False) -> None:
        """
        Initializes the FabricEndpoint instance, sets up the authentication token.

        Args:
            token_credential: The token credential.
            requests_module: The requests module.
            suppress_identity_print: If True, suppresses the printing of the executing identity.
        """
        self.aad_token = None
        self.aad_storage_token = None
        self.aad_token_expiration = None
        self.token_credential = token_credential
        self.disable_print_identity = disable_print_identity
        self._refresh_token(scope)

    def _refresh_token(self, scope: str) -> None:
        """Refreshes the AAD token if empty or expiration has passed."""
        if (
            self.aad_token is None
            or self.aad_token_expiration is None
            or self.aad_token_expiration < datetime.datetime.utcnow()
        ):
            resource_url = scope

            try:
                self.aad_token = self.token_credential.get_token(resource_url).token
            except ClientAuthenticationError as e:
                msg = f"Failed to acquire AAD token. {e}"
                raise TokenError(msg, logger) from e
            except Exception as e:
                msg = f"An unexpected error occurred when generating the AAD token. {e}"
                raise TokenError(msg, logger) from e

            try:
                decoded_token = jwt.decode(self.aad_token, options={"verify_signature": False})

                expiration = decoded_token.get("exp")
                upn = decoded_token.get("upn")
                appid = decoded_token.get("appid")
                oid = decoded_token.get("oid")

                if expiration:
                    self.aad_token_expiration = datetime.datetime.fromtimestamp(expiration)
                else:
                    msg = "Token does not contain expiration claim."
                    raise TokenError(msg, logger)

                if not self.disable_print_identity and "disable_print_identity" not in constants.FEATURE_FLAG:
                    if upn:
                        identity_msg = f"Executing as User '{upn}'"
                    elif appid:
                        identity_msg = f"Executing as Application Id '{appid}'"
                    elif oid:
                        identity_msg = f"Executing as Object Id '{oid}'"
                    logger.info(identity_msg)

            except Exception as e:
                msg = f"An unexpected error occurred while decoding the credential token. {e}"
                raise TokenError(msg, logger) from e
