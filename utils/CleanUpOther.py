#!/usr/bin/env python3
import argparse
import json
import os
import sys
from google.cloud import firestore
import vertexai
from vertexai.generative_models import GenerativeModel

def load_product_catalog(filename="utils/product_catalog.json"):
    """Loads the product catalog from a JSON file."""
    if not os.path.exists(filename):
        # Try to find the file in the root directory
        filename = os.path.join(os.path.dirname(__file__), '..', filename)
        if not os.path.exists(filename):
            print(f"Error: Product catalog file '{filename}' not found.")
            exit(1)
    with open(filename, 'r') as f:
        return json.load(f)

def get_gemini_suggestions(project_id, location, doc_id, document_data, product_catalog):
    """
    Uses Gemini to suggest a product_name and product_category
    with a sophisticated, multi-step analysis prompt.
    """
    print("  Calling Gemini API for analysis...")
    vertexai.init(project=project_id, location=location)
    model = GenerativeModel("gemini-2.5-flash-preview-05-20")

    prompt = f"""
    Your task is to be an expert Google Cloud developer and accurately identify the primary 'product_name' and its corresponding 'product_category' for the given document.

    Follow these steps in order:

    1.  **Analyze Metadata First (Primary Method):**
        * Examine the `git_info.github_link`. The path often contains the product name (e.g., `/ai-platform/` or `/vertex-ai/`). "asset" would be part of "Cloud Asset Inventory"
        * Examine the `region_tags`. These are often formatted like `[productname_verb_noun]` (e.g., `[vision_face_detection]`). The first part is a strong indicator of the product.

    2.  **Analyze Code (Secondary Method):**
        * If the product is not obvious from the metadata, then analyze the `raw_code`.
        * Look for `import` statements (e.g., `from google.cloud import storage`) and client instantiations (e.g., `storage.Client()`) to determine the primary Google Cloud service being used.

    3.  **Match to Catalog:**
        * Based on your findings, find the single best `product_name` and its `product_category` from the provided 'Product Catalog'.

    4.  **Provide JSON Output:**
        * Your final answer MUST be only the raw JSON object, with no other conversational text, explanations, or markdown formatting.

    **Product Catalog:**
    ```json
    {json.dumps(product_catalog, indent=2)}
    ```

    **Document Data:**
    ```json
    {json.dumps(document_data, indent=2)}
    ```
    """

    try:
        response = model.generate_content(prompt)

        if not response.candidates:
            print(f"  [!] For doc '{doc_id}', Gemini returned no candidates (likely due to safety filters).")
            return None

        response_text = response.text.strip()
        # A simple check for the start of a JSON object
        if not response_text.startswith('{'):
             json_string = response_text.lstrip("```json").rstrip("```").strip()
        else:
            json_string = response_text

        suggested = json.loads(json_string)
        return suggested

    except json.JSONDecodeError as e:
        print(f"  [!] For doc '{doc_id}', failed to decode JSON from Gemini's response.")
        print(f"      Error: {e}")
        print(f"      Raw Response: '{response.text}'")
        return None
    except Exception as e:
        print(f"  [!] An unexpected error occurred calling Gemini API for doc '{doc_id}': {e}")
        return None

def scan_and_update_firestore(project_id, collection_name, product_catalog, location, dry_run=True):
    """
    Scans all documents in a Firestore collection, uses Gemini to determine the correct
    product/category, and updates if necessary. Includes a dry-run mode for safety.
    """
    db = firestore.Client(database="generated-samples", project=project_id)
    collection_ref = db.collection(collection_name)

    print("Fetching all documents from the collection (this may take a moment)...")
    all_docs = list(collection_ref.stream())
    total_docs = len(all_docs)
    print(f"Found {total_docs} total documents to review.")

    docs_to_update = []

    for i, doc in enumerate(all_docs):
        doc_data = doc.to_dict()

        # --- START OF FIX ---
        # Get the evaluation_data field first to check its type
        eval_data = doc_data.get("evaluation_data")

        print(f"\n--- Reviewing document {i+1}/{total_docs}: {doc.id} ---")

        # Validate that eval_data is a dictionary before proceeding
        if not isinstance(eval_data, dict):
            print(f"  STATUS: Skipping. 'evaluation_data' field is a {type(eval_data).__name__}, not a dictionary.")
            continue
        # --- END OF FIX ---

        current_product_name = eval_data.get("product_name", "N/A")
        current_product_category = eval_data.get("product_category", "N/A")

        print(f"  Current: '{current_product_name}' in '{current_product_category}'")

        suggestions = get_gemini_suggestions(project_id, location, doc.id, doc_data, product_catalog)

        if suggestions and 'product_name' in suggestions and 'product_category' in suggestions:
            new_product_name = suggestions['product_name']
            new_product_category = suggestions['product_category']

            print(f"  Suggestion: '{new_product_name}' in '{new_product_category}'")

            if new_product_name != current_product_name or new_product_category != current_product_category:
                print("  STATUS: Change detected, update needed.")
                docs_to_update.append({
                    "id": doc.id,
                    "update_payload": {
                        "evaluation_data.product_name": new_product_name,
                        "evaluation_data.product_category": new_product_category
                    }
                })
            else:
                print("  STATUS: No change needed.")
        else:
            print("  STATUS: Failed to get a valid suggestion.")

    print(f"\n--- Review Complete ---")
    print(f"{len(docs_to_update)} documents flagged for update.")

    if dry_run:
        print("\nDRY RUN MODE: No changes will be written to Firestore.")
        print("Run with the --execute flag to apply the updates.")
        return

    if not docs_to_update:
        print("\nNo documents needed updating.")
        return

    user_input = input(f"Proceed with updating {len(docs_to_update)} documents in Firestore? (yes/no): ")
    if user_input.lower() != 'yes':
        print("Update cancelled by user.")
        return

    print("\nExecuting updates...")
    for item in docs_to_update:
        doc_ref = collection_ref.document(item['id'])
        doc_ref.update(item['update_payload'])
        print(f"  Updated {item['id']}")

    print("All updates complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scans and re-categorizes all documents in a Firestore collection using Vertex AI."
    )
    parser.add_argument("--project_id", required=True, help="Your Google Cloud project ID.")
    parser.add_argument("--collection", required=True, help="The Firestore collection to scan.")
    parser.add_argument("--location", default="us-central1", help="The GCP location for Vertex AI.")
    parser.add_argument("--execute", action="store_true", help="Execute the updates. Default is a dry run.")

    args = parser.parse_args()

    product_catalog = load_product_catalog()

    is_dry_run = not args.execute
    if is_dry_run:
        print("--- RUNNING IN DRY-RUN MODE ---")
    else:
        print("--- RUNNING IN EXECUTE MODE ---")

    scan_and_update_firestore(args.project_id, args.collection, product_catalog, args.location, dry_run=is_dry_run)