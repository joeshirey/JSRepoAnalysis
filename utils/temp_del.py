import os
from tools.firestore import FirestoreClient, read_all_in_collection, delete

def delete_specific_records(collection_name: str, prefix: str):
    """
    Deletes records from a Firestore collection where the document ID starts with a specific prefix.

    Args:
        collection_name: The name of the Firestore collection.
        prefix: The prefix to match for document IDs to be deleted.
    """
    client = FirestoreClient()
    client.open_connection()

    if not client.get_db():
        print("Failed to open Firestore connection. Exiting.")
        return

    print(f"Scanning collection '{collection_name}' for documents starting with '{prefix}'...")
    documents = read_all_in_collection(collection_name)

    if not documents:
        print(f"No documents found in collection '{collection_name}' or an error occurred.")
        client.close_connection()
        return

    deleted_count = 0
    for doc in documents:
        doc_id = doc.get('id')
        if doc_id and doc_id.startswith(prefix):
            print(f"Deleting document: {doc_id}")
            delete(collection_name, doc_id)
            deleted_count += 1
    
    print(f"Finished deleting records. Total deleted: {deleted_count}")
    client.close_connection()

if __name__ == '__main__':
    # Ensure FIRESTORE_PROJECT_ID and FIRESTORE_DB are set in your .env file
    # Example:
    # FIRESTORE_PROJECT_ID=your-project-id
    # FIRESTORE_DB=(default) or your-database-name

    # Replace 'your-collection-name' with the actual name of your Firestore collection
    COLLECTION_NAME = os.getenv("FIRESTORE_COLLECTION_NAME", "Python") 
    PREFIX_TO_DELETE = "https___github_com_googleapis"

    delete_specific_records(COLLECTION_NAME, PREFIX_TO_DELETE)
