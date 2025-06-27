import os
from google.cloud import firestore
from typing import Dict, Any, Optional

class FirestoreRepository:
    def __init__(self, config):
        self.config = config
        self._db = firestore.Client(project=self.config.project_id, database=self.config.firestore_db)
        print("Firestore connection opened.")

    def create(self, collection_name: str, document_id: str, document_payload: Dict[str, Any]):
        """
        Writes a document to a Firestore collection.
        """
        try:
            doc_ref = self._db.collection(collection_name).document(document_id)
            doc_ref.set(document_payload)
            print(f"Document '{document_id}' successfully written to collection '{collection_name}'.")
        except Exception as e:
            print(f"Error writing document to Firestore: {e}")

    def read(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Reads a document from a Firestore collection.
        """
        try:
            doc_ref = self._db.collection(collection_name).document(document_id)
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

    def read_all_in_collection(self, collection_name: str) -> list[Dict[str, Any]]:
        """
        Reads all documents from a Firestore collection.
        """
        documents_data = []
        try:
            docs = self._db.collection(collection_name).stream()
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data['id'] = doc.id
                documents_data.append(doc_data)
            print(f"Successfully read {len(documents_data)} documents from collection '{collection_name}'.")
            return documents_data
        except Exception as e:
            print(f"Error reading all documents from collection '{collection_name}': {e}")
            return []

    def delete(self, collection_name: str, document_id: str):
        """
        Deletes a document from a Firestore collection.
        """
        try:
            self._db.collection(collection_name).document(document_id).delete()
            print(f"Document '{document_id}' successfully deleted from collection '{collection_name}'.")
        except Exception as e:
            print(f"Error deleting document from Firestore: {e}")

    def close(self):
        # Firestore client doesn't have an explicit close method.
        # This is here for conceptual clarity.
        print("Firestore connection conceptually closed.")