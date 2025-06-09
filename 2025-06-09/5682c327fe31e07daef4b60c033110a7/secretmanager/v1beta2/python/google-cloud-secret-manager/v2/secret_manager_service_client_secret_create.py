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
import json
import os
import sys
from typing import Optional


#
# [START secretmanager_v1beta2_secretmanagerservice_secret_create]
def create_secret_sample(
    project_id: str, secret_id: str, secret_config_path: Optional[str] = None
) -> "Secret":
    """Creates a new secret.

    Args:
        project_id: The Google Cloud project ID.
        secret_id: The ID of the secret to create.
        secret_config_path: Optional path to a JSON file containing the
            Secret resource configuration. If not provided, a basic
            secret with automatic replication will be created.
            Refer to the official Google Cloud documentation for the Secret
            resource format:
            https://cloud.google.com/secret-manager/docs/reference/rest/v1beta2/projects.secrets#Secret

    Returns:
        The created Secret object.
    """
    # Imports specific to this sample function.
    from google.cloud import secretmanager_v1beta2
    from google.cloud.secretmanager_v1beta2.types import Secret
    from google.protobuf import json_format

    # Create the Secret Manager client.
    # The client is created within a 'with' statement to ensure resources are properly closed.
    with secretmanager_v1beta2.SecretManagerServiceClient() as client:
        parent = f"projects/{project_id}"

        secret_data = {}
        if secret_config_path:
            try:
                with open(secret_config_path, "r") as f:
                    secret_data = json.load(f)
            except FileNotFoundError:
                print(f"Error: Secret configuration file not found at "
                      f"{secret_config_path}", file=sys.stderr)
                sys.exit(1)
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON in secret configuration file at "
                      f"{secret_config_path}", file=sys.stderr)
                sys.exit(1)

        secret = Secret()
        if secret_data:
            try:
                # Parse the dictionary into the Secret protobuf message
                json_format.ParseDict(secret_data, secret)
            except Exception as e:
                print(f"Error parsing secret configuration: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            # If no secret_config_path is provided, create a basic secret with automatic replication.
            secret.replication.automatic.CopyFrom(secretmanager_v1beta2.types.Replication.Automatic())

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
            print(f"Error creating secret: {e}", file=sys.stderr)
            raise
# [END secretmanager_v1beta2_secretmanagerservice_secret_create]


def main():
    parser = argparse.ArgumentParser(
        description="Create a new Google Cloud Secret Manager secret."
    )
    parser.add_argument(
        "--project_id",
        type=str,
        default=os.environ.get("GCP_PROJECT_ID"),
        help="Your Google Cloud project ID. Defaults to the "
             "GCP_PROJECT_ID environment variable.",
    )
    parser.add_argument(
        "--secret_id",
        type=str,
        required=True,
        help="The ID of the secret to create.",
    )
    parser.add_argument(
        "--secret_file",
        type=str,
        help="Path to a JSON file containing the Secret resource configuration. "
             "See https://cloud.google.com/secret-manager/docs/reference/rest/"
             "v1beta2/projects.secrets#Secret for format.",
    )

    args = parser.parse_args()

    if not args.project_id:
        print(
            "Error: --project_id or GCP_PROJECT_ID environment variable "
            "must be set.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        secret = create_secret_sample(
            args.project_id, args.secret_id, args.secret_file
        )
        # Convert the protobuf message to a dictionary for JSON serialization
        # The to_dict() method is available on protobuf messages from google-cloud-python.
        secret_dict = type(secret).to_dict(secret)
        print(json.dumps(secret_dict, indent=2))
    except Exception:
        # Error already printed by the sample function or its callers
        sys.exit(1)


if __name__ == "__main__":
    main()
