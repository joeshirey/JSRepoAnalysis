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

# // [START secretmanager_v1_secretmanagerservice_secret_delete]
from google.cloud import secretmanager_v1
from google.api_core import exceptions

def delete_secret_sample(
    project_id: str, secret_id: str
) -> None:
    """
    Deletes a secret from Google Cloud Secret Manager.

    Args:
        project_id: The ID of the Google Cloud project.
        secret_id: The ID of the secret to delete.
    """
    # Create the Secret Manager client.
    # It's recommended to use a 'with' statement for clients that support it
    # to ensure resources are properly released.
    with secretmanager_v1.SecretManagerServiceClient() as client:
        # Build the resource name of the secret.
        name = client.secret_path(project_id, secret_id)

        try:
            # Call the API to delete the secret.
            # The delete_secret method returns None on successful deletion.
            client.delete_secret(request={"name": name})
            return None
        except exceptions.NotFound:
            raise ValueError(
                f"Secret '{secret_id}' not found in project '{project_id}'."
            )
        except Exception as e:
            # Catch any other potential errors from the API call
            raise RuntimeError(f"Failed to delete secret '{secret_id}': {e}")


# // [END secretmanager_v1_secretmanagerservice_secret_delete]

import argparse
import os
import json

def main():
    parser = argparse.ArgumentParser(
        description="Delete a secret in Google Cloud Secret Manager."
    )
    parser.add_argument(
        "--project_id",
        type=str,
        default=os.getenv("GCP_PROJECT_ID"),
        help="Your Google Cloud project ID. Defaults to GCP_PROJECT_ID environment variable.",
    )
    parser.add_argument(
        "--secret_id",
        type=str,
        help="The ID of the secret to delete.",
        required=True,
    )

    args = parser.parse_args()

    if not args.project_id:
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": "Error: --project_id or GCP_PROJECT_ID environment variable must be set.",
                }
            )
        )
        exit(1)

    try:
        # Call the primary sample function.
        delete_secret_sample(args.project_id, args.secret_id)
        # If delete_secret_sample returns without raising an exception, it means success.
        result = {
            "status": "success",
            "secret_id": args.secret_id,
            "message": f"Secret '{args.secret_id}' deleted successfully.",
        }
    except (ValueError, RuntimeError) as e:
        # Catch specific errors raised by the sample function
        result = {
            "status": "error",
            "secret_id": args.secret_id,
            "message": str(e),
        }
    except Exception as e:
        # Catch any unexpected errors
        result = {
            "status": "error",
            "secret_id": args.secret_id,
            "message": f"An unexpected error occurred: {e}",
        }

    # Print the result to standard output in JSON format.
    print(json.dumps(result))


if __name__ == "__main__":
    main()
