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


"""
This script demonstrates how to delete a secret in Google Cloud Secret Manager.

It requires the GCP_PROJECT_ID environment variable to be set.
The secret ID to delete must be passed as a command-line argument.
"""

# [START secretmanager_v1_secretmanagerservice_secret_delete]
import argparse
import json
import os
from google.cloud import secretmanager_v1
from google.api_core import exceptions

def delete_secret_sample(project_id: str, secret_id: str) -> str:
    """
    Deletes a secret.

    Args:
        project_id: The Google Cloud project ID.
        secret_id: The ID of the secret to delete.

    Returns:
        A string indicating the result of the operation.
    """
    try:
        # Initialize the client. Using a 'with' statement ensures the client is properly closed.
        with secretmanager_v1.SecretManagerServiceClient() as client:
            name = client.secret_path(project_id, secret_id)

            # Create the DeleteSecretRequest object
            request = secretmanager_v1.types.DeleteSecretRequest(name=name)
            client.delete_secret(request=request)
            return f"Secret '{secret_id}' deleted successfully."
    except exceptions.NotFound:
        return f"Secret '{secret_id}' not found."
    except exceptions.FailedPrecondition as e:
        return (
            f"Failed to delete secret '{secret_id}': {e}. "
            "It might have versions or be in use."
        )
    except Exception as e:
        return f"An unexpected error occurred: {e}"
# [END secretmanager_v1_secretmanagerservice_secret_delete]


def main():
    """
    Main entry point for the script.
    Parses command-line arguments, calls the sample function, and prints the result.
    """
    parser = argparse.ArgumentParser(
        description="Delete a Secret in Google Cloud Secret Manager."
    )
    parser.add_argument(
        "--secret-id", required=True, help="The ID of the secret to delete."
    )

    args = parser.parse_args()

    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        print(
            json.dumps(
                {"error": "GCP_PROJECT_ID environment variable not set."}
            ),
            file=os.sys.stderr,
        )
        os.sys.exit(1)

    result_message = delete_secret_sample(project_id, args.secret_id)

    # The final result of the API call is a message indicating success or failure.
    # This is wrapped in a JSON object as required by the output schema.
    print(json.dumps({"message": result_message}))


if __name__ == "__main__":
    main()
