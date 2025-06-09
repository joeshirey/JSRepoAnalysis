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
import asyncio
from google.cloud import secretmanager_v1 as secretmanager
from google.api_core.exceptions import GoogleAPICallError

async def get_secret(project_id: str, secret_id: str, location: str = None) -> secretmanager.Secret:
    """
    Gets a secret from Google Cloud Secret Manager.

    Args:
        project_id: The ID of the Google Cloud project.
        secret_id: The ID of the secret to retrieve.
        location: (Optional) The location of the secret. If not provided,
                  the global secret path will be used.

    Returns:
        The retrieved Secret object.
    """
    # [START secretmanager_v1_secretmanagerservice_secret_create_async]
    client = secretmanager.SecretManagerServiceAsyncClient()

    if location:
        name = client.secret_path(project_id, location, secret_id)
    else:
        name = client.secret_path(project_id, secret_id)

    request = secretmanager.GetSecretRequest(name=name)

    response = None
    try:
        response = await client.get_secret(request=request)
    except GoogleAPICallError as e:
        print(f"Error getting secret '{secret_id}': {e}")
        raise
    finally:
        await client.close()

    return response
    # [END secretmanager_v1_secretmanagerservice_secret_create_async]

async def main():
    parser = argparse.ArgumentParser(
        description="Get a secret from Google Cloud Secret Manager."
    )
    parser.add_argument(
        "--secret-id",
        type=str,
        required=True,
        help="The ID of the secret to retrieve.",
    )
    parser.add_argument(
        "--location",
        type=str,
        required=False,
        help="The location of the secret (e.g., 'global' or 'us-central1').",
    )

    args = parser.parse_args()

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        raise ValueError("GCP_PROJECT_ID environment variable not set.")

    try:
        secret = await get_secret(project_id, args.secret_id, args.location)
        print(secret)
    except Exception as e:
        print(f"Failed to retrieve secret: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
