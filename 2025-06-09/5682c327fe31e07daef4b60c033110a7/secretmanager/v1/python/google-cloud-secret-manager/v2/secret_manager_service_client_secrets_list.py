# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python3

# This script lists all secrets in a specified Google Cloud project.
# It requires the GCP_PROJECT_ID environment variable to be set.
#
# Usage:
#   export GCP_PROJECT_ID="your-gcp-project-id"
#   python3 your_script_name.py

import argparse
import os
import json
from google.cloud import secretmanager_v1
from google.api_core import exceptions


# // [START secretmanager_v1_secretmanagerservice_secrets_list]
def list_secrets_sample(project_id: str) -> list[str]:
    """
    Lists all secrets in the given Google Cloud project.

    Args:
        project_id: The ID of the Google Cloud project.

    Returns:
        A list of secret names (full resource paths).

    Raises:
        RuntimeError: If an error occurs during the API call.
    """
    client = secretmanager_v1.SecretManagerServiceClient()
    parent = f"projects/{project_id}"

    secrets_list = []
    try:
        # The list_secrets method returns a pager, which can be
        # iterated directly.
        for secret in client.list_secrets(parent=parent):
            secrets_list.append(secret.name)
    except exceptions.GoogleAPIError as e:
        # Re-raise the exception after printing, so the main function can catch
        # it and format the error output as JSON.
        raise RuntimeError(f"Error listing secrets: {e}") from e
    finally:
        # For SecretManagerServiceClient, there isn't an explicit .close()
        # method that needs to be called. The client manages its own
        # connections.
        pass

    return secrets_list
# // [END secretmanager_v1_secretmanagerservice_secrets_list]


def main():
    """
    Parses command-line arguments (though none are expected for this sample),
    calls the primary sample function, and prints the result.
    """
    # This sample does not take command-line arguments for API parameters,
    # as GCP_PROJECT_ID is expected from environment variables.
    parser = argparse.ArgumentParser(
        description="List secrets in a Google Cloud project."
    )
    args = parser.parse_args() # Parse to allow --help, etc.

    project_id = os.getenv("GCP_PROJECT_ID")

    if not project_id:
        print(
            json.dumps(
                {
                    "error": (
                        "Google Cloud project ID not provided. Please set the "
                        "GCP_PROJECT_ID environment variable."
                    )
                }
            )
        )
        exit(1)

    try:
        secrets = list_secrets_sample(project_id)
        # Print the result as a JSON object.
        print(json.dumps({"secret_names": secrets}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        exit(1)


if __name__ == "__main__":
    main()
