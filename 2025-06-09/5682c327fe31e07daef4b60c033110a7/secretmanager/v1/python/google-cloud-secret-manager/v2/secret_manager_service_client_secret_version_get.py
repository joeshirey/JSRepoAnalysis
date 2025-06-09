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

# [START secretmanager_v1_secretmanagerservice_secretversion_get]
# The START tag must be before any imports as per instructions.

import os
import argparse
import json
from google.cloud import secretmanager_v1
from google.protobuf.json_format import MessageToDict


def get_secret_version_sample(
    project_id: str, secret_id: str, version_id: str
):
    """Gets metadata for a SecretVersion.

    Args:
        project_id: The ID of the GCP project.
        secret_id: The ID of the secret.
        version_id: The version of the secret (e.g., '1', '2', or 'latest').
    Returns:
        google.cloud.secretmanager_v1.types.SecretVersion: The SecretVersion
            object.
    """
    client = secretmanager_v1.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    # Format: projects/{project}/secrets/{secret}/versions/{secret_version}
    # 'latest' can be used for version_id to get the most recently created
    # version.
    name = client.secret_version_path(project_id, secret_id, version_id)

    try:
        # Get the secret version.
        response = client.get_secret_version(name=name)
        return response
    except Exception as e:
        # Re-raising the exception after printing, as per typical error handling
        # in samples where the main function handles exit.
        print(f"Error getting secret version: {e}")
        raise
    finally:
        # In Python, clients are generally context managers and handle their
        # own cleanup. For SecretManagerServiceClient, there's no explicit
        # close() method needed.
        pass
# [END secretmanager_v1_secretmanagerservice_secretversion_get]


def main():
    parser = argparse.ArgumentParser(
        description="Get a Secret Version from Google Cloud Secret Manager."
    )
    parser.add_argument(
        "--secret_id",
        type=str,
        required=True,
        help="The ID of the secret (e.g., 'my-secret')."
    )
    parser.add_argument(
        "--version_id",
        type=str,
        required=True,
        help="The version of the secret (e.g., '1', '2', or 'latest')."
    )

    args = parser.parse_args()

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        print("Error: GCP_PROJECT_ID environment variable not set.")
        exit(1)

    try:
        secret_version = get_secret_version_sample(
            project_id=project_id,
            secret_id=args.secret_id,
            version_id=args.version_id
        )
        # Convert the SecretVersion object to a dictionary for JSON output
        output = MessageToDict(secret_version)
        print(json.dumps(output, indent=2))
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)


if __name__ == "__main__":
    main()