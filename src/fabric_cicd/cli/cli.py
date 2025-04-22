import os

from azure.identity import DefaultAzureCredential

# from fabric_cli.core.fab_auth import FabAuth
from fabric_cicd._common._fabric_endpoint import FabricEndpoint

SCOPE_FABRIC_DEFAULT = ["https://analysis.windows.net/powerbi/api/.default"]
SCOPE_ONELAKE_DEFAULT = ["https://storage.azure.com/.default"]
SCOPE_AZURE_DEFAULT = ["https://management.azure.com/.default"]


fe = FabricEndpoint(DefaultAzureCredential())

# set these os environment variables
os.environ["FAB_TOKEN"] = fe.fab_token.aad_token
os.environ["FAB_TOKEN_ONELAKE"] = fe.fab_token_storage.aad_token

# os.environ["FAB_TOKEN_AZURE"] = ""

# print(FabAuth()._get_access_token_from_env_vars_if_exist(SCOPE_FABRIC_DEFAULT))

# t = subprocess.run(["fab", "-c", "ls"], capture_output=True, text=True)
# print(t)

import contextlib
import io
import sys

from fabric_cli.main import main as fab_cli

sys.argv = ["fab", "-c", "ls"]

# Capture stdout and stderr
stdout_buffer = io.StringIO()
stderr_buffer = io.StringIO()
with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
    try:
        fab_cli()
    except SystemExit:
        # Prevent exit from killing your script
        pass

output = stdout_buffer.getvalue()
error_output = stderr_buffer.getvalue()

# Now you can use 'output' and 'error_output' as needed
print("Captured output:", output)
print("Captured errors:", error_output)
