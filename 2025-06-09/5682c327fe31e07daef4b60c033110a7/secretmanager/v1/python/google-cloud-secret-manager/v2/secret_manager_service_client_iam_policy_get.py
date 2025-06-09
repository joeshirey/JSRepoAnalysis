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

# [START secretmanager_v1_secretmanagerservice_iampolicy_get]
import argparse
import json
import os
import sys

from google.cloud import secretmanager_v1
from google.iam.v1 import iam_policy_pb2  # type: ignore
from google.api_core.exceptions import GoogleAPIError


def get_iam_policy_sample(project_id: str, secret_id: str):
    """
    Gets the IAM policy for a secret.

    Args:
        project_id: The ID of the Google Cloud project.
        secret_id: The ID of the secret to get the IAM policy for.
    Returns:
        google.iam.v1.policy_pb2.Policy: The IAM policy for the secret.
    """
    client = None
    try:
        # Create the Secret Manager client.
        # Clients should be reused across multiple calls to avoid connection
        # overhead.
        client = secretmanager_v1.SecretManagerServiceClient()

        # Build the resource name for the secret.
        # This example assumes the secret is not in a specific location.
        # For location-specific secrets, the format would be:
        # "projects/PROJECT_ID/locations/LOCATION_ID/secrets/SECRET_ID"
        resource_name = client.secret_path(project_id, secret_id)

        # Build the request.
        request = iam_policy_pb2.GetIamPolicyRequest(
            resource=resource_name,
        )

        # Call the API.
        policy = client.get_iam_policy(request=request)
        return policy
    except GoogleAPIError:
        # Re-raise the exception to be caught by the main function's handler.
        raise
    finally:
        if client:
            client.close()
# [END secretmanager_v1_secretmanagerservice_iampolicy_get]


def main():
    """
    Main entry point for the script.

    This script demonstrates how to retrieve the IAM policy for a Google Cloud
    Secret Manager secret. It takes the secret ID as a command-line argument
    and the Google Cloud project ID from an environment variable.

    Prerequisites:
    - Environment variable `GCP_PROJECT_ID` must be set to your Google Cloud
      Project ID.
    - A Secret Manager secret with the specified ID must exist within the
      project.
    - Appropriate IAM permissions to call `secretmanager.secrets.getIamPolicy`
      on the specified secret.

    Usage:
    export GCP_PROJECT_ID="your-project-id"
    python get_iam_policy.py --secret-id "your-secret-id"
    """
    parser = argparse.ArgumentParser(
        description="Get the IAM policy for a Secret Manager secret."
    )
    parser.add_argument(
        "--secret-id",
        type=str,
        required=True,
        help="The ID of the secret (e.g., 'my-secret-name').",
    )

    args = parser.parse_args()

    # Get project ID from environment variable
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        print(
            "Error: Environment variable GCP_PROJECT_ID is not set. "
            "Please set it to your Google Cloud Project ID.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        policy = get_iam_policy_sample(project_id, args.secret_id)

        # Convert the Policy object to a dictionary for JSON serialization
        # and ensure line length compliance.
        policy_dict = {
            "version": policy.version,
            "bindings": [],
            "etag": policy.etag.decode("utf-8") if policy.etag else "",
        }

        for binding in policy.bindings:
            binding_dict = {
                "role": binding.role,
                "members": list(binding.members),
            }
            # Only include condition if it has an expression
            if binding.condition.expression:
                binding_dict["condition"] = {
                    "expression": binding.condition.expression,
                    "title": binding.condition.title,
                    "description": binding.condition.description,
                    "location": binding.condition.location,
                }
            policy_dict["bindings"].append(binding_dict)

        print(json.dumps(policy_dict, indent=2))
    except GoogleAPIError as e:
        print(f"Error getting IAM policy: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
