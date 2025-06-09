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


# // [START secretmanager_v1beta2_secretmanagerservice_secretversions_list]
def list_secret_versions(project_id: str, secret_id: str) -> list:
    """
    Lists all secret versions for a given secret.

    Args:
        project_id: The ID of the Google Cloud project.
        secret_id: The ID of the secret to list versions for.

    Returns:
        A list of SecretVersion objects.
    """
    client = secretmanager_v1beta2.SecretManagerServiceClient()
    parent = client.secret_path(project_id, secret_id)

    secret_versions = []
    try:
        # The list_secret_versions method returns a pager, which is iterable.
        for version in client.list_secret_versions(parent=parent):
            secret_versions.append(version)
        return secret_versions
    except exceptions.NotFound:
        print(
            f"Error: Secret '{secret_id}' not found in project '{project_id}'. "
            "Please ensure the secret exists and you have the necessary "
            "permissions.",
            file=os.sys.stderr,
        )
        return []
    except exceptions.PermissionDenied:
        print(
            f"Error: Permission denied to access secret '{secret_id}' in "
            f"project '{project_id}'. Please check your IAM permissions.",
            file=os.sys.stderr,
        )
        return []
    except exceptions.GoogleAPICallError as e:
        print(f"An API error occurred: {e}", file=os.sys.stderr)
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=os.sys.stderr)
        return []
# // [END secretmanager_v1beta2_secretmanagerservice_secretversions_list]


def main():
    parser = argparse.ArgumentParser(
        description="List secret versions in Google Secret Manager."
    )
    parser.add_argument(
        "--secret-id",
        type=str,
        required=True,
        help="The ID of the secret to list versions for. E.g., 'my-secret-name'",
    )

    args = parser.parse_args()

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        print(
            "Error: GCP_PROJECT_ID environment variable not set. "
            "Please set it to your Google Cloud project ID.",
            file=os.sys.stderr,
        )
        os._exit(1)

    versions = list_secret_versions(project_id, args.secret_id)

    # Convert SecretVersion objects to a serializable format for JSON output
    serializable_versions = []
    for version in versions:
        serializable_versions.append(
            {
                "name": version.name,
                "state": secretmanager_v1beta2.SecretVersion.State(
                    version.state
                ).name,
                "create_time": (
                    version.create_time.isoformat()
                    if version.create_time
                    else None
                ),
                "destroy_time": (
                    version.destroy_time.isoformat()
                    if version.destroy_time
                    else None
                ),
                "etag": version.etag,
                "client_managed": version.client_managed,
            }
        )

    # Print the result as JSON
    print(json.dumps(serializable_versions, indent=2))


if __name__ == "__main__":
    main()
