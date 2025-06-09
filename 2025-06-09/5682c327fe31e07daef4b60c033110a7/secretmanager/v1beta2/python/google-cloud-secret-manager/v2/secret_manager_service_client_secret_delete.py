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
from google.api_core import exceptions


# [START secretmanager_v1beta2_secretmanagerservice_secret_delete]
def delete_secret_sample(project_id: str, secret_id: str) -> dict:
    """Deletes a secret from Google Cloud Secret Manager.

    Args:
        project_id: The ID of the Google Cloud project.
        secret_id: The ID of the secret to delete.

    Returns:
        dict: A dictionary indicating the status and message of the operation.
              Schema: {"status": "success"|"error", "message": str}
    """
    # Create the Secret Manager client.
    # Use a context manager for proper resource cleanup.
    try:
        with secretmanager_v1beta2.SecretManagerServiceClient() as client:
            # Build the resource name of the secret.
            name = client.secret_path(project_id, secret_id)

            # Delete the secret.
            # This API call returns an empty response (google.protobuf.Empty)
            # on success.
            client.delete_secret(name=name)
            return {
                "status": "success",
                "message": f"Secret '{secret_id}' deleted successfully.",
            }
    except exceptions.NotFound:
        return {
            "status": "error",
            "message": (
                f"Secret '{secret_id}' not found in project "
                f"'{project_id}'."
            ),
        }
    except exceptions.GoogleAPIError as e:
        # For GoogleAPIError, str(e) usually provides a good summary.
        return {"status": "error", "message": f"An API error occurred: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}

# [END secretmanager_v1beta2_secretmanagerservice_secret_delete]


def main():
    """Parses command-line arguments and calls the delete_secret_sample function.

    Prints the result to the console in JSON format.
    """
    parser = argparse.ArgumentParser(
        description="Delete a secret in Google Cloud Secret Manager."
    )
    parser.add_argument(
        "--project-id",
        type=str,
        help="Your Google Cloud project ID. Defaults to GCP_PROJECT_ID "
        "environment variable.",
        default=os.environ.get("GCP_PROJECT_ID"),
    )
    parser.add_argument(
        "--secret-id",
        type=str,
        required=True,
        help="The ID of the secret to delete.",
    )

    args = parser.parse_args()

    if not args.project_id:
        result = {
            "status": "error",
            "message": (
                "Project ID is required. Please provide it via --project-id "
                "or set the GCP_PROJECT_ID environment variable."
            ),
        }
        print(json.dumps(result))
        return

    # Call the primary sample function.
    result = delete_secret_sample(args.project_id, args.secret_id)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
