import argparse
import os
from config import Config
from code_processor import CodeProcessor
from strategies.strategy_factory import get_strategy
from utils.logger import logger

def main():
    parser = argparse.ArgumentParser(description="Process a code file or directory.")
    parser.add_argument("file_link", help="Path to the code file or directory.")
    parser.add_argument("--regen", action="store_true", help="Overwrite existing Firestore entry if true.")
    parser.add_argument("--db", nargs='?', const=None, help="Firestore database name (overrides environment variable).")
    args = parser.parse_args()

    config = Config(db_name=args.db)

    processor = CodeProcessor(config)
    try:
        if os.path.isfile(args.file_link):
            logger.info(f"Processing file: {args.file_link}")
            try:
                processor.process_file(args.file_link, regen=args.regen)
            except Exception as e:
                logger.error(f"Error processing file {args.file_link}: {e}")
        elif os.path.isdir(args.file_link):
            logger.info(f"Processing directory: {args.file_link}")
            for root, dirs, files in os.walk(args.file_link):
                for file in files:
                    file_path = os.path.join(root, file)
                    if get_strategy(file_path, config):
                        logger.info(f"Processing file: {file_path}")
                        try:
                            processor.process_file(file_path, regen=args.regen)
                        except Exception as e:
                            logger.error(f"Error processing file {file_path}: {e}")
        else:
            logger.error(f"Error: Invalid path provided: {args.file_link}")
    finally:
        processor.close()

if __name__ == "__main__":
    main()
