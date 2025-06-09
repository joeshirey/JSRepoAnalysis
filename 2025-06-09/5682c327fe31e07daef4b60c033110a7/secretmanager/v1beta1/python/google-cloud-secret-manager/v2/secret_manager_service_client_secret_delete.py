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

# [START secretmanager_v1beta1_secretmanagerservice_secret_delete]
import argparse
import os

from google.cloud import secretmanager_v1beta1
from google.api_core import exceptions

# This sample demonstrates how to delete a secret in Google Cloud Secret Manager.
#
# Prerequisites:
# - Google Cloud Project ID set in the environment variable GCP_PROJECT_ID.
# - A secret to delete, specified via the --secret-id command-line argument.
# - The service account running this code must have `secretmanager.secrets.delete`
#   permission on the secret.


def delete_secret_sample(project_id: str, secret_id: str) -> None:
    """Deletes a secret from Google Cloud Secret Manager.

    Args:
        project_id: The Google Cloud project ID.
        secret_id: The ID of the secret to delete.

    Raises:
        google.api_core.exceptions.NotFound: If the secret does not exist.
        google.api_core.exceptions.FailedPrecondition: If the secret cannot
            be deleted (e.g., has enabled versions or is pending deletion).
        Exception: For any other unexpected errors.
    """
    # Initialize the client using a 'with' statement for proper
    # resource cleanup.
    with secretmanager_v1beta1.SecretManagerServiceClient() as client:
        # Build the resource name of the secret.
        secret_name = client.secret_path(project_id, secret_id)

        # Execute the API call within a try/catch block for basic
        # error handling.
        try:
            client.delete_secret(name=secret_name)
            # The delete_secret method returns None on success.
            # No explicit return value needed here, as the success is
            # implied if no exception is raised.
        except exceptions.NotFound as e:
            # Re-raise to be handled by the main block for consistent output.
            raise exceptions.NotFound(
                f"Secret {secret_name} not found."
            ) from e
        except exceptions.FailedPrecondition as e:
            # Re-raise with a more descriptive message.
            raise exceptions.FailedPrecondition(
                f"Secret {secret_name} could not be deleted: {e}. "
                "It might have enabled versions or be pending deletion."
            ) from e
        except Exception as e:
            # Catch any other unexpected errors.
            raise Exception(
                f"An unexpected error occurred while deleting "
                f"secret {secret_name}: {e}"
            ) from e

# [END secretmanager_v1beta1_secretmanagerservice_secret_delete]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Delete a secret in Google Cloud Secret Manager."
    )
    parser.add_argument(
        "--secret-id",
        required=True,
        help="The ID of the secret to delete.",
    )

    args = parser.parse_args()

    # GCP_PROJECT_ID is a global configuration value, sourced from
    # environment.
    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        print(
            "Error: GCP_PROJECT_ID environment variable not set. "
            "Please set it to your Google Cloud project ID."
        )
        exit(1)

    try:
        delete_secret_sample(project_id, args.secret_id)
        # Print success message from the main block as per instructions.
        print(f"Secret projects/{project_id}/secrets/{args.secret_id} "
              "deleted successfully.")
    except exceptions.NotFound as e:
        print(f"Error: {e}")
        exit(1)
    except exceptions.FailedPrecondition as e:
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)
