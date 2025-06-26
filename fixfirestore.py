# main.py
import os
import firebase_admin
from firebase_admin import credentials, firestore

# --- SCRIPT CONFIGURATION ---
# IMPORTANT: Replace this with the actual name of the collection you want to process.
COLLECTION_NAME = "Python"
# Specify the name of your Firestore database.
DATABASE_NAME = "existing-samples"
# The criterion name you are looking for.
OLD_CRITERION_NAME = "API Effectiveness (googleapis/googleapis)"
# The new value you want to set for the criterion name.
NEW_CRITERION_NAME = "API Effectiveness"
# The top-level field containing the evaluation results.
EVALUATION_DATA_FIELD = "evaluation_data"
# The field within the evaluation object that contains the list of criteria.
CRITERIA_LIST_FIELD_NAME = "criteria_breakdown"
# The key within each criterion object that holds the name.
CRITERION_NAME_KEY = "criterion_name"


def initialize_firestore_app():
    """
    Initializes the Firebase Admin SDK application instance.
    It expects the Google Application Credentials to be set as an environment
    variable. For example:
    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/serviceAccountKey.json"

    Returns:
        The initialized Firebase app object, or None if initialization fails.
    """
    try:
        # Check if the default app is already initialized to prevent errors.
        if not firebase_admin._apps:
            cred = credentials.ApplicationDefault()
            app = firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully.")
            return app
        else:
            print("Firebase Admin SDK already initialized.")
            return firebase_admin.get_app()
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {e}")
        print("Please ensure you have set the GOOGLE_APPLICATION_CREDENTIALS environment variable.")
        return None

def update_documents_in_collection(db, collection_name):
    """
    Iterates through all documents, looks for evaluation data, and updates a
    specific criterion name within a nested list. Includes detailed diagnostic counters.

    Args:
        db: The Firestore database client for your specific database.
        collection_name: The name of the collection to process.
    """
    if not collection_name or collection_name == "your_collection_name":
        print("Error: Please update the 'COLLECTION_NAME' variable at the top of the script.")
        return

    print(f"\nStarting to process collection: '{collection_name}' in database '{DATABASE_NAME}'...")
    collection_ref = db.collection(collection_name)
    docs = collection_ref.stream()

    # --- Initialize Counters ---
    processed_count = 0
    updated_count = 0
    # Diagnostic counters
    skipped_key_missing = 0
    skipped_string_notice = 0
    skipped_no_criteria_list = 0
    skipped_other_bad_format = 0

    for doc in docs:
        processed_count += 1
        doc_data = doc.to_dict()
        doc_id = doc.id

        # This is the main data field we are inspecting
        evaluation_data = doc_data.get(EVALUATION_DATA_FIELD)

        # Initialize here to use in the update call later
        criteria_list = None
        evaluation_obj = None

        # --- REVISED DIAGNOSTIC LOGIC ---
        # CASE 1: The 'evaluation_data' is a DICTIONARY (the primary expected format).
        if isinstance(evaluation_data, dict):
            evaluation_obj = evaluation_data
            criteria_list = evaluation_obj.get(CRITERIA_LIST_FIELD_NAME)
            if not isinstance(criteria_list, list):
                skipped_no_criteria_list += 1
                continue # Skip this document as it's missing the list to check.
        
        # CASE 2: The 'evaluation_data' is a LIST (e.g., holding a string notice).
        elif isinstance(evaluation_data, list):
            if evaluation_data and isinstance(evaluation_data[0], str):
                skipped_string_notice += 1
            else: # Catches empty lists or lists with non-string/non-dict content
                skipped_other_bad_format +=1
            continue # Skip list-based fields as they don't have criteria to update.
            
        # CASE 3: The key is missing or it's another format (None, int, etc).
        else:
            if evaluation_data is None:
                skipped_key_missing += 1
            else:
                skipped_other_bad_format += 1
            continue # Skip this document.
        
        # --- Perform Update Logic ---
        # This section is only reached if we have a valid criteria_list to check.
        was_modified = False
        for criterion_item in criteria_list:
            if isinstance(criterion_item, dict):
                if criterion_item.get(CRITERION_NAME_KEY) == OLD_CRITERION_NAME:
                    criterion_item[CRITERION_NAME_KEY] = NEW_CRITERION_NAME
                    was_modified = True
                    print(f"  - Found and marked criterion for update in document ID: {doc_id}")
        
        if was_modified:
            try:
                # We need to update the entire evaluation_data object
                doc.reference.update({EVALUATION_DATA_FIELD: evaluation_obj})
                print(f"  -> Successfully updated document ID: {doc_id}")
                updated_count += 1
            except Exception as e:
                print(f"  -> Error updating document ID {doc_id}: {e}")
        
        if processed_count % 500 == 0:
            print(f" ...scanned {processed_count} documents...")

    # --- Print Final Report ---
    print("\n--- Processing Complete ---")
    print(f"Total documents scanned in collection: {processed_count}")
    print(f"Total documents updated successfully: {updated_count}")
    
    print("\n--- Diagnostic Counts ---")
    valid_for_check = processed_count - skipped_key_missing - skipped_string_notice - skipped_no_criteria_list - skipped_other_bad_format
    print(f"Documents skipped (key '{EVALUATION_DATA_FIELD}' missing): {skipped_key_missing}")
    print(f"Documents skipped ('{EVALUATION_DATA_FIELD}' contains a string notice): {skipped_string_notice}")
    print(f"Documents skipped (had evaluation data but no '{CRITERIA_LIST_FIELD_NAME}' list): {skipped_no_criteria_list}")
    print(f"Documents skipped (other unexpected format): {skipped_other_bad_format}")
    print("-" * 25)
    print(f"Total documents with a valid structure for checking: {valid_for_check}")
    print(f" -> Of these, documents that required an update: {updated_count}")
    print(f" -> Of these, documents that did NOT require an update: {valid_for_check - updated_count}")


if __name__ == "__main__":
    app = initialize_firestore_app()
    if app:
        try:
            db_client = firestore.client(database_id=DATABASE_NAME)
            print(f"Successfully connected to Firestore database: '{DATABASE_NAME}'")
            update_documents_in_collection(db_client, COLLECTION_NAME)
        except Exception as e:
            print(f"Error connecting to database '{DATABASE_NAME}': {e}")
            print("Please ensure the database name is correct and that the service account has permissions.")
