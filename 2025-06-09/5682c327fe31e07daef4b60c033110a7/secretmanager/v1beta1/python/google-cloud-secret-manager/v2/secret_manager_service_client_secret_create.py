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

# [START secretmanager_v1beta1_secretmanagerservice_secret_create]
import argparse
import json
import os
import sys

from google.cloud import secretmanager_v1beta1
from google.api_core.exceptions import GoogleAPICallError


def create_secret_sample(
    project_id: str, secret_id: str, labels_file_path: str = None
):
    """Creates a new secret in Google Cloud Secret Manager.

    Args:
        project_id: The Google Cloud project ID.
        secret_id: The ID to assign to the new secret.
        labels_file_path: Optional. Path to a JSON file containing labels for
                          the secret. The file should contain a JSON object
                          where keys and values are strings.
                          Example: `{"environment": "dev", "owner": "team-a"}`
                          See: https://cloud.google.com/secret-manager/docs/reference/rest/v1/projects.secrets#Secret

    Returns:
        google.cloud.secretmanager_v1beta1.types.Secret: The created secret.
    """
    client = secretmanager_v1beta1.SecretManagerServiceClient()
    parent = f"projects/{project_id}"

    secret_labels = {}
    if labels_file_path:
        try:
            with open(labels_file_path, "r") as f:
                secret_labels = json.load(f)
            if not isinstance(secret_labels, dict) or not all(
                isinstance(k, str) and isinstance(v, str)
                for k, v in secret_labels.items()
            ):
                raise ValueError(
                    "Labels file must contain a JSON object with string keys "
                    "and string values."
                )
        except FileNotFoundError:
            print(
                f"Error: Labels file not found at {labels_file_path}",
                file=sys.stderr,
            )
            raise
        except json.JSONDecodeError:
            print(
                f"Error: Invalid JSON in labels file at {labels_file_path}",
                file=sys.stderr,
            )
            raise
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            raise

    # Create a Secret object with automatic replication
    secret = secretmanager_v1beta1.types.Secret(
        replication=secretmanager_v1beta1.types.Replication(
            automatic=secretmanager_v1beta1.types.Replication.Automatic()
        ),
        labels=secret_labels,
    )

    try:
        # Create the secret request
        request = secretmanager_v1beta1.types.CreateSecretRequest(
            parent=parent,
            secret_id=secret_id,
            secret=secret,
        )

        # Make the API call
        created_secret = client.create_secret(request=request)
        return created_secret
    except GoogleAPICallError as e:
        print(f"Error creating secret: {e}", file=sys.stderr)
        raise
# [END secretmanager_v1beta1_secretmanagerservice_secret_create]


def main():
    parser = argparse.ArgumentParser(
        description="Create a Google Cloud Secret Manager secret."
    )
    parser.add_argument(
        "--secret-id",
        required=True,
        help="The ID to assign to the new secret.",
    )
    parser.add_argument(
        "--labels-file-path",
        required=False,
        help="Optional. Path to a JSON file containing labels for the secret. "
        "The file should contain a JSON object with string keys and string "
        "values. See: https://cloud.google.com/secret-manager/docs/reference/"
        "rest/v1/projects.secrets#Secret",
    )

    args = parser.parse_args()

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        print("Error: GCP_PROJECT_ID environment variable not set.", file=sys.stderr)
        sys.exit(1)

    try:
        result = create_secret_sample(
            project_id=project_id,
            secret_id=args.secret_id,
            labels_file_path=args.labels_file_path,
        )
        # Print the result in a structured format (e.g., JSON)
        # Convert protobuf timestamp to ISO format string
        create_time_iso = (
            result.create_time.isoformat() if result.create_time else None
        )

        # Ensure labels are a plain dict for JSON serialization
        labels_dict = dict(result.labels) if result.labels else {}

        print(
            json.dumps(
                {
                    "name": result.name,
                    "project_id": project_id,
                    "secret_id": args.secret_id,
                    "replication": "automatic",  # Based on sample's replication setting
                    "labels": labels_dict,
                    "create_time": create_time_iso,
                },
                indent=2,
            )
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
