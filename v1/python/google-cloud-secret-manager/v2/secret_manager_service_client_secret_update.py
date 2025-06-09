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

# [START secretmanager_v1_secretmanagerservice_secret_update]
# This sample demonstrates how to update a Secret Manager secret.
#
# To run this sample, install the Google Cloud Secret Manager client library:
# pip install google-cloud-secret-manager
#
# Set the GCP_PROJECT_ID environment variable to your Google Cloud project ID.

from typing import Optional


def update_secret_sample(
    project_id: str,
    secret_id: str,
    new_labels_file: Optional[str] = None,
    new_replication_policy_file: Optional[str] = None,
) -> "secretmanager_v1.types.Secret":
    """
    Updates the metadata of an existing secret.

    Args:
        project_id (str): The Google Cloud project ID.
        secret_id (str): The ID of the secret to update.
        new_labels_file (Optional[str]): Path to a JSON file containing new labels.
                                         See https://cloud.google.com/secret-manager/docs/reference/rest/v1/projects.secrets#Secret.FIELDS.labels
        new_replication_policy_file (Optional[str]): Path to a JSON file containing
                                                     the new replication policy.
                                                     See https://cloud.google.com/secret-manager/docs/reference/rest/v1/projects.secrets#Replication
    Returns:
        google.cloud.secretmanager_v1.types.Secret: The updated secret.
    """
    # Imports are placed here to satisfy the region tag requirement
    import json
    import os
    import sys

    from google.cloud import secretmanager_v1
    from google.protobuf import field_mask_pb2
    from google.protobuf.json_format import MessageToDict

    def _load_json_from_file(file_path: str) -> dict:
        """Loads a JSON object from the given file path."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, "r") as f:
            return json.load(f)

    client = secretmanager_v1.SecretManagerServiceClient()
    secret_name = f"projects/{project_id}/secrets/{secret_id}"

    updated_secret = secretmanager_v1.types.Secret(name=secret_name)
    update_mask_paths = []

    if new_labels_file:
        try:
            labels_data = _load_json_from_file(new_labels_file)
            if not isinstance(labels_data, dict):
                raise ValueError("Labels file must contain a JSON object.")
            updated_secret.labels = labels_data
            update_mask_paths.append("labels")
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            print(f"Error reading labels file: {e}", file=sys.stderr)
            raise

    if new_replication_policy_file:
        try:
            replication_data = _load_json_from_file(new_replication_policy_file)
            replication_proto = secretmanager_v1.types.Replication()

            if "automatic" in replication_data:
                replication_proto.automatic.CopyFrom(
                    secretmanager_v1.types.Replication.Automatic()
                )
            elif "user_managed" in replication_data:
                user_managed_config = replication_data["user_managed"]
                for replica_data in user_managed_config.get("replicas", []):
                    if "location" not in replica_data:
                        raise ValueError(
                            "Each replica in user_managed replication must have "
                            "a 'location'."
                        )
                    replication_proto.user_managed.replicas.add(
                        location=replica_data["location"]
                    )
            else:
                raise ValueError(
                    "Replication policy must contain either 'automatic' or "
                    "'user_managed' key."
                )

            updated_secret.replication.CopyFrom(replication_proto)
            update_mask_paths.append("replication")
        except (FileNotFoundError, json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Error reading replication policy file: {e}", file=sys.stderr)
            raise

    if not update_mask_paths:
        raise ValueError(
            "No fields specified for update. Provide --new-labels-file or "
            "--new-replication-policy-file."
        )

    # Create the field mask based on what's being updated
    field_mask = field_mask_pb2.FieldMask(paths=update_mask_paths)

    try:
        response = client.update_secret(secret=updated_secret, update_mask=field_mask)
        return response
    except Exception as e:
        print(f"Error updating secret: {e}", file=sys.stderr)
        raise
    finally:
        # In Python, client objects manage their own connections and usually don't
        # require explicit closing.
        pass


# [END secretmanager_v1_secretmanagerservice_secret_update]

def main():
    """
    Main entry point for the script.
    Parses command-line arguments and calls the update_secret_sample function.
    """
    import argparse
    import json
    import os
    import sys

    # Import MessageToDict for main's print statement
    from google.protobuf.json_format import MessageToDict

    parser = argparse.ArgumentParser(
        description="Update a Google Cloud Secret Manager secret."
    )
    parser.add_argument(
        "--secret-id",
        required=True,
        help="The ID of the secret to update (e.g., 'my-secret').",
    )
    parser.add_argument(
        "--new-labels-file",
        help="Path to a JSON file containing new labels for the secret. "
             "Example file content: {'env': 'production', 'owner': 'team-a'}. "
             "See https://cloud.google.com/secret-manager/docs/reference/rest/v1/projects.secrets#Secret.FIELDS.labels",
    )
    parser.add_argument(
        "--new-replication-policy-file",
        help="Path to a JSON file containing the new replication policy for "
             "the secret. Example for automatic replication: {'automatic': {}}. "
             "Example for user-managed replication: "
             "{'user_managed': {'replicas': [{'location': 'us-central1'}, "
             "{'location': 'us-east1'}]}}. "
             "See https://cloud.google.com/secret-manager/docs/reference/rest/v1/projects.secrets#Replication",
    )

    args = parser.parse_args()

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        print("Error: GCP_PROJECT_ID environment variable not set.", file=sys.stderr)
        sys.exit(1)

    if not args.new_labels_file and not args.new_replication_policy_file:
        print(
            "Error: At least one of --new-labels-file or "
            "--new-replication-policy-file must be provided.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        updated_secret = update_secret_sample(
            project_id=project_id,
            secret_id=args.secret_id,
            new_labels_file=args.new_labels_file,
            new_replication_policy_file=args.new_replication_policy_file,
        )
        print(json.dumps(MessageToDict(updated_secret), indent=2))
    except Exception as e:
        print(f"Script execution failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
