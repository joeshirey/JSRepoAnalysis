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

# A sample that demonstrates how to get metadata for a specific secret version
# using the Google Cloud Secret Manager API.

# [START secretmanager_v1_secretmanagerservice_secretversion_get]
import argparse
import os
import json

from google.cloud import secretmanager_v1

def get_secret_version_sample(
    project_id: str, secret_id: str, version_id: str
):
    """
    Gets metadata for a specific secret version.

    Args:
        project_id: The Google Cloud project ID.
        secret_id: The ID of the secret.
        version_id: The version ID of the secret (e.g., '1', '2', or 'latest').
    """
    # Create the Secret Manager client.
    # Using 'with' statement ensures the client is properly closed.
    with secretmanager_v1.SecretManagerServiceClient() as client:
        # Build the resource name of the secret version.
        # The format is projects/*/secrets/*/versions/*
        # You can also use 'latest' as the version ID to get the most
        # recent version.
        name = client.secret_version_path(project_id, secret_id, version_id)

        try:
            # Get the secret version metadata.
            response = client.get_secret_version(name=name)
            return response
        except Exception as e:
            print(f"Error getting secret version: {e}")
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get metadata for a specific secret version."
    )
    parser.add_argument(
        "--secret_id", required=True, help="The ID of the secret."
    )
    parser.add_argument(
        "--version_id",
        required=True,
        help="The version ID of the secret (e.g., '1', '2', or 'latest').",
    )

    args = parser.parse_args()

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        raise ValueError("GCP_PROJECT_ID environment variable not set.")

    try:
        secret_version = get_secret_version_sample(
            project_id, args.secret_id, args.version_id
        )
        # Convert the protobuf message to a dictionary and then to JSON string
        # for pretty printing.
        print(
            json.dumps(
                secretmanager_v1.SecretVersion.to_dict(secret_version),
                indent=2
            )
        )
    except Exception as e:
        print(f"Failed to execute sample: {e}")
        exit(1)
# [END secretmanager_v1_secretmanagerservice_secretversion_get]
