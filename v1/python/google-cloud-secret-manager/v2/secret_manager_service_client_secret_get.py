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

// [START secretmanager_v1_secretmanagerservice_secret_get]
import argparse
import os
import json
from google.cloud import secretmanager_v1
from google.api_core import exceptions
from google.protobuf.json_format import MessageToDict


def get_secret_sample(project_id: str, secret_id: str):
    """Retrieves metadata for a given Secret.

    Args:
        project_id: The Google Cloud project ID.
        secret_id: The ID of the secret to retrieve.

    Returns:
        google.cloud.secretmanager_v1.types.Secret: The retrieved Secret object,
        or None if an error occurred or the secret was not found.
    """
    client = secretmanager_v1.SecretManagerServiceClient()
    name = client.secret_path(project=project_id, secret=secret_id)

    try:
        response = client.get_secret(name=name)
        return response
    except exceptions.NotFound:
        print(f"Secret '{name}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
# [END secretmanager_v1_secretmanagerservice_secret_get]


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Get metadata for a Google Cloud Secret Manager secret."
    )
    parser.add_argument(
        "--project_id",
        type=str,
        default=os.environ.get("GCP_PROJECT_ID"),
        help=(
            "Your Google Cloud project ID. Defaults to the GCP_PROJECT_ID "
            "environment variable."
        ),
        required=False,
    )
    parser.add_argument(
        "--secret_id",
        type=str,
        help="The ID of the secret to retrieve (e.g., 'my-secret').",
        required=True,
    )

    args = parser.parse_args()

    if not args.project_id:
        raise ValueError(
            "Project ID must be provided either via --project_id or the "
            "GCP_PROJECT_ID environment variable."
        )

    secret = get_secret_sample(args.project_id, args.secret_id)

    if secret:
        # Convert the Secret object to a dictionary for JSON serialization.
        # preserving_proto_field_name=True ensures field names match the proto
        # definition (e.g., create_time instead of createTime).
        secret_dict = MessageToDict(secret, preserving_proto_field_name=True)
        print(json.dumps(secret_dict, indent=2))
    else:
        # If secret is None, an error message was already printed by the sample
        # function. Exit with a non-zero code to indicate failure.
        exit(1)


if __name__ == "__main__":
    main()
