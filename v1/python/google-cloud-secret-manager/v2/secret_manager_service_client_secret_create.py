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

# [START secretmanager_v1_secretmanagerservice_secret_create]
import argparse
import os
import json
from typing import Dict, Any

from google.cloud import secretmanager_v1

def create_secret_sample(
    project_id: str, secret_id: str, secret_config: Dict[str, Any]
) -> secretmanager_v1.Secret:
    """
    Creates a new secret in Google Secret Manager.

    Args:
        project_id: The Google Cloud project ID.
        secret_id: The ID of the secret to create.
        secret_config: A dictionary representing the Secret object's configuration.
                       For more information about the Secret object, see:
                       https://cloud.google.com/secret-manager/docs/reference/rest/v1/projects.secrets#Secret

    Returns:
        The created Secret object.
    """
    client = secretmanager_v1.SecretManagerServiceClient()

    # Build the parent name.
    # For regional secrets, use the format:
    # "projects/PROJECT_ID/locations/LOCATION_ID"
    # For global secrets, use the format: "projects/PROJECT_ID"
    # This sample uses global secrets.
    parent = f"projects/{project_id}"

    # Create the secret object from the provided configuration.
    # The secret_config dictionary should conform to the Secret proto message.
    secret = secretmanager_v1.Secret(secret_config)

    try:
        created_secret = client.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_id,
                "secret": secret,
            }
        )
        return created_secret
    except Exception as e:
        print(f"Error creating secret: {e}")
        raise
# [END secretmanager_v1_secretmanagerservice_secret_create]


def main():
    parser = argparse.ArgumentParser(
        description="Create a Google Secret Manager secret."
    )
    parser.add_argument(
        "--secret-id",
        type=str,
        required=True,
        help="The ID of the secret to create.",
    )
    parser.add_argument(
        "--secret-config-file",
        type=str,
        required=True,
        help=(
            "Path to a JSON file containing the Secret object configuration. "
            "See https://cloud.google.com/secret-manager/docs/reference/rest/v1/"
            "projects.secrets#Secret for the expected format. "
            "Example: '{\"replication\": {\"automatic\": {}}}'"
        ),
    )

    args = parser.parse_args()

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        raise ValueError("GCP_PROJECT_ID environment variable not set.")

    # Read secret configuration from file
    try:
        with open(args.secret_config_file, "r") as f:
            secret_config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Secret config file not found at {args.secret_config_file}")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in secret config file {args.secret_config_file}")
        exit(1)

    print(
        f"Attempting to create secret '{args.secret_id}' "
        f"in project '{project_id}' with config from '{args.secret_config_file}'..."
    )
    try:
        result = create_secret_sample(project_id, args.secret_id, secret_config)
        # Convert the protobuf message to a dictionary for pretty printing
        result_dict = type(result).to_dict(result)
        print(json.dumps(result_dict, indent=2))
    except Exception as e:
        print(f"Failed to create secret: {e}")
        exit(1)


if __name__ == "__main__":
    main()
