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

# This script demonstrates how to get metadata for a secret in Google Cloud
# Secret Manager.
# It requires the 'google-cloud-secret-manager' Python client library.
#
# Usage:
# 1. Set the GCP_PROJECT_ID environment variable:
#    export GCP_PROJECT_ID="your-gcp-project-id"
# 2. Run the script with the secret ID as a command-line argument:
#    python get_secret.py --secret-id my-secret-name

# [START secretmanager_v1beta1_secretmanagerservice_secret_get]
import os
import argparse
import json

from google.api_core import exceptions
from google.protobuf.json_format import MessageToDict
from google.cloud import secretmanager_v1beta1


def get_secret_sample(project_id: str, secret_id: str):
    """
    Gets metadata for a given Secret.

    Args:
        project_id: The ID of the GCP project.
        secret_id: The ID of the secret to retrieve.

    Returns:
        google.cloud.secretmanager_v1beta1.types.Secret: The retrieved Secret
                                                          object. Returns None if
                                                          the secret is not found
                                                          or an error occurs.
    """
    client = secretmanager_v1beta1.SecretManagerServiceClient()
    name = client.secret_path(project_id, secret_id)

    try:
        response = client.get_secret(name=name)
        return response
    except exceptions.NotFound:
        print(f"Secret '{name}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
# [END secretmanager_v1beta1_secretmanagerservice_secret_get]


def main():
    parser = argparse.ArgumentParser(
        description="Get metadata for a Google Cloud Secret Manager secret."
    )
    parser.add_argument(
        "--secret-id",
        type=str,
        required=True,
        help="The ID of the secret to retrieve (e.g., 'my-secret')."
    )

    args = parser.parse_args()

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        print("Error: GCP_PROJECT_ID environment variable not set.")
        exit(1)

    secret = get_secret_sample(project_id, args.secret_id)

    if secret:
        # Convert the Secret object to a dictionary for JSON serialization
        secret_dict = MessageToDict(secret)
        print(json.dumps(secret_dict, indent=2))


if __name__ == "__main__":
    main()
