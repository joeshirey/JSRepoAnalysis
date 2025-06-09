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

// [START secretmanager_v1_secretmanagerservice_secret_get]
import argparse
import os
import json
import sys
from google.cloud import secretmanager_v1
from google.api_core import exceptions

def get_secret_sample(project_id: str, secret_id: str) -> dict:
    """Gets metadata for a given Secret.

    Args:
        project_id: The ID of the GCP project.
        secret_id: The ID of the secret to retrieve.

    Returns:
        A dictionary representing the retrieved Secret resource.
    """
    # Perform all required setup, such as initializing the API client.
    client = secretmanager_v1.SecretManagerServiceClient()

    # Build the resource name of the secret.
    # Format: projects/{project_id}/secrets/{secret_id}
    name = client.secret_path(project_id, secret_id)

    try:
        # Execute the API call within a try/catch block for basic error handling.
        secret = client.get_secret(name=name)
        # The Secret object is a protobuf message. Convert it to a dictionary
        # for consistent JSON output.
        return secret.to_dict()
    except exceptions.NotFound:
        raise ValueError(f"Secret '{name}' not found.")
    except Exception as e:
        raise RuntimeError(f"Failed to get secret '{name}': {e}")
    finally:
        # Perform any necessary cleanup (e.g., closing the client if required).
        # In Python, gRPC clients do not typically need explicit closing.
        # The client manages its own connections.
        pass
# [END secretmanager_v1_secretmanagerservice_secret_get]


def main():
    """
    Main entry point for the script. Parses command-line arguments,
    calls the primary sample function, and prints the result.
    """
    parser = argparse.ArgumentParser(
        description="Get a Secret from Google Cloud Secret Manager."
    )
    parser.add_argument(
        "--project-id",
        type=str,
        help=(
            "The GCP project ID where the secret is located. "
            "Required if GCP_PROJECT_ID environment variable is not set."
        ),
    )
    parser.add_argument(
        "--secret-id",
        type=str,
        required=True,
        help="The ID of the secret to retrieve.",
    )

    args = parser.parse_args()

    # Use environment variable as a fallback for project_id
    if not args.project_id:
        args.project_id = os.environ.get("GCP_PROJECT_ID")

    if not args.project_id:
        parser.error(
            "The --project-id argument is required or set the "
            "GCP_PROJECT_ID environment variable."
        )

    try:
        secret_data = get_secret_sample(args.project_id, args.secret_id)
        # Print the final result of the successful API call to standard output.
        print(json.dumps(secret_data, indent=2))
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
