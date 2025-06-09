import argparse
import json
from tools.firestore import read
from dotenv import load_dotenv
import os

def main():
    load_dotenv() # Load environment variables from .env file

    parser = argparse.ArgumentParser(description="Read a document from Firestore.")
    parser.add_argument("collection_name", help="The name of the Firestore collection.")
    parser.add_argument("document_id", help="The ID of the document to read.")
    args = parser.parse_args()

    document = read(args.collection_name, args.document_id)

    if document:
        print(json.dumps(document, indent=4))
    else:
        print(f"Document not found in collection '{args.collection_name}' with ID '{args.document_id}'.")

if __name__ == "__main__":
    main()
