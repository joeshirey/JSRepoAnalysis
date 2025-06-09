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

from google.cloud import secretmanager_v1
from google.api_core import exceptions

# [START secretmanager_v1_secretmanagerservice_secrets_list]

def list_secrets_sample(project_id: str):
    """
    Lists all secrets within a given Google Cloud project.

    Args:
        project_id: The ID of the Google Cloud project.
    """
    client = secretmanager_v1.SecretManagerServiceClient()
    # The client will automatically be closed when the function exits or
    # an error occurs. For longer-lived applications, consider re-using
    # the client instance.

    # Build the parent resource name
    parent = f"projects/{project_id}"

    try:
        # List all secrets
        secrets_data = []
        for secret in client.list_secrets(request={"parent": parent}):
            replication_info = {}
            if secret.replication.automatic:
                replication_info["automatic"] = True
            elif secret.replication.user_managed:
                replication_info["user_managed"] = [
                    {
                        "replica": {
                            "location": r.location,
                            "customer_managed_encryption": {
                                "kms_key_name": (
                                    r.customer_managed_encryption.kms_key_name
                                )
                            } if r.customer_managed_encryption else None
                        }
                    } for r in secret.replication.user_managed.replicas
                ]

            secrets_data.append({
                "name": secret.name,
                "create_time": (
                    secret.create_time.isoformat() if secret.create_time else None
                ),
                "labels": dict(secret.labels),
                "replication": replication_info,
            })
        print(json.dumps(secrets_data, indent=2))
    except exceptions.GoogleAPIError as e:
        print(f"Error listing secrets: {e}")
        raise
    finally:
        client.close()
# [END secretmanager_v1_secretmanagerservice_secrets_list]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="List secrets in a Google Cloud project."
    )
    parser.add_argument(
        "--project-id",
        type=str,
        default=os.environ.get("GCP_PROJECT_ID"),
        help="Your Google Cloud project ID. Defaults to GCP_PROJECT_ID "
             "environment variable.",
    )

    args = parser.parse_args()

    if not args.project_id:
        raise ValueError(
            "Project ID must be provided via --project-id or "
            "GCP_PROJECT_ID environment variable."
        )

    try:
        list_secrets_sample(args.project_id)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
