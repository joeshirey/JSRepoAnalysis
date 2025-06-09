import os
from dotenv import load_dotenv
from google.cloud import firestore
from typing import Dict, Any

# Load environment variables from .env file
load_dotenv()

def create(collection_name: str, document_id: str, document_payload: Dict[str, Any]):
    """
    Writes a document to a Firestore collection.

    Args:
        collection_name: The name of the Firestore collection.
        document_id: The ID of the document to create.
        document_payload: The data to write to the document.
    """
    # Get Firestore project ID and credentials file path from environment variables
    project_id = os.getenv("FIRESTORE_PROJECT_ID")
    #credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    firestore_db = os.getenv("FIRESTORE_DB")
    print(firestore_db)
    if not project_id:
        print("Error: PROJECT_ID environment variable not set.")
        return

    # Initialize Firestore client
    try:
        if credentials_path and os.path.exists(credentials_path):
            db = firestore.Client(project=project_id, database=firestore_db) # Assuming default database
        else:
             # If GOOGLE_APPLICATION_CREDENTIALS is not set or file not found,
             # Firestore client will attempt to use default credentials (e.g., from gcloud)
            db = firestore.Client(project=project_id, database=firestore_db) # Assuming default database

    except Exception as e:
        print(f"Error initializing Firestore client: {e}")
        return

    # Write the document
    try:
        doc_ref = db.collection(collection_name).document(document_id)
        doc_ref.set(document_payload)
        print(f"Document '{document_id}' successfully written to collection '{collection_name}'.")
    except Exception as e:
        print(f"Error writing document to Firestore: {e}")

def read(collection_name: str, document_id: str) -> Dict[str, Any] | None:
    """
    Reads a document from a Firestore collection.

    Args:
        collection_name: The name of the Firestore collection.
        document_id: The ID of the document to read.

    Returns:
        The document data as a dictionary if found, otherwise None.
    """
    project_id = os.getenv("FIRESTORE_PROJECT_ID")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    firestore_db = os.getenv("FIRESTORE_DB")

    if not project_id:
        print("Error: PROJECT_ID environment variable not set.")
        return None

    try:
        if credentials_path and os.path.exists(credentials_path):
            db = firestore.Client(project=project_id, database=firestore_db)
        else:
            db = firestore.Client(project=project_id, database=firestore_db)
    except Exception as e:
        print(f"Error initializing Firestore client: {e}")
        return None

    try:
        doc_ref = db.collection(collection_name).document(document_id)
        doc = doc_ref.get()
        if doc.exists:
            print(f"Document '{document_id}' successfully read from collection '{collection_name}'.")
            return doc.to_dict()
        else:
            print(f"Document '{document_id}' does not exist in collection '{collection_name}'.")
            return None
    except Exception as e:
        print(f"Error reading document from Firestore: {e}")
        return None

def read_all_in_collection(collection_name: str) -> list[Dict[str, Any]]:
    """
    Reads all documents from a Firestore collection.

    Args:
        collection_name: The name of the Firestore collection.

    Returns:
        A list of dictionaries, where each dictionary represents a document
        with its ID and data. Returns an empty list if no documents are found
        or an error occurs.
    """
    project_id = os.getenv("FIRESTORE_PROJECT_ID")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    firestore_db = os.getenv("FIRESTORE_DB")

    if not project_id:
        print("Error: PROJECT_ID environment variable not set.")
        return []

    try:
        if credentials_path and os.path.exists(credentials_path):
            db = firestore.Client(project=project_id, database=firestore_db)
        else:
            db = firestore.Client(project=project_id, database=firestore_db)
    except Exception as e:
        print(f"Error initializing Firestore client: {e}")
        return []

    documents_data = []
    try:
        docs = db.collection(collection_name).stream()
        for doc in docs:
            doc_data = doc.to_dict()
            doc_data['id'] = doc.id  # Include the document ID
            documents_data.append(doc_data)
        print(f"Successfully read {len(documents_data)} documents from collection '{collection_name}'.")
        return documents_data
    except Exception as e:
        print(f"Error reading all documents from collection '{collection_name}': {e}")
        return []

if __name__ == '__main__':
    # Example usage (replace with your actual collection, document ID, and payload)
    # Ensure .env has FIRESTORE_PROJECT_ID and GOOGLE_APPLICATION_CREDENTIALS (optional)
    # create("my_collection", "my_document", {"key": "value", "number": 123})
    pass
