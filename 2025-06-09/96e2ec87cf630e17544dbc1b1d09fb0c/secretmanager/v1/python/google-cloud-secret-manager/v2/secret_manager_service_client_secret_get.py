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

# [START secretmanager_v1_secretmanagerservice_secret_get]
import argparse
import os
import json
from google.cloud import secretmanager_v1
from google.api_core import exceptions
from google.protobuf.json_format import MessageToDict

def get_secret_sample(project_id: str, secret_id: str):
    """Gets metadata for a given Secret.

    Args:
        project_id: The Google Cloud project ID.
        secret_id: The ID of the secret to retrieve.

    Returns:
        The Secret object if found, None otherwise.
    """
    client = secretmanager_v1.SecretManagerServiceClient()

    # Build the resource name of the secret.
    # Format: projects/{project_id}/secrets/{secret_id}
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
# [END secretmanager_v1_secretmanagerservice_secret_get]

def main():
    """
    To run this sample:
    1. Install the Google Cloud Secret Manager client library:
       pip install google-cloud-secret-manager
    2. Authenticate to Google Cloud:
       gcloud auth application-default login
    3. Set the GCP_PROJECT_ID environment variable:
       export GCP_PROJECT_ID="your-gcp-project-id"
    4. Run the script with the required command-line arguments:
       python get_secret.py --secret_id my-secret-id
    """
    parser = argparse.ArgumentParser(
        description="Get a secret from Google Cloud Secret Manager."
    )
    parser.add_argument(
        "--secret_id",
        required=True,
        help="The ID of the secret to retrieve (e.g., 'my-secret')."
    )

    args = parser.parse_args()

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        raise ValueError(
            "The GCP_PROJECT_ID environment variable must be set. "
            "Please set it to your Google Cloud project ID."
        )

    secret = get_secret_sample(project_id, args.secret_id)
    if secret:
        # Print the secret metadata as JSON
        # MessageToDict converts the protobuf message to a Python dictionary,
        # which can then be serialized to JSON.
        print(json.dumps(MessageToDict(secret), indent=2))

if __name__ == "__main__":
    main()
