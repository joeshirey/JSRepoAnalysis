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

// [START secretmanager_v1beta1_secretmanagerservice_secret_create]
def create_secret_sample(project_id: str, secret_id: str, labels: dict = None):
    """
    Creates a new secret in Google Secret Manager.

    Args:
        project_id: The Google Cloud project ID.
        secret_id: The ID to assign to the new secret.
        labels: Optional dictionary of labels to apply to the secret.
                See https://cloud.google.com/secret-manager/docs/reference/rest/v1beta1/projects.secrets#Secret
                for expected format.

    Returns:
        google.cloud.secretmanager_v1beta1.types.Secret: The created secret.
    """
    client = secretmanager_v1beta1.SecretManagerServiceClient()
    parent = f"projects/{project_id}"

    # Define the replication policy. Automatic replication is used here.
    # For user-managed replication, you would define replicas:
    # replication_policy = secretmanager_v1beta1.types.Replication(
    #     user_managed=secretmanager_v1beta1.types.Replication.UserManaged(
    #         replicas=[
    #             secretmanager_v1beta1.types.Replication.UserManaged.Replica(location="us-east1"),
    #             secretmanager_v1beta1.types.Replication.UserManaged.Replica(location="us-west1"),
    #         ]
    #     )
    # )
    replication_policy = secretmanager_v1beta1.types.Replication(
        automatic=secretmanager_v1beta1.types.Replication.Automatic()
    )

    secret = secretmanager_v1beta1.types.Secret(
        replication=replication_policy,
        labels=labels
    )

    try:
        created_secret = client.create_secret(
            parent=parent,
            secret_id=secret_id,
            secret=secret
        )
        return created_secret
    except Exception as e:
        print(f"Error creating secret: {e}", file=sys.stderr)
        raise
# // [END secretmanager_v1beta1_secretmanagerservice_secret_create]


import argparse
import json
import os
import sys

from google.cloud import secretmanager_v1beta1
from google.protobuf import json_format


def main():
    parser = argparse.ArgumentParser(
        description="Create a secret in Google Secret Manager."
    )
    parser.add_argument(
        "--secret-id",
        required=True,
        help="The ID to assign to the new secret."
    )
    parser.add_argument(
        "--secret-labels-file",
        required=False,
        help=(
            "Path to a JSON file containing labels for the secret. "
            "Example: {'env': 'dev', 'owner': 'team-a'}. "
            "See https://cloud.google.com/secret-manager/docs/reference/rest/v1beta1/projects.secrets#Secret "
            "for format."
        ),
    )

    args = parser.parse_args()

    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        print("Error: GCP_PROJECT_ID environment variable not set.", file=sys.stderr)
        sys.exit(1)

    labels = None
    if args.secret_labels_file:
        try:
            with open(args.secret_labels_file, "r") as f:
                labels = json.load(f)
            if not isinstance(labels, dict):
                raise ValueError("Labels file must contain a JSON object.")
        except FileNotFoundError:
            print(
                f"Error: Labels file not found at {args.secret_labels_file}",
                file=sys.stderr,
            )
            sys.exit(1)
        except json.JSONDecodeError:
            print(
                f"Error: Invalid JSON in labels file {args.secret_labels_file}",
                file=sys.stderr,
            )
            sys.exit(1)
        except ValueError as e:
            print(f"Error processing labels file: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        secret = create_secret_sample(project_id, args.secret_id, labels)
        # Convert the protobuf message to a dictionary for JSON output
        secret_dict = json_format.MessageToDict(secret)
        print(json.dumps(secret_dict, indent=2))
    except Exception:
        # Error message already printed by create_secret_sample or earlier validation
        sys.exit(1)


if __name__ == "__main__":
    main()
