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

from google.cloud import secretmanager_v1beta2
from google.cloud.secretmanager_v1beta2 import services
from google.api_core import exceptions


# [START secretmanager_v1beta2_secretmanagerservice_secretversion_get]
def get_secret_version_sample(
    project_id: str, secret_id: str, version_id: str
) -> secretmanager_v1beta2.resources.SecretVersion | None:
    """Gets metadata for a specific Secret Version.

    Args:
        project_id: The ID of the Google Cloud project.
                    (Sourced from GCP_PROJECT_ID environment variable in main).
        secret_id: The ID of the secret.
        version_id: The version of the secret (e.g., '1', 'latest').

    Returns:
        A SecretVersion object if successful, None otherwise.
    """
    # Initialize the client using a 'with' statement for proper resource
    # management.
    with secretmanager_v1beta2.SecretManagerServiceClient() as client:
        # Build the resource name of the secret version.
        # The format is projects/{project_id}/secrets/{secret_id}/versions/
        # {version_id}
        name = client.secret_version_path(project_id, secret_id, version_id)

        # Create the request object.
        request = services.secret_manager_service.GetSecretVersionRequest(
            name=name
        )

        try:
            # Access the secret version.
            response = client.get_secret_version(request=request)
            return response
        except exceptions.NotFound:
            print(f"Error: Secret version '{name}' not found.")
            return None
        except exceptions.PermissionDenied:
            print(f"Error: Permission denied to access secret version "
                  f"'{name}'.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
# [END secretmanager_v1beta2_secretmanagerservice_secretversion_get]


def main():
    """
    Main entry point for the script.
    Parses command-line arguments, retrieves environment variables,
    calls the sample function, and prints the result.
    """
    parser = argparse.ArgumentParser(
        description="Get metadata for a Secret Version."
    )
    parser.add_argument(
        "--secret-id",
        type=str,
        required=True,
        help="The ID of the secret (e.g., 'my-secret').",
    )
    parser.add_argument(
        "--version-id",
        type=str,
        required=True,
        help="The version of the secret (e.g., '1', 'latest').",
    )

    args = parser.parse_args()

    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        print("Error: GCP_PROJECT_ID environment variable not set.")
        return

    secret_version = get_secret_version_sample(
        project_id, args.secret_id, args.version_id
    )

    if secret_version:
        # Convert the SecretVersion object to a dictionary for JSON
        # serialization. Protobuf Timestamp objects need to be converted to
        # ISO format strings. Enums need to be converted to their string names.
        secret_version_dict = {
            "name": secret_version.name,
            "create_time": (
                secret_version.create_time.isoformat()
                if secret_version.create_time
                else None
            ),
            "destroy_time": (
                secret_version.destroy_time.isoformat()
                if secret_version.destroy_time
                else None
            ),
            "state": (
                secretmanager_v1beta2.resources.SecretVersion.State(
                    secret_version.state
                ).name
            ),
            "etag": secret_version.etag,
            "client_specified_payload_checksum": (
                secret_version.client_specified_payload_checksum
            ),
            "scheduled_destroy_time": (
                secret_version.scheduled_destroy_time.isoformat()
                if secret_version.scheduled_destroy_time
                else None
            ),
        }

        # Handle nested customer_managed_encryption if present
        # Check if the field is set using HasField
        if secret_version.HasField("customer_managed_encryption"):
            secret_version_dict["customer_managed_encryption"] = {
                "kms_key_version_name": (
                    secret_version.customer_managed_encryption
                    .kms_key_version_name
                )
            }
        else:
            secret_version_dict["customer_managed_encryption"] = None

        # Handle replication_status
        replication_status_dict = {}
        if secret_version.HasField("replication_status"):
            if secret_version.replication_status.HasField("automatic"):
                replication_status_dict["automatic"] = {}
                if (
                    secret_version.replication_status.automatic.HasField(
                        "customer_managed_encryption"
                    )
                ):
                    replication_status_dict["automatic"][
                        "customer_managed_encryption"
                    ] = {
                        "kms_key_version_name": (
                            secret_version.replication_status.automatic
                            .customer_managed_encryption.kms_key_version_name
                        )
                    }
                else:
                    replication_status_dict["automatic"][
                        "customer_managed_encryption"
                    ] = None
            elif secret_version.replication_status.HasField("user_managed"):
                replication_status_dict["user_managed"] = {"replicas": []}
                for replica in (
                    secret_version.replication_status.user_managed.replicas
                ):
                    replica_dict = {"location": replica.location}
                    if replica.HasField("customer_managed_encryption"):
                        replica_dict["customer_managed_encryption"] = {
                            "kms_key_version_name": (
                                replica.customer_managed_encryption
                                .kms_key_version_name
                            )
                        }
                    else:
                        replica_dict["customer_managed_encryption"] = None
                    replication_status_dict["user_managed"]["replicas"].append(
                        replica_dict
                    )
        secret_version_dict["replication_status"] = (
            replication_status_dict if replication_status_dict else None
        )

        print(json.dumps(secret_version_dict, indent=2))


if __name__ == "__main__":
    main()
