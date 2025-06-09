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

import argparse
import os
import json

from google.cloud import secretmanager_v1beta2
from google.api_core import exceptions


def list_secrets_sample(project_id: str, location_id: str = None) -> list:
    """Lists secrets in a Google Cloud project or specific location.

    Args:
        project_id: The Google Cloud project ID.
        location_id: Optional. The location ID (e.g., 'global', 'us-central1').
                     If not specified, lists secrets across all locations.

    Returns:
        A list of dictionaries, each representing a secret with its name,
        creation time, and replication status. Returns an empty list on error.
    """
    # [START secretmanager_v1beta2_secretmanagerservice_secrets_list]
    # Create a client
    # SecretManagerServiceClient does not require explicit closing.
    # The client is thread-safe and can be reused across multiple API calls.
    # For more details, see:
    # https://googleapis.dev/python/google-api-core/latest/client_options.html
    with secretmanager_v1beta2.SecretManagerServiceClient() as client:
        if location_id:
            parent = f"projects/{project_id}/locations/{location_id}"
        else:
            parent = f"projects/{project_id}"

        secrets_list = []
        try:
            # List all secrets in the given project or location.
            # The list_secrets method returns an iterable pager.
            for secret in client.list_secrets(parent=parent):
                secrets_list.append({
                    "name": secret.name,
                    "create_time": (
                        secret.create_time.isoformat()
                        if secret.create_time
                        else None
                    ),
                    "replication": {
                        "automatic": secret.replication.automatic is not None
                    }
                })
        except exceptions.GoogleAPIError as e:
            print(f"Error listing secrets: {e}")
            # Return an empty list on error as per sample requirements.
            secrets_list = []
        return secrets_list
    # [END secretmanager_v1beta2_secretmanagerservice_secrets_list]


def main():
    """Parses command-line arguments and calls the list secrets sample."""
    parser = argparse.ArgumentParser(
        description="List secrets in a Google Cloud project."
    )
    parser.add_argument(
        "--location_id",
        type=str,
        default=None,
        help=(
            "Optional. The location ID (e.g., 'global', 'us-central1'). "
            "If not specified, lists secrets across all locations."
        ),
    )

    args = parser.parse_args()

    # Global configuration values MUST be sourced from system environment variables.
    # GCP_PROJECT_ID is a global configuration value.
    project_id = os.environ.get("GCP_PROJECT_ID")

    if not project_id:
        print(
            "Error: Google Cloud project ID not provided. "
            "Please set the GCP_PROJECT_ID environment variable."
        )
        exit(1)

    secrets = list_secrets_sample(project_id, args.location_id)
    print(json.dumps(secrets, indent=2))


if __name__ == "__main__":
    main()
