import os
from google.cloud import firestore
from typing import Dict, Any, Optional
from utils.logger import logger
from utils.exceptions import FirestoreError

class FirestoreRepository:
    def __init__(self, config):
        self.config = config
        try:
            self._db = firestore.Client(project=self.config.FIRESTORE_PROJECT_ID, database=self.config.FIRESTORE_DB)
            logger.info("Firestore connection opened.")
        except Exception as e:
            raise FirestoreError(f"Error initializing Firestore client: {e}")

    def create(self, collection_name: str, document_id: str, document_payload: Dict[str, Any]):
        """
        Writes a document to a Firestore collection.
        """
        try:
            doc_ref = self._db.collection(collection_name).document(document_id)
            doc_ref.set(document_payload)
            logger.info(f"Successfully wrote document '{document_id}' to project '{self.config.FIRESTORE_PROJECT_ID}', database '{self.config.FIRESTORE_DB}', collection '{collection_name}'.")
        except Exception as e:
            raise FirestoreError(f"Error writing document to Firestore: {e}")

    def read(self, collection_name: str, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Reads a document from a Firestore collection.
        """
        try:
            doc_ref = self._db.collection(collection_name).document(document_id)
            doc = doc_ref.get()
            if doc.exists:
                logger.info(f"Document '{document_id}' successfully read from collection '{collection_name}'.")
                return doc.to_dict()
            else:
                logger.info(f"Document '{document_id}' does not exist in collection '{collection_name}'.")
                return None
        except Exception as e:
            raise FirestoreError(f"Error reading document from Firestore: {e}")

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
            logger.info(f"Successfully read {len(documents_data)} documents from collection '{collection_name}'.")
            return documents_data
        except Exception as e:
            raise FirestoreError(f"Error reading all documents from collection '{collection_name}': {e}")

    def delete(self, collection_name: str, document_id: str):
        """
        Deletes a document from a Firestore collection.
        """
        try:
            self._db.collection(collection_name).document(document_id).delete()
            logger.info(f"Document '{document_id}' successfully deleted from collection '{collection_name}'.")
        except Exception as e:
            raise FirestoreError(f"Error deleting document from Firestore: {e}")

    def close(self):
        # Firestore client doesn't have an explicit close method.
        # This is here for conceptual clarity.
        logger.info("Firestore connection conceptually closed.")