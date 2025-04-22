# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Handles interactions with the Fabric API, including authentication and request management."""

import json
import logging
import time
from typing import Optional

import requests
from azure.core.credentials import TokenCredential

import fabric_cicd.constants as constants
from fabric_cicd._common._exceptions import InvokeError
from fabric_cicd._common._fabric_auth import FabricAuth

logger = logging.getLogger(__name__)


class FabricEndpoint:
    """Handles interactions with the Fabric API, including authentication and request management."""

    def __init__(self, token_credential: TokenCredential, requests_module: requests = requests) -> None:
        """
        Initializes the FabricEndpoint instance, sets up the authentication token.

        Args:
            token_credential: The token credential.
            requests_module: The requests module.
        """
        self.requests = requests_module
        self.fab_token = FabricAuth(token_credential, "https://api.fabric.microsoft.com/.default")
        self.fab_token_storage = FabricAuth(token_credential, "https://storage.azure.com/.default")
        self.fab_token_azure = FabricAuth(token_credential, "https://management.azure.com/.default")

    def invoke(self, method: str, url: str, body: str = "{}", files: Optional[dict] = None, **kwargs) -> dict:
        """
        Sends an HTTP request to the specified URL with the given method and body.

        Args:
            method: HTTP method to use for the request (e.g., 'GET', 'POST', 'PATCH', 'DELETE').
            url: URL to send the request to.
            body: The JSON body to include in the request. Defaults to an empty JSON object.
            files: The file path to be included in the request. Defaults to None.
            **kwargs: Additional keyword arguments to pass to the method.
        """
        exit_loop = False
        iteration_count = 0
        long_running = False
        start_time = time.time()
        invoke_log_message = ""

        while not exit_loop:
            try:
                headers = {
                    "Authorization": f"Bearer {self.fab_token}",
                    "User-Agent": f"{constants.USER_AGENT}",
                }
                if files is None:
                    headers["Content-Type"] = "application/json; charset=utf-8"
                response = self.requests.request(method=method, url=url, headers=headers, json=body, files=files)

                iteration_count += 1

                invoke_log_message = _format_invoke_log(response, method, url, body)

                # Handle expired authentication token
                if response.status_code == 401 and response.headers.get("x-ms-public-api-error-code") == "TokenExpired":
                    logger.info(f"{constants.INDENT}AAD token expired. Refreshing token.")
                    self.fab_token._refresh_token()
                else:
                    exit_loop, method, url, body, long_running = _handle_response(
                        response,
                        method,
                        url,
                        body,
                        long_running,
                        iteration_count,
                        **kwargs,
                    )

                # Log if reached to end of loop iteration
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(invoke_log_message)

            except Exception as e:
                logger.debug(invoke_log_message)
                raise InvokeError(e, logger, invoke_log_message) from e

        end_time = time.time()
        logger.debug(f"Request completed in {end_time - start_time} seconds")

        return {
            "header": dict(response.headers),
            "body": (response.json() if "application/json" in response.headers.get("Content-Type") else {}),
            "status_code": response.status_code,
        }


def _handle_response(
    response: requests.Response,
    method: str,
    url: str,
    body: str,
    long_running: bool,
    iteration_count: int,
    **kwargs: any,
) -> tuple:
    """
    Handles the response from an HTTP request, including retries, throttling, and token expiration.
    Technical debt: this method needs to be refactored to be more testable and requires less parameters.
    Initial approach is only temporary to support testing, but only temporary.

    Args:
        response: The response object from the HTTP request.
        method: The HTTP method used in the request.
        url: The URL used in the request.
        body: The JSON body used in the request.
        long_running: A boolean indicating if the operation is long-running.
        iteration_count: The current iteration count of the loop.
        kwargs: Additional keyword arguments to pass to the method.
    """
    exit_loop = False
    retry_after = response.headers.get("Retry-After", 60)

    # Handle long-running operations
    # https://learn.microsoft.com/en-us/rest/api/fabric/core/long-running-operations/get-operation-result
    if (response.status_code == 200 and long_running) or response.status_code == 202:
        url = response.headers.get("Location")
        method = "GET"
        body = "{}"
        response_json = response.json()

        if long_running:
            status = response_json.get("status")
            if status == "Succeeded":
                long_running = False
                # If location not included in operation success call, no body is expected to be returned
                exit_loop = url is None

            elif status == "Failed":
                response_error = response_json["error"]
                msg = (
                    f"Operation failed. Error Code: {response_error['errorCode']}. "
                    f"Error Message: {response_error['message']}"
                )
                raise Exception(msg)
            elif status == "Undefined":
                msg = f"Operation is in an undefined state. Full Body: {response_json}"
                raise Exception(msg)
            else:
                handle_retry(
                    attempt=iteration_count - 1,
                    base_delay=0.5,
                    response_retry_after=retry_after,
                    max_retries=kwargs.get("max_retries", 5),
                    prepend_message=f"{constants.INDENT}Operation in progress.",
                )
        else:
            time.sleep(1)
            long_running = True

    # Handle successful responses
    elif response.status_code in {200, 201} or (
        # Valid response for environmentlibrariesnotfound
        response.status_code == 404
        and response.headers.get("x-ms-public-api-error-code") == "EnvironmentLibrariesNotFound"
    ):
        exit_loop = True

    # Handle API throttling
    elif response.status_code == 429:
        handle_retry(
            attempt=iteration_count,
            base_delay=10,
            max_retries=5,
            response_retry_after=retry_after,
            prepend_message="API is throttled.",
        )

    # Handle unauthorized access
    elif response.status_code == 401 and response.headers.get("x-ms-public-api-error-code") == "Unauthorized":
        msg = f"The executing identity is not authorized to call {method} on '{url}'."
        raise Exception(msg)

    # Handle item name conflicts
    elif (
        response.status_code == 400
        and response.headers.get("x-ms-public-api-error-code") == "ItemDisplayNameAlreadyInUse"
    ):
        handle_retry(
            attempt=iteration_count,
            base_delay=30,
            max_retries=5,
            response_retry_after=300,
            prepend_message="Item name is reserved.",
        )

    # Handle scenario where library removed from environment before being removed from repo
    elif response.status_code == 400 and "is not present in the environment." in response.json().get(
        "message", "No message provided"
    ):
        msg = (
            f"Deployment attempted to remove a library that is not present in the environment. "
            f"Description: {response.json().get('message')}"
        )
        raise Exception(msg)

    # Handle unsupported principal type
    elif (
        response.status_code == 400
        and response.headers.get("x-ms-public-api-error-code") == "PrincipalTypeNotSupported"
    ):
        msg = f"The executing principal type is not supported to call {method} on '{url}'."
        raise Exception(msg)

    # Handle unsupported item types
    elif response.status_code == 403 and response.reason == "FeatureNotAvailable":
        msg = f"Item type not supported. Description: {response.reason}"
        raise Exception(msg)

    # Handle unexpected errors
    else:
        err_msg = (
            f" Message: {response.json()['message']}.  {response.json().get('moreDetails', '')}"
            if "application/json" in (response.headers.get("Content-Type") or "")
            else ""
        )
        msg = f"Unhandled error occurred calling {method} on '{url}'.{err_msg}"
        raise Exception(msg)

    return exit_loop, method, url, body, long_running


def handle_retry(
    attempt: int, base_delay: float, max_retries: int, response_retry_after: float = 60, prepend_message: str = ""
) -> None:
    """
    Handles retry logic with exponential backoff based on the response.

    Args:
        attempt: The current attempt number.
        base_delay: Base delay in seconds for backoff.
        max_retries: Maximum number of retry attempts.
        response_retry_after: The value of the Retry-After header from the response.
        prepend_message: Message to prepend to the retry log.
    """
    if attempt < max_retries:
        retry_after = float(response_retry_after)
        base_delay = float(base_delay)
        delay = min(retry_after, base_delay * (2**attempt))

        # modify output for proper plurality and formatting
        delay_str = f"{delay:.0f}" if delay.is_integer() else f"{delay:.2f}"
        second_str = "second" if delay == 1 else "seconds"
        prepend_message += " " if prepend_message else ""

        logger.info(
            f"{constants.INDENT}{prepend_message}Checking again in {delay_str} {second_str} (Attempt {attempt}/{max_retries})..."
        )
        time.sleep(delay)
    else:
        msg = f"Maximum retry attempts ({max_retries}) exceeded."
        raise Exception(msg)


def _format_invoke_log(response: requests.Response, method: str, url: str, body: str) -> str:
    """
    Format the log message for the invoke method.

    Args:
        response: The response object from the HTTP request.
        method: The HTTP method used in the request.
        url: The URL used in the request.
        body: The JSON body used in the request.
    """
    message = [
        f"\nURL: {url}",
        f"Method: {method}",
        (f"Request Body:\n{json.dumps(body, indent=4)}" if body else "Request Body: None"),
    ]
    if response is not None:
        message.extend([
            f"Response Status: {response.status_code}",
            "Response Headers:",
            json.dumps(dict(response.headers), indent=4),
            "Response Body:",
            (
                json.dumps(response.json(), indent=4)
                if response.headers.get("Content-Type") == "application/json"
                else response.text
            ),
            "",
        ])

    return "\n".join(message)
