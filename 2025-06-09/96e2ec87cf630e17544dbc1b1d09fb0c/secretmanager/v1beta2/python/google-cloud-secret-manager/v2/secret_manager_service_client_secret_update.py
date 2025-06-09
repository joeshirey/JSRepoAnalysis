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

# [START secretmanager_v1beta2_secretmanagerservice_secret_update]
import argparse
import json
import os
from typing import Optional

from google.cloud import secretmanager_v1beta2
from google.cloud.secretmanager_v1beta2.types import Secret
from google.protobuf import field_mask_pb2
from google.protobuf import duration_pb2


def update_secret_sample(
    project_id: str,
    secret_id: str,
    new_labels_file: Optional[str] = None,
    new_annotations_file: Optional[str] = None,
    new_rotation_period_seconds: Optional[int] = None,
    new_ttl_seconds: Optional[int] = None,
) -> Optional[Secret]:
    """Updates metadata of an existing Secret.

    Args:
        project_id: The Google Cloud project ID.
        secret_id: The ID of the secret to update.
        new_labels_file: Optional path to a JSON file containing new labels.
            See https://cloud.google.com/secret-manager/docs/reference/rest/v1beta2/projects.secrets#Secret
            for expected format of 'labels' field.
        new_annotations_file: Optional path to a JSON file containing new
            annotations.
            See https://cloud.google.com/secret-manager/docs/reference/rest/v1beta2/projects.secrets#Secret
            for expected format of 'annotations' field.
        new_rotation_period_seconds: Optional new rotation period in seconds.
        new_ttl_seconds: Optional new TTL (Time-To-Live) for the secret in
            seconds.
    Returns:
        The updated Secret object, or None if no fields were specified for
        update.
    """
    # Create the Secret Manager client.
    client = secretmanager_v1beta2.SecretManagerServiceClient()

    # Build the secret name.
    secret_name = client.secret_path(project_id, secret_id)

    # Create a Secret object to hold the updated values. Its 'name' field
    # is required.
    updated_secret = Secret(name=secret_name)

    # Create a FieldMask to specify which fields are being updated.
    update_mask = field_mask_pb2.FieldMask()

    # Handle new labels from file.
    if new_labels_file:
        try:
            with open(new_labels_file, "r") as f:
                new_labels = json.load(f)
            if not isinstance(new_labels, dict) or not all(
                isinstance(k, str) and isinstance(v, str) for k, v in new_labels.items()
            ):
                raise ValueError(
                    "Labels file must contain a JSON object with string keys "
                    "and string values."
                )
            updated_secret.labels = new_labels
            update_mask.paths.append("labels")
        except FileNotFoundError:
            print(f"Error: Labels file not found at {new_labels_file}")
            raise
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in labels file at {new_labels_file}")
            raise
        except ValueError as e:
            print(f"Error processing labels file: {e}")
            raise

    # Handle new annotations from file.
    if new_annotations_file:
        try:
            with open(new_annotations_file, "r") as f:
                new_annotations = json.load(f)
            if not isinstance(new_annotations, dict) or not all(
                isinstance(k, str) and isinstance(v, str)
                for k, v in new_annotations.items()
            ):
                raise ValueError(
                    "Annotations file must contain a JSON object with string "
                    "keys and string values."
                )
            updated_secret.annotations = new_annotations
            update_mask.paths.append("annotations")
        except FileNotFoundError:
            print(f"Error: Annotations file not found at {new_annotations_file}")
            raise
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in annotations file at {new_annotations_file}")
            raise
        except ValueError as e:
            print(f"Error processing annotations file: {e}")
            raise

    # Handle new rotation period.
    if new_rotation_period_seconds is not None:
        # Ensure the rotation object exists before setting its period.
        if updated_secret.rotation is None:
            updated_secret.rotation = secretmanager_v1beta2.types.Rotation()
        updated_secret.rotation.rotation_period = duration_pb2.Duration(
            seconds=new_rotation_period_seconds
        )
        # Specify the full path to the field being updated.
        update_mask.paths.append("rotation.rotation_period")

    # Handle new TTL.
    if new_ttl_seconds is not None:
        updated_secret.ttl = duration_pb2.Duration(seconds=new_ttl_seconds)
        # For oneof fields (like 'expiration' which contains 'ttl'),
        # the path in the update mask should be the oneof field name itself.
        update_mask.paths.append("expiration")

    if not update_mask.paths:
        print("No fields specified for update. "
              "Please provide at least one field to update.")
        return None

    try:
        # Call the API to update the secret.
        response = client.update_secret(secret=updated_secret, update_mask=update_mask)
        print(f"Successfully updated secret: {response.name}")
        return response
    except Exception as e:
        print(f"Error updating secret: {e}")
        raise
# [END secretmanager_v1beta2_secretmanagerservice_secret_update]


def main():
    parser = argparse.ArgumentParser(
        description="Update a Secret Manager secret's metadata."
    )
    parser.add_argument(
        "--project-id",
        type=str,
        default=os.environ.get("GCP_PROJECT_ID"),
        help="Your Google Cloud project ID. "
             "Defaults to GCP_PROJECT_ID environment variable.",
    )
    parser.add_argument(
        "--secret-id",
        type=str,
        required=True,
        help="The ID of the secret to update.",
    )
    parser.add_argument(
        "--new-labels-file",
        type=str,
        help="Path to a JSON file containing new labels for the secret. "
             "Example: {'key1': 'value1', 'key2': 'value2'}. "
             "See https://cloud.google.com/secret-manager/docs/reference/rest/v1beta2/projects.secrets#Secret "
             "for format.",
    )
    parser.add_argument(
        "--new-annotations-file",
        type=str,
        help="Path to a JSON file containing new annotations for the secret. "
             "Example: {'key1': 'value1', 'key2': 'value2'}. "
             "See https://cloud.google.com/secret-manager/docs/reference/rest/v1beta2/projects.secrets#Secret "
             "for format.",
    )
    parser.add_argument(
        "--new-rotation-period-seconds",
        type=int,
        help="New rotation period for the secret in seconds. "
             "Must be at least 3600 (1 hour).",
    )
    parser.add_argument(
        "--new-ttl-seconds",
        type=int,
        help="New TTL (Time-To-Live) for the secret in seconds. "
             "If set, the secret will expire after this duration.",
    )

    args = parser.parse_args()

    if not args.project_id:
        print("Error: --project-id is required or set "
              "GCP_PROJECT_ID environment variable.")
        exit(1)

    # Check if at least one update argument is provided
    if not any([args.new_labels_file, args.new_annotations_file,
                args.new_rotation_period_seconds, args.new_ttl_seconds]):
        print("Error: At least one update argument (--new-labels-file, "
              "--new-annotations-file, --new-rotation-period-seconds, "
              "or --new-ttl-seconds) must be provided.")
        parser.print_help()
        exit(1)

    try:
        updated_secret = update_secret_sample(
            project_id=args.project_id,
            secret_id=args.secret_id,
            new_labels_file=args.new_labels_file,
            new_annotations_file=args.new_annotations_file,
            new_rotation_period_seconds=args.new_rotation_period_seconds,
            new_ttl_seconds=args.new_ttl_seconds,
        )
        if updated_secret:
            # Print the updated secret details in a structured format.
            from google.protobuf.json_format import MessageToDict
            print(json.dumps(MessageToDict(updated_secret), indent=2))
    except Exception as e:
        print(f"Script execution failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()