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


# // [START secretmanager_v1_secretmanagerservice_secret_create]
def create_secret_sample(
    project_id: str, secret_id: str, labels: dict = None
) -> secretmanager_v1.Secret:
    """
    Creates a new secret in Google Secret Manager.

    Args:
        project_id: The ID of the Google Cloud project.
        secret_id: The ID to assign to the new secret.
        labels: Optional. A dictionary of labels to apply to the secret.
                See https://cloud.google.com/secret-manager/docs/reference/rest/v1/
                projects.secrets#Secret.FIELDS.labels for expected format.

    Returns:
        google.cloud.secretmanager_v1.Secret: The created secret.

    Raises:
        google.api_core.exceptions.GoogleAPIError: If the API call fails.
    """
    client = secretmanager_v1.SecretManagerServiceClient()
    parent = f"projects/{project_id}"

    # Create a Secret object. Labels are optional.
    secret = secretmanager_v1.Secret(labels=labels)

    # Create the CreateSecretRequest object.
    request = secretmanager_v1.CreateSecretRequest(
        parent=parent,
        secret_id=secret_id,
        secret=secret,
    )

    try:
        # Make the API call to create the secret.
        response = client.create_secret(request=request)
        return response
    except exceptions.GoogleAPIError as e:
        print(f"Error creating secret: {e}")
        raise
    finally:
        # Explicitly close the client, as it holds network connections.
        client.close()
# // [END secretmanager_v1_secretmanagerservice_secret_create]


def main():
    parser = argparse.ArgumentParser(
        description="Create a new secret in Google Secret Manager."
    )
    parser.add_argument(
        "--secret-id",
        type=str,
        required=True,
        help="The ID to assign to the new secret.",
    )
    parser.add_argument(
        "--labels-file",
        type=str,
        help=(
            "Optional. Path to a JSON file containing labels for the secret. "
            "Example: `{'environment': 'dev', 'owner': 'team-a'}`. "
            "See https://cloud.google.com/secret-manager/docs/reference/rest/v1/"
            "projects.secrets#Secret.FIELDS.labels for expected format."
        ),
    )

    args = parser.parse_args()

    # Retrieve GCP_PROJECT_ID from environment variables.
    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        raise ValueError("Environment variable GCP_PROJECT_ID must be set.")

    labels = None
    if args.labels_file:
        try:
            with open(args.labels_file, 'r') as f:
                labels = json.load(f)
            if not isinstance(labels, dict):
                raise ValueError(
                    "Labels file must contain a JSON object (dictionary)."
                )
        except FileNotFoundError:
            print(f"Error: Labels file not found at {args.labels_file}")
            exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in labels file {args.labels_file}")
            exit(1)
        except Exception as e:
            print(
                f"An unexpected error occurred while reading labels file: {e}"
            )
            exit(1)

    try:
        created_secret = create_secret_sample(
            project_id=project_id,
            secret_id=args.secret_id,
            labels=labels
        )
        # Print the result of the API call in JSON format.
        # The 'name' field is the full resource name (e.g.,
        # projects/my-project/secrets/my-secret-id).
        print(json.dumps({
            "secret_name": created_secret.name,
            "secret_id": created_secret.secret_id,
            "labels": dict(created_secret.labels) if created_secret.labels else {}
        }))
    except Exception as e:
        print(f"Failed to create secret: {e}")
        exit(1)


if __name__ == "__main__":
    main()
