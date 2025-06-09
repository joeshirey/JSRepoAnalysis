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

# [START secretmanager_v1_secretmanagerservice_secret_delete]
import argparse
import os
import sys

from google.cloud import secretmanager_v1
from google.api_core import exceptions
from google.protobuf import empty_pb2


def delete_secret_sample(
    project_id: str, secret_id: str
) -> None | empty_pb2.Empty:
    """
    Deletes a secret from Google Secret Manager.

    Args:
        project_id: The ID of the Google Cloud project.
        secret_id: The ID of the secret to delete.

    Returns:
        google.protobuf.empty_pb2.Empty if the secret was deleted successfully.
        None if the secret was not found.

    Raises:
        google.api_core.exceptions.GoogleAPICallError: If an API call fails
            for reasons other than the secret not being found.
    """
    client = secretmanager_v1.SecretManagerServiceClient()
    name = client.secret_path(project_id, secret_id)

    try:
        response = client.delete_secret(name=name)
        return response
    except exceptions.NotFound:
        return None
    except exceptions.GoogleAPICallError as e:
        # Re-raise other API errors for main to handle
        raise e


# [END secretmanager_v1_secretmanagerservice_secret_delete]

def main():
    parser = argparse.ArgumentParser(
        description="Delete a secret in Google Secret Manager."
    )
    parser.add_argument(
        "--project_id",
        type=str,
        default=os.environ.get("GCP_PROJECT_ID"),
        help=(
            "Your Google Cloud project ID. Defaults to GCP_PROJECT_ID "
            "environment variable."
        ),
    )
    parser.add_argument(
        "--secret_id",
        type=str,
        required=True,
        help="The ID of the secret to delete.",
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
        result = delete_secret_sample(args.project_id, args.secret_id)
        if result is None:
            print(
                f"Secret '{args.secret_id}' not found in project "
                f"'{args.project_id}'."
            )
        else:
            print(
                f"Secret '{args.secret_id}' in project '{args.project_id}' "
                "deleted successfully."
            )
    except exceptions.GoogleAPICallError as e:
        print(f"Error deleting secret: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
