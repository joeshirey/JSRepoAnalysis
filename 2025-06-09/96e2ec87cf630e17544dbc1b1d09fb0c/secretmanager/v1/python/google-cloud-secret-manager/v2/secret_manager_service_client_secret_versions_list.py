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
import argparse
import os
import json
from google.cloud import secretmanager_v1


def list_secret_versions_sample(
    project_id: str,
    secret_id: str
) -> list:
    """Lists all secret versions for a given secret.

    Args:
        project_id: The ID of the GCP project.
        secret_id: The ID of the secret to list versions for.

    Returns:
        A list of dictionaries, each representing a secret version.
    """
    client = secretmanager_v1.SecretManagerServiceClient()
    # Build the resource name of the parent secret.
    # Format: projects/{project_id}/secrets/{secret_id}
    parent = client.secret_path(project_id, secret_id)

    secret_versions_data = []
    try:
        # List all secret versions.
        # The list_secret_versions method returns an iterable pager.
        for version in client.list_secret_versions(request={"parent": parent}):
            version_info = {
                "name": version.name,
                "state": secretmanager_v1.SecretVersion.State(
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
            }
            secret_versions_data.append(version_info)
        return secret_versions_data
    except Exception as e:
        # Re-raising the exception after printing for consistent error
        # handling in main.
        print(
            f"Error listing secret versions for secret '{secret_id}' "
            f"in project '{project_id}': {e}"
        )
        raise
# [END secretmanager_v1_secretmanagerservice_secretversions_list]


def main():
    parser = argparse.ArgumentParser(
        description=(
            "List all secret versions for a given secret in Google Secret Manager."
        )
    )
    parser.add_argument(
        "--project-id",
        type=str,
        help=(
            "Your Google Cloud project ID. "
            "Defaults to the GCP_PROJECT_ID environment variable."
        ),
        default=os.environ.get("GCP_PROJECT_ID"),
    )
    parser.add_argument(
        "--secret-id",
        type=str,
        required=True,
        help="The ID of the secret to list versions for (e.g., 'my-secret').",
    )

    args = parser.parse_args()

    if not args.project_id:
        print(
            "Error: --project-id or GCP_PROJECT_ID environment variable must be set."
        )
        parser.print_help()
        exit(1)

    try:
        versions = list_secret_versions_sample(args.project_id, args.secret_id)
        print(json.dumps(versions, indent=2))
    except Exception:
        # The error is already printed by the sample function, just exit with
        # error code.
        exit(1)


if __name__ == "__main__":
    main()
