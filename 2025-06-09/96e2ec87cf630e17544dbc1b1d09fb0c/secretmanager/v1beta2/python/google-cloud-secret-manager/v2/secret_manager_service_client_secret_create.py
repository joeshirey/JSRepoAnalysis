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

# // [START secretmanager_v1beta2_secretmanagerservice_secret_create]
def create_secret_sample(
    project_id: str, secret_id: str
) -> "google.cloud.secretmanager_v1beta2.Secret":
    """
    Creates a new secret in Google Cloud Secret Manager.

    Args:
        project_id: The Google Cloud project ID.
        secret_id: The ID to assign to the new secret.

    Returns:
        The created Secret object.
    """
    # Imports for the sample function are placed here to strictly satisfy the
    # "before any imports" rule for the START tag.
    from google.cloud import secretmanager_v1beta2
    import os
    import sys

    client = secretmanager_v1beta2.SecretManagerServiceClient()
    parent = f"projects/{project_id}"

    # Build the secret object.
    # For more information on the Secret resource:
    # https://cloud.google.com/secret-manager/docs/reference/rest/v1beta2/projects.secrets#Secret
    secret = secretmanager_v1beta2.Secret(
        replication=secretmanager_v1beta2.Replication(
            automatic=secretmanager_v1beta2.Replication.Automatic()
        )
    )

    try:
        created_secret = client.create_secret(
            parent=parent,
            secret_id=secret_id,
            secret=secret,
        )
        return created_secret
    except Exception as e:
        print(f"Error creating secret: {e}", file=sys.stderr)
        raise
# // [END secretmanager_v1beta2_secretmanagerservice_secret_create]


import argparse
import json
import os
import sys
from google.protobuf.json_format import MessageToDict


def main():
    """
    Main entry point for the script.
    Parses command-line arguments and calls the create_secret_sample function.
    """
    parser = argparse.ArgumentParser(
        description="Create a new secret in Google Cloud Secret Manager."
    )
    parser.add_argument(
        "--secret-id",
        type=str,
        required=True,
        help="The ID to assign to the new secret (e.g., 'my-new-secret').",
    )

    args = parser.parse_args()

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        print(
            "Error: GCP_PROJECT_ID environment variable not set.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        secret = create_secret_sample(project_id, args.secret_id)
        # Convert the protobuf message to a dictionary for JSON output
        result_dict = MessageToDict(
            secret._pb, preserving_proto_field_names=True
        )
        print(json.dumps(result_dict, indent=2))
    except Exception:
        # Error already printed by the sample function, just exit with non-zero code.
        sys.exit(1)


if __name__ == "__main__":
    main()
