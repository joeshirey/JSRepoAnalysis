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

#!/usr/bin/env python3

# This sample demonstrates how to get the IAM policy for a Secret Manager secret.
#
# It requires the following environment variable to be set:
# - GCP_PROJECT_ID: The Google Cloud Project ID.
#
# It takes the following command-line argument:
# - --secret-id: The ID of the secret.
#
# Example usage:
# GCP_PROJECT_ID=your-project-id python3 your_script_name.py --secret-id your-secret-id

import argparse
import os
import json

from google.cloud import secretmanager_v1
from google.iam.v1 import iam_policy_pb2
from google.iam.v1 import policy_pb2


def get_iam_policy_sample(resource_name: str) -> policy_pb2.Policy:
    # [START secretmanager_v1_secretmanagerservice_iampolicy_get]
    """Gets the IAM policy for a secret.

    Args:
        resource_name: The full resource name of the secret,
                       e.g., "projects/my-project/secrets/my-secret".

    Returns:
        The IAM policy for the secret.
    """
    client = secretmanager_v1.SecretManagerServiceClient()
    request = iam_policy_pb2.GetIamPolicyRequest(
        resource=resource_name,
    )

    try:
        policy = client.get_iam_policy(request=request)
        return policy
    except Exception as err:
        print(f"Error getting IAM policy: {err}")
        raise
    # [END secretmanager_v1_secretmanagerservice_iampolicy_get]


def main():
    parser = argparse.ArgumentParser(
        description="Get IAM policy for a Secret Manager secret."
    )
    parser.add_argument(
        "--secret-id",
        type=str,
        required=True,
        help="The ID of the secret.",
    )

    args = parser.parse_args()

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        print("Error: GCP_PROJECT_ID environment variable not set.")
        exit(1)

    # Construct the resource name for the secret
    # The client library provides a helper for this:
    resource_name = secretmanager_v1.SecretManagerServiceClient.secret_path(
        project=project_id,
        secret=args.secret_id
    )

    try:
        policy = get_iam_policy_sample(resource_name)
        # Convert policy to a dictionary for JSON serialization
        policy_dict = {
            "version": policy.version,
            "bindings": [
                {
                    "role": b.role,
                    "members": list(b.members),
                    "condition": {
                        "expression": b.condition.expression,
                        "title": b.condition.title,
                        "description": b.condition.description,
                    } if b.condition.expression else None,
                }
                for b in policy.bindings
            ],
            "etag": policy.etag.decode('utf-8') if policy.etag else None,
        }
        print(json.dumps(policy_dict, indent=2))
    except Exception:  # The sample function already prints the error
        exit(1)


if __name__ == "__main__":
    main()
