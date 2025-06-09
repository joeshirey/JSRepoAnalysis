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

# [START secretmanager_v1_secretmanagerservice_secretversions_list]
import os
import argparse
import json
import sys
from google.cloud import secretmanager_v1
from google.api_core import exceptions


def list_secret_versions(project_id: str, secret_id: str):
    """
    Lists all secret versions for a given secret.

    Args:
        project_id: The Google Cloud project ID.
        secret_id: The ID of the secret whose versions are to be listed.

    Returns:
        A list of dictionaries, each representing a secret version.
    """
    client = secretmanager_v1.SecretManagerServiceClient()
    parent = client.secret_path(project_id, secret_id)

    versions_list = []
    try:
        # Construct the request
        request = secretmanager_v1.ListSecretVersionsRequest(
            parent=parent,
        )

        # Make the request and iterate through the pages
        page_result = client.list_secret_versions(request=request)

        for version in page_result:
            versions_list.append({
                "name": version.name,
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
                "state": secretmanager_v1.SecretVersion.State(
                    version.state
                ).name,
            })
        return versions_list
    except exceptions.GoogleAPIError as e:
        print(f"Error listing secret versions: {e}", file=sys.stderr)
        raise
# [END secretmanager_v1_secretmanagerservice_secretversions_list]


def main():
    parser = argparse.ArgumentParser(
        description="List secret versions for a given secret."
    )
    parser.add_argument(
        "--project-id",
        type=str,
        help=(
            "Your Google Cloud project ID. Defaults to GCP_PROJECT_ID "
            "environment variable."
        ),
        default=os.environ.get("GCP_PROJECT_ID"),
    )
    parser.add_argument(
        "--secret-id",
        type=str,
        required=True,
        help="The ID of the secret whose versions are to be listed.",
    )

    args = parser.parse_args()

    if not args.project_id:
        print(
            "Error: --project-id or GCP_PROJECT_ID environment variable "
            "must be set.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        versions = list_secret_versions(args.project_id, args.secret_id)
        print(json.dumps(versions, indent=2))
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
