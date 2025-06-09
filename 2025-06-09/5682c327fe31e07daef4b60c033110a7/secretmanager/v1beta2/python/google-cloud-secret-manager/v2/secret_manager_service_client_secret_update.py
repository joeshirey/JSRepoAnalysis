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

#!/usr/bin/env python3

# [START secretmanager_v1beta2_secretmanagerservice_secret_update]
import argparse
import json
import os
import sys

from google.cloud import secretmanager_v1beta2
from google.cloud.secretmanager_v1beta2.types import Secret
from google.protobuf import field_mask_pb2


def update_secret_sample(
    project_id: str,
    secret_id: str,
    new_labels_file: str = None,
    new_annotations_file: str = None,
) -> Secret:
    """Updates the metadata of an existing secret.

    Args:
        project_id (str): Your Google Cloud project ID.
        secret_id (str): The ID of the secret to update.
        new_labels_file (str, optional): Path to a JSON file containing new labels
            for the secret. The JSON should be a dictionary like:
            `{"key1": "value1", "key2": "value2"}`.
            See:
            https://cloud.google.com/secret-manager/docs/reference/rest/v1beta2/projects.secrets#Secret
        new_annotations_file (str, optional): Path to a JSON file containing new
            annotations for the secret. The JSON should be a dictionary like:
            `{"key1": "value1", "key2": "value2"}`.
            See:
            https://cloud.google.com/secret-manager/docs/reference/rest/v1beta2/projects.secrets#Secret

    Returns:
        google.cloud.secretmanager_v1beta2.types.Secret: The updated secret resource.
    """
    client = secretmanager_v1beta2.SecretManagerServiceClient()

    # Build the resource name of the secret.
    name = client.secret_path(project_id, secret_id)

    updated_secret = Secret(name=name)
    update_mask = field_mask_pb2.FieldMask()

    if new_labels_file:
        try:
            with open(new_labels_file, "r") as f:
                new_labels = json.load(f)
            if not isinstance(new_labels, dict):
                raise ValueError(
                    "Labels file must contain a JSON object (dictionary)."
                )
            updated_secret.labels = new_labels
            update_mask.paths.append("labels")
        except FileNotFoundError:
            print(
                f"Error: Labels file not found at {new_labels_file}",
                file=sys.stderr,
            )
            raise
        except json.JSONDecodeError:
            print(
                f"Error: Invalid JSON in labels file {new_labels_file}",
                file=sys.stderr,
            )
            raise
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            raise

    if new_annotations_file:
        try:
            with open(new_annotations_file, "r") as f:
                new_annotations = json.load(f)
            if not isinstance(new_annotations, dict):
                raise ValueError(
                    "Annotations file must contain a JSON object (dictionary)."
                )
            updated_secret.annotations = new_annotations
            update_mask.paths.append("annotations")
        except FileNotFoundError:
            print(
                f"Error: Annotations file not found at {new_annotations_file}",
                file=sys.stderr,
            )
            raise
        except json.JSONDecodeError:
            print(
                f"Error: Invalid JSON in annotations file {new_annotations_file}",
                file=sys.stderr,
            )
            raise
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            raise

    if not update_mask.paths:
        raise ValueError(
            "No fields specified for update. Provide --new_labels_file or "
            "--new_annotations_file."
        )

    try:
        # Call the API to update the secret.
        response = client.update_secret(
            secret=updated_secret, update_mask=update_mask
        )
        return response
    except Exception as e:
        print(f"Error updating secret: {e}", file=sys.stderr)
        raise
    finally:
        # The client should be closed when it's no longer needed.
        # This ensures all underlying connections are properly shut down.
        client.close()
# [END secretmanager_v1beta2_secretmanagerservice_secret_update]


def main():
    parser = argparse.ArgumentParser(
        description="Update a Google Cloud Secret Manager secret."
    )
    parser.add_argument(
        "--project_id",
        type=str,
        default=os.environ.get("GCP_PROJECT_ID"),
        help="Your Google Cloud project ID. Defaults to the GCP_PROJECT_ID "
        "environment variable.",
    )
    parser.add_argument(
        "--secret_id",
        type=str,
        required=True,
        help="The ID of the secret to update (e.g., 'my-secret').",
    )
    parser.add_argument(
        "--new_labels_file",
        type=str,
        help="Path to a JSON file containing new labels for the secret. "
        "Example file content: `{'environment': 'production', 'owner': 'devops'}`. "
        "See: https://cloud.google.com/secret-manager/docs/reference/rest/v1beta2/projects.secrets#Secret",
    )
    parser.add_argument(
        "--new_annotations_file",
        type=str,
        help="Path to a JSON file containing new annotations for the secret. "
        "Example file content: `{'deployment_tool': 'ansible', "
        "'last_updated_by': 'admin'}`. "
        "See: https://cloud.google.com/secret-manager/docs/reference/rest/v1beta2/projects.secrets#Secret",
    )

    args = parser.parse_args()

    if not args.project_id:
        print(
            "Error: --project_id or GCP_PROJECT_ID environment variable "
            "must be set.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        updated_secret = update_secret_sample(
            project_id=args.project_id,
            secret_id=args.secret_id,
            new_labels_file=args.new_labels_file,
            new_annotations_file=args.new_annotations_file,
        )
        print(
            json.dumps(
                {
                    "name": updated_secret.name,
                    "labels": dict(updated_secret.labels),
                    "annotations": dict(updated_secret.annotations),
                    "create_time": (
                        updated_secret.create_time.isoformat()
                        if updated_secret.create_time
                        else None
                    ),
                    "etag": updated_secret.etag,
                },
                indent=2,
            )
        )
    except Exception as e:
        print(f"Failed to update secret: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
