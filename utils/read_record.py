#!/usr/bin/env python3
import argparse
import json
import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.firestore import FirestoreRepository
from config import Config

def main():
    load_dotenv() # Load environment variables from .env file

    parser = argparse.ArgumentParser(description="Read a document from Firestore.")
    parser.add_argument("collection_name", help="The name of the Firestore collection.")
    parser.add_argument("document_id", help="The ID of the document to read.")
    args = parser.parse_args()

    config = Config()
    firestore_repo = FirestoreRepository(config)
    document = firestore_repo.read(args.collection_name, args.document_id)

    if document:
        print(json.dumps(document, indent=4))
    else:
        print(f"Document not found in collection '{args.collection_name}' with ID '{args.document_id}'.")

if __name__ == "__main__":
    main()
