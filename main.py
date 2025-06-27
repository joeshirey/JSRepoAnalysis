import argparse
import os
from dotenv import load_dotenv
from code_processor import CodeProcessor
from strategies.strategy_factory import get_strategy

def main():
    load_dotenv(override=True)
    parser = argparse.ArgumentParser(description="Process a code file or directory.")
    parser.add_argument("file_link", help="Path to the code file or directory.")
    parser.add_argument("--regen", action="store_true", help="Overwrite existing Firestore entry if true.")
    parser.add_argument("--db", nargs='?', const=None, help="Firestore database name (overrides environment variable).")
    args = parser.parse_args()

    processor = CodeProcessor(db_name=args.db)
    try:
        if os.path.isfile(args.file_link):
            print(f"Processing file: {args.file_link}")
            processor.process_file(args.file_link, regen=args.regen)
        elif os.path.isdir(args.file_link):
            print(f"Processing directory: {args.file_link}")
            for root, dirs, files in os.walk(args.file_link):
                for file in files:
                    file_path = os.path.join(root, file)
                    if get_strategy(file_path):
                        print(f"Processing file: {file_path}")
                        processor.process_file(file_path, regen=args.regen)
        else:
            print(f"Error: Invalid path provided: {args.file_link}")
    finally:
        processor.close()

if __name__ == "__main__":
    main()
