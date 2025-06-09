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

# This sample demonstrates how to retrieve the IAM policy for a Secret Manager secret.
#
# To run this sample:
# 1. Install the Google Cloud Secret Manager client library:
#    pip install google-cloud-secret-manager
# 2. Set the GCP_PROJECT_ID environment variable:
#    export GCP_PROJECT_ID="your-gcp-project-id"
# 3. Run the script from the command line, providing the secret ID:
#    python your_script_name.py --secret-id your-secret-id

import argparse
import os
import json

from google.cloud import secretmanager_v1
from google.iam.v1 import iam_policy_pb2


# [START secretmanager_v1_secretmanagerservice_iampolicy_get]
def get_iam_policy_sample(project_id: str, secret_id: str):
    """
    Retrieves the IAM policy for a Secret Manager secret.

    Args:
        project_id: The ID of the Google Cloud project.
        secret_id: The ID of the secret to retrieve the IAM policy for.

    Returns:
        google.iam.v1.policy_pb2.Policy: The IAM policy for the secret.
    """
    client = secretmanager_v1.SecretManagerServiceClient()

    # The client library automatically handles authentication and project context.
    # For long-lived applications, it's recommended to reuse the client instance.

    try:
        # Build the resource name of the secret.
        # The resource name format is projects/{project_id}/secrets/{secret_id}
        name = client.secret_path(project_id, secret_id)

        request = iam_policy_pb2.GetIamPolicyRequest(
            resource=name,
        )

        policy = client.get_iam_policy(request=request)
        return policy
    except Exception as e:
        print(f"Error getting IAM policy for secret {name}: {e}")
        raise
    finally:
        client.close()
# [END secretmanager_v1_secretmanagerservice_iampolicy_get]


def main():
    parser = argparse.ArgumentParser(
        description="Get IAM policy for a Secret Manager secret."
    )
    parser.add_argument(
        "--secret-id",
        type=str,
        required=True,
        help="The ID of the secret to get the IAM policy for."
    )
    args = parser.parse_args()

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        print("Error: GCP_PROJECT_ID environment variable not set.")
        exit(1)

    try:
        policy = get_iam_policy_sample(project_id, args.secret_id)

        # Convert the policy object to a dictionary for JSON serialization.
        # Protobuf objects are not directly JSON serializable.
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
                    } if b.condition.expression else None,  # Only include condition if it has an expression
                }
                for b in policy.bindings
            ],
            "etag": policy.etag.decode('utf-8') if policy.etag else None,
        }
        print(json.dumps(policy_dict, indent=2))
    except Exception as e:
        print(f"Failed to get IAM policy: {e}")
        exit(1)


if __name__ == "__main__":
    main()
