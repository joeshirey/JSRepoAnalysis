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

# [START secretmanager_v1beta1_secretmanagerservice_secretversions_list]
import argparse
import os
import json
from google.cloud import secretmanager_v1beta1


def list_secret_versions_sample(project_id: str, secret_id: str):
    """
    Lists all secret versions for a given secret.

    Args:
        project_id: The Google Cloud project ID.
        secret_id: The ID of the secret to list versions for.

    Returns:
        A list of secret version resources.
    """
    client = secretmanager_v1beta1.SecretManagerServiceClient()
    parent = f"projects/{project_id}/secrets/{secret_id}"

    secret_versions = []
    try:
        # List all secret versions.
        # The request parameter expects a dictionary or a request object.
        for version in client.list_secret_versions(request={"parent": parent}):
            secret_versions.append({
                "name": version.name,
                "state": str(version.state.name),
                "create_time": (
                    version.create_time.isoformat()
                    if version.create_time else None
                ),
                "destroy_time": (
                    version.destroy_time.isoformat()
                    if version.destroy_time else None
                ),
            })
    except Exception as e:
        print(f"Error listing secret versions: {e}")
        raise
    finally:
        # In newer versions of google-cloud-secret-manager, the client does
        # not need explicit closing. If using an older version that requires
        # client.close(), uncomment the line below.
        pass

    return secret_versions
# [END secretmanager_v1beta1_secretmanagerservice_secretversions_list]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="List secret versions for a given secret."
    )
    parser.add_argument(
        "--secret-id",
        required=True,
        help="The ID of the secret to list versions for."
    )

    args = parser.parse_args()

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        print("Error: GCP_PROJECT_ID environment variable not set.")
        exit(1)

    try:
        result = list_secret_versions_sample(project_id, args.secret_id)
        # The final result of the successful API call should be printed
        # to the standard output from the main block.
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
