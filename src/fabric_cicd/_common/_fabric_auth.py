# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Handles interactions with the Fabric API, including authentication and request management."""

import base64
import datetime
import json
import logging

from azure.core.credentials import TokenCredential
from azure.core.exceptions import (
    ClientAuthenticationError,
)

import fabric_cicd.constants as constants
from fabric_cicd._common._exceptions import TokenError

logger = logging.getLogger(__name__)


class FabricAuth:
    """Handles authentication with Fabric known APIs"""

    def __init__(self, token_credential: TokenCredential, scope: str) -> None:
        """
        Initializes the FabricEndpoint instance, sets up the authentication token.

        Args:
            token_credential: The token credential.
            requests_module: The requests module.
        """
        self.aad_token = None
        self.aad_storage_token = None
        self.aad_token_expiration = None
        self.token_credential = token_credential
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
                decoded_token = _decode_jwt(self.aad_token)
                expiration = decoded_token.get("exp")
                upn = decoded_token.get("upn")
                appid = decoded_token.get("appid")
                oid = decoded_token.get("oid")

                if expiration:
                    self.aad_token_expiration = datetime.datetime.fromtimestamp(expiration)
                else:
                    msg = "Token does not contain expiration claim."
                    raise TokenError(msg, logger)

                if upn:
                    _log_executing_identity(f"Executing as User '{upn}'")
                    self.upn_auth = True
                else:
                    self.upn_auth = False
                    if appid:
                        _log_executing_identity(f"Executing as Application Id '{appid}'")
                    elif oid:
                        _log_executing_identity(f"Executing as Object Id '{oid}'")

            except Exception as e:
                msg = f"An unexpected error occurred while decoding the credential token. {e}"
                raise TokenError(msg, logger) from e


def _log_executing_identity(msg: str) -> None:
    if "disable_print_identity" not in constants.FEATURE_FLAG:
        logger.info(msg)


def _decode_jwt(token: str) -> dict:
    """
    Decodes a JWT token and returns the payload as a dictionary.

    Args:
        token: The JWT token to decode.
    """
    try:
        # Split the token into its parts
        parts = token.split(".")
        if len(parts) != 3:
            msg = "The token has an invalid JWT format"
            raise TokenError(msg, logger)

        # Decode the payload (second part of the token)
        payload = parts[1]
        padding = "=" * (4 - len(payload) % 4)
        payload += padding
        decoded_bytes = base64.urlsafe_b64decode(payload.encode("utf-8"))
        decoded_str = decoded_bytes.decode("utf-8")
        return json.loads(decoded_str)
    except Exception as e:
        msg = f"An unexpected error occurred while decoding the credential token. {e}"
        raise TokenError(msg, logger) from e
