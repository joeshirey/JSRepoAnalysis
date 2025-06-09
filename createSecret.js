// Copyright 2025 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

"use strict";

const { SecretManagerServiceClient } = require("@google-cloud/secret-manager");

/**
 * Gets metadata for a given Secret.
 *
 * @param {string} projectId The Google Cloud Project ID.
 * @param {string} secretId The ID of the secret to retrieve.
 * @returns {Promise<object>} The Secret metadata.
 */
async function getSecret(projectId, secretId) {
  // [START secretmanager_v1_secretmanagerservice_get_secret_async]
  // Initialize the Secret Manager client.
  // The client can be reused across multiple calls to reduce overhead.
  const client = new SecretManagerServiceClient();

  // Construct the resource name for the secret.
  // The format is projects/{project}/secrets/{secret}
  // For regional secrets, it would be projects/{project}/locations/{location}/secrets/{secret}
  // This sample uses the global secret format.
  const name = `projects/${projectId}/secrets/${secretId}`;

  try {
    // Call the getSecret API to retrieve the secret metadata.
    const [secret] = await client.getSecret({ name });
    return secret;
  } catch (err) {
    // Re-throw the error to be caught by the main function's try/catch block.
    throw new Error(`Failed to get secret '${name}': ${err.message || err}`);
  } finally {
    // Close the client to release resources.
    // This is important for long-running processes.
    await client.close();
  }
  // [END secretmanager_v1_secretmanagerservice_get_secret_async]
}

/**
 * Main function to parse arguments, call the getSecret function, and print the result.
 */
async function main() {
  try {
    // Manually parse command-line arguments.
    const args = {};
    process.argv.slice(2).forEach((arg) => {
      if (arg.startsWith("--")) {
        const parts = arg.substring(2).split("=");
        if (parts.length === 2) {
          args[parts[0]] = parts[1];
        } else {
          args[parts[0]] = true;
        }
      }
    });

    const secretId = args["secret-id"];
    if (!secretId) {
      console.error("Error: --secret-id argument is required.");
      console.error("Usage: node get_secret.js --secret-id=<your-secret-id>");
      process.exit(1);
    }

    // Get the Google Cloud Project ID from environment variables.
    const projectId = process.env.GCP_PROJECT_ID;
    if (!projectId) {
      throw new Error(
        "GCP_PROJECT_ID environment variable is not set. Please set it to your Google Cloud Project ID.",
      );
    }

    // Call the primary sample function.
    const secret = await getSecret(projectId, secretId);

    // Print the result to standard output in JSON format.
    console.log(JSON.stringify(secret, null, 2));
  } catch (error) {
    // Log any errors and set a non-zero exit code.
    console.error("Error:", error.message || error);
    process.exitCode = 1;
  }
}

// Execute the main function when the script is run directly.
if (require.main === module) {
  main();
}
