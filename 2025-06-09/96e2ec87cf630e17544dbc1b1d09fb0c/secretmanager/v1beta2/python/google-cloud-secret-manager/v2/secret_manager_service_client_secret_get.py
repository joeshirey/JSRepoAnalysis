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

# [START secretmanager_v1beta2_secretmanagerservice_secret_get]
import argparse
import os
import json

from google.cloud import secretmanager_v1beta2
from google.api_core import exceptions

def get_secret_sample(project_id: str, secret_id: str):
    """Gets metadata for a given Secret.

    Args:
        project_id: The ID of the Google Cloud project.
        secret_id: The ID of the secret to retrieve.

    Returns:
        The Secret object if found, None otherwise.
    """
    client = secretmanager_v1beta2.SecretManagerServiceClient()

    # Build the resource name of the secret.
    # The secret name is in the format projects/*/secrets/*
    name = client.secret_path(project_id, secret_id)

    try:
        response = client.get_secret(name=name)
        return response
    except exceptions.NotFound:
        print(f"Secret {name} not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
# [END secretmanager_v1beta2_secretmanagerservice_secret_get]


def main():
    parser = argparse.ArgumentParser(description="Get metadata for a Secret.")
    parser.add_argument(
        "--secret-id",
        required=True,
        help="The ID of the secret to retrieve (e.g., 'my-secret').",
    )

    args = parser.parse_args()

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        print("Error: GCP_PROJECT_ID environment variable not set.")
        print("Please set the GCP_PROJECT_ID environment variable to your Google Cloud project ID.")
        exit(1)

    secret = get_secret_sample(project_id, args.secret_id)

    if secret:
        # Convert the protobuf message to a dictionary for pretty printing
        # and then to a JSON string.
        # The to_dict() method is available on protobuf messages in google-cloud libraries.
        secret_dict = type(secret).to_dict(secret)
        print(json.dumps(secret_dict, indent=2))


if __name__ == "__main__":
    main()
