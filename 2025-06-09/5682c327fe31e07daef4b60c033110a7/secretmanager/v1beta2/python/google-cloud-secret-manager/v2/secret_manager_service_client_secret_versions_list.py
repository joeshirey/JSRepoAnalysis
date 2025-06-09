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

# [START secretmanager_v1beta2_secretmanagerservice_secretversions_list]
import os
import argparse
import json
from typing import List, Dict, Any

from google.cloud import secretmanager_v1beta2

def list_secret_versions_sample(
    project_id: str, secret_id: str
) -> List[Dict[str, Any]]:
    """Lists all secret versions for a given secret.

    Args:
        project_id: The Google Cloud project ID.
        secret_id: The ID of the secret to list versions for.

    Returns:
        A list of dictionaries, where each dictionary represents a secret version
        with its name, state, creation time, and destroy time.
    """
    client = secretmanager_v1beta2.SecretManagerServiceClient()
    parent = f"projects/{project_id}/secrets/{secret_id}"

    secret_versions_data = []
    try:
        # The list_secret_versions method returns a pager object,
        # which can be iterated.
        for version in client.list_secret_versions(parent=parent):
            secret_versions_data.append({
                "name": version.name,
                "state": version.state.name,
                "create_time": version.create_time.isoformat()
                if version.create_time else None,
                "destroy_time": version.destroy_time.isoformat()
                if version.destroy_time else None,
            })
        return secret_versions_data
    except Exception as e:
        print(f"Error listing secret versions: {e}", file=os.sys.stderr)
        raise  # Re-raise to be caught by main's try/except
# [END secretmanager_v1beta2_secretmanagerservice_secretversions_list]


def main():
    parser = argparse.ArgumentParser(
        description="List secret versions for a Google Cloud Secret Manager "
        "secret."
    )
    parser.add_argument(
        "--secret-id",
        type=str,
        required=True,
        help="The ID of the secret to list versions for."
    )
    args = parser.parse_args()

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        print(
            "Error: GCP_PROJECT_ID environment variable not set.",
            file=os.sys.stderr
        )
        os._exit(1)

    try:
        versions = list_secret_versions_sample(project_id, args.secret_id)
        print(json.dumps(versions, indent=2))
    except Exception:
        # The sample function already prints the error, just exit
        os._exit(1)


if __name__ == "__main__":
    main()
