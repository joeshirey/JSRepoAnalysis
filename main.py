import argparse
import os
import logging
import json
from datetime import datetime
from config import settings
from tools.code_processor import CodeProcessor
from strategies.strategy_factory import get_strategy
from utils.logger import logger
from utils.exceptions import NoRegionTagsError

def main():
    parser = argparse.ArgumentParser(description="Process a code file or directory.")
    parser.add_argument("file_link", nargs='?', default=None, help="Path to the code file or directory.")
    parser.add_argument("--regen", action="store_true", help="Overwrite existing Firestore entry if true.")
    parser.add_argument("--db", help="Firestore database name (overrides environment variable).")
    parser.add_argument("--reprocess-log", help="Path to a log file to reprocess.")
    parser.add_argument("--eval_only", action="store_true", help="Only evaluate a single file and print the result.")
    args = parser.parse_args()

    # If in evaluation-only mode, process a single file and exit.
    if args.eval_only:
        if not args.file_link or not os.path.isfile(args.file_link):
            parser.error("--eval_only requires a single file path.")
        
        processor = CodeProcessor(settings)
        try:
            result = processor.analyze_file_only(args.file_link)
            if result:
                print(json.dumps(result, indent=4))
        except Exception as e:
            logger.error(f"Error during evaluation: {e}")
        return

    # Override the Firestore database name if provided on the command line.
    if args.db:
        settings.FIRESTORE_DB = args.db

    if not args.file_link and not args.reprocess_log:
        parser.error("Either file_link or --reprocess-log is required.")

    # Create a dynamic log file name based on the run parameters.
    source = "reprocess" if args.reprocess_log else "dir" if os.path.isdir(args.file_link) else "file"
    log_filename_parts = [datetime.now().strftime("%Y%m%d-%H%M%S"), source]
    if args.regen:
        log_filename_parts.append("regen")
    if args.db:
        log_filename_parts.append(args.db)
    log_filename = "_".join(log_filename_parts) + ".log"
    
    error_log_path = os.path.join("logs", log_filename)
    error_logger = logging.getLogger('error_logger')
    error_logger.setLevel(logging.ERROR)
    error_handler = logging.FileHandler(error_log_path)
    error_handler.setFormatter(logging.Formatter('%(message)s'))
    error_logger.addHandler(error_handler)

    # Gather the list of files to process from the specified source.
    files_to_process = []
    if args.reprocess_log:
        try:
            with open(args.reprocess_log, 'r') as f:
                files_to_process = [line.strip() for line in f if line.strip()]
            logger.info(f"Reprocessing {len(files_to_process)} files from {args.reprocess_log}")
        except FileNotFoundError:
            logger.error(f"Error: Log file not found at {args.reprocess_log}")
            return
    elif os.path.isfile(args.file_link):
        files_to_process.append(args.file_link)
    elif os.path.isdir(args.file_link):
        for root, _, files in os.walk(args.file_link):
            for file in files:
                file_path = os.path.join(root, file)
                if get_strategy(file_path, settings):
                    files_to_process.append(file_path)

    if not files_to_process:
        logger.info("No files to process.")
        return

    # Process all files in a single session to avoid repeated connections.
    processor = CodeProcessor(settings)
    total_files = len(files_to_process)
    try:
        for i, file_path in enumerate(files_to_process):
            try:
                logger.info(f"Processing file {i+1}/{total_files}: {file_path}")
                processor.process_file(file_path, regen=args.regen)
            except NoRegionTagsError as e:
                logger.info(f"Skipping file {file_path}: {e}")
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                error_logger.error(file_path)
    finally:
        processor.close()

    if args.reprocess_log:
        archive_path = os.path.join("logs", "archive", os.path.basename(args.reprocess_log))
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        os.rename(args.reprocess_log, archive_path)
        logger.info(f"Archived log file to {archive_path}")
    
    if os.path.exists(error_log_path) and os.path.getsize(error_log_path) == 0:
        os.remove(error_log_path)
        logger.info("No errors, removing empty log file.")
    elif os.path.exists(error_log_path):
        logger.info(f"Errors were encountered. See {error_log_path} for details.")
        reprocess = input("Would you like to reprocess the failed files? (y/n): ")
        if reprocess.lower() == 'y':
            print(f"\nTo reprocess, run the following command:")
            print(f"uv run main.py --reprocess-log {error_log_path} --regen")

if __name__ == "__main__":
    main()
