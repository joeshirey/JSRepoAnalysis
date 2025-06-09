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

# [START secretmanager_v1_secretmanagerservice_secrets_list]
import argparse
import os
import json
import sys
from google.cloud import secretmanager_v1
from google.api_core import exceptions


def list_secrets_sample(project_id: str) -> list:
    """Lists all secrets in the given project.

    Args:
        project_id: The ID of the Google Cloud project.

    Returns:
        A list of dictionaries, each representing a secret with its name,
        project ID, secret ID, creation time, and labels.
    """
    client = secretmanager_v1.SecretManagerServiceClient()
    parent = f"projects/{project_id}"

    secrets = []
    try:
        # The list_secrets method returns a pager, which can be iterated directly.
        for secret in client.list_secrets(parent=parent):
            secrets.append(
                {
                    "name": secret.name,
                    "project_id": secret.name.split("/")[1],  # Extract project_id from name
                    "secret_id": secret.name.split("/")[3],  # Extract secret_id from name
                    "create_time": (
                        secret.create_time.isoformat() if secret.create_time else None
                    ),
                    "labels": dict(secret.labels) if secret.labels else {},
                }
            )
        return secrets
    except exceptions.GoogleAPIError as e:
        print(f"Error listing secrets: {e}", file=sys.stderr)
        raise
    finally:
        # The SecretManagerServiceClient does not require explicit closing.
        # Resources are managed by the underlying gRPC channel.
        pass


def main():
    """
    Main entry point for the script.
    Retrieves the project ID from environment variables and calls
    the list_secrets_sample function.
    """
    parser = argparse.ArgumentParser(
        description="List secrets in a Google Cloud project."
    )
    # No command-line arguments are needed for this specific API call,
    # as the project ID is sourced from an environment variable.
    _ = parser.parse_args()

    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        print(
            "Error: GCP_PROJECT_ID environment variable not set.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        secrets_list = list_secrets_sample(project_id)
        # Print the result as a JSON array of secret details
        print(json.dumps(secrets_list, indent=2))
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
# [END secretmanager_v1_secretmanagerservice_secrets_list]
