import os
from dotenv import load_dotenv
from google.cloud import firestore
from typing import Dict, Any, Optional

# Load environment variables from .env file
load_dotenv()

class FirestoreClient:
    _instance = None
    _db: Optional[firestore.Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirestoreClient, cls).__new__(cls)
        return cls._instance

    def open_connection(self):
        if self._db is None:
            project_id = os.getenv("FIRESTORE_PROJECT_ID")
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            firestore_db_name = os.getenv("FIRESTORE_DB")

            if not project_id:
                print("Error: FIRESTORE_PROJECT_ID environment variable not set.")
                return

            try:
                if credentials_path and os.path.exists(credentials_path):
                    self._db = firestore.Client(project=project_id, database=firestore_db_name)
                else:
                    self._db = firestore.Client(project=project_id, database=firestore_db_name)
                print("Firestore connection opened.")
            except Exception as e:
                print(f"Error initializing Firestore client: {e}")
                self._db = None

    def close_connection(self):
        if self._db:
            # Firestore client doesn't have an explicit close method,
            # but setting it to None allows for re-initialization if needed.
            self._db = None
            print("Firestore connection closed (client released).")

    def get_db(self) -> Optional[firestore.Client]:
        if self._db is None:
            print("Warning: Firestore connection not open. Call open_connection() first.")
        return self._db

def create(collection_name: str, document_id: str, document_payload: Dict[str, Any]):
    """
    Writes a document to a Firestore collection.

    Args:
        collection_name: The name of the Firestore collection.
        document_id: The ID of the document to create.
        document_payload: The data to write to the document.
    """
    db = FirestoreClient().get_db()
    if not db:
        print("Error: Firestore client not available for create operation.")
        return

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
    db = FirestoreClient().get_db()
    if not db:
        print("Error: Firestore client not available for read operation.")
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
    db = FirestoreClient().get_db()
    if not db:
        print("Error: Firestore client not available for read_all_in_collection operation.")
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
    # client = FirestoreClient()
    # client.open_connection()
    # create("my_collection", "my_document", {"key": "value", "number": 123})
    # client.close_connection()
    pass
