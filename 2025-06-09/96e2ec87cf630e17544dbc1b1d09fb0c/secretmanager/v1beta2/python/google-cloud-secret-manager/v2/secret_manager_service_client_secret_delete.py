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
import sys

from google.cloud import secretmanager_v1beta2
from google.api_core import exceptions


def delete_secret_sample(project_id: str, secret_id: str) -> bool:
    """
    Deletes a secret from Google Cloud Secret Manager.

    Args:
        project_id: The Google Cloud project ID.
        secret_id: The ID of the secret to delete.

    Returns:
        True if the secret was deleted successfully.
        False if the secret was not found (idempotent delete).
    Raises:
        google.api_core.exceptions.GoogleAPICallError: If an API call fails
            for reasons other than NotFound.
    """
    # [START secretmanager_v1beta2_secretmanagerservice_secret_delete]
    # Create the Secret Manager client.
    # The client is designed to be reused. It's safe to create it once and use it
    # across multiple calls. For cleanup, you can use a 'with' statement or
    # explicitly call client.close().
    with secretmanager_v1beta2.SecretManagerServiceClient() as client:
        name = client.secret_path(project_id, secret_id)

        try:
            client.delete_secret(name=name)
            return True  # Successfully deleted
        except exceptions.NotFound:
            # Secret not found is often treated as a successful idempotent delete.
            return False  # Indicate that it was not found
        except exceptions.GoogleAPICallError as e:
            # Re-raise other API errors for main to handle.
            raise e
    # [END secretmanager_v1beta2_secretmanagerservice_secret_delete]


def main():
    parser = argparse.ArgumentParser(
        description="Deletes a secret in Google Cloud Secret Manager."
    )
    parser.add_argument(
        "--project-id",
        type=str,
        default=os.environ.get("GCP_PROJECT_ID"),
        help=(
            "Your Google Cloud project ID. Defaults to GCP_PROJECT_ID environment "
            "variable."
        ),
    )
    parser.add_argument(
        "--secret-id",
        type=str,
        required=True,
        help="The ID of the secret to delete.",
    )

    args = parser.parse_args()

    if not args.project_id:
        print(
            "Error: --project-id or GCP_PROJECT_ID environment variable must be set.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        deleted = delete_secret_sample(args.project_id, args.secret_id)
        if deleted:
            print(
                f"Secret '{args.secret_id}' in project '{args.project_id}' "
                "deleted successfully."
            )
        else:
            print(
                f"Secret '{args.secret_id}' not found in project "
                f"'{args.project_id}'."
            )
    except exceptions.GoogleAPICallError as e:
        print(
            f"Error deleting secret '{args.secret_id}': {e}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
