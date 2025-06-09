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

# [START secretmanager_v1beta1_secretmanagerservice_secrets_list]
"""
This sample demonstrates how to list secrets in Google Cloud Secret Manager.

It uses the google-cloud-secret-manager SDK to perform the list_secrets
operation. The script takes a project ID as a command-line argument or
from the GCP_PROJECT_ID environment variable.

Usage:
    python your_script_name.py --project-id <your-project-id>

Environment Variables:
    GCP_PROJECT_ID: Your Google Cloud Project ID. This will be used if
                    --project-id is not provided.
"""

import argparse
import os
import json

from google.cloud import secretmanager_v1beta1
from google.api_core import exceptions


def list_secrets_sample(project_id: str):
    """
    Lists all secrets in the given Google Cloud project.

    Args:
        project_id: The ID of the Google Cloud project.

    Returns:
        A list of dictionaries, where each dictionary represents a secret
        with its name, creation time, and labels. Returns an empty list
        if an error occurs or no secrets are found.
    """
    # Initialize the Secret Manager client.
    # The client is designed to be reused.
    client = secretmanager_v1beta1.SecretManagerServiceClient()

    # Build the parent resource name.
    # Format: projects/{project_id}
    parent = f"projects/{project_id}"

    secrets_list = []
    try:
        # List all secrets. The API call returns an iterable pager object.
        for secret in client.list_secrets(parent=parent):
            secrets_list.append(
                {
                    "name": secret.name,
                    "create_time": (
                        secret.create_time.isoformat()
                        if secret.create_time
                        else None
                    ),
                    "labels": dict(secret.labels),
                }
            )
        return secrets_list
    except exceptions.GoogleAPIError as e:
        print(f"Error listing secrets: {e}")
        return []
    finally:
        # In Python, clients are generally managed by garbage collection.
        # Explicit closing is not strictly necessary for this client
        # unless resources need to be immediately released.
        pass


def main():
    parser = argparse.ArgumentParser(
        description="List secrets in a Google Cloud project."
    )
    parser.add_argument(
        "--project-id",
        type=str,
        help=(
            "The ID of the Google Cloud project. Defaults to "
            "GCP_PROJECT_ID environment variable."
        ),
        default=os.environ.get("GCP_PROJECT_ID"),
    )

    args = parser.parse_args()

    if not args.project_id:
        print(
            "Error: --project-id argument or GCP_PROJECT_ID environment "
            "variable must be set."
        )
        parser.print_help()
        exit(1)

    secrets = list_secrets_sample(args.project_id)

    # Print the result as a JSON array of secret objects
    print(json.dumps(secrets, indent=2))


if __name__ == "__main__":
    main()
# [END secretmanager_v1beta1_secretmanagerservice_secrets_list]
