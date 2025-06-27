import argparse
import os
import logging
from datetime import datetime
from config import settings
from tools.code_processor import CodeProcessor
from strategies.strategy_factory import get_strategy
from utils.logger import logger

def main():
    parser = argparse.ArgumentParser(description="Process a code file or directory.")
    parser.add_argument("file_link", nargs='?', default=None, help="Path to the code file or directory.")
    parser.add_argument("--regen", action="store_true", help="Overwrite existing Firestore entry if true.")
    parser.add_argument("--db", help="Firestore database name (overrides environment variable).")
    parser.add_argument("--reprocess-log", help="Path to a log file to reprocess.")
    args = parser.parse_args()

    if not args.file_link and not args.reprocess_log:
        parser.error("Either file_link or --reprocess-log is required.")

    log_filename_parts = ["errors", datetime.now().strftime("%Y-%m-%d")]
    if args.regen:
        log_filename_parts.append("regen")
    if args.db:
        log_filename_parts.append(args.db)
    log_filename = "_".join(log_filename_parts) + ".log"
    
    error_log_path = os.path.join("logs", log_filename)
    file_handler = logging.FileHandler(error_log_path)
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    logger.addHandler(file_handler)

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

    processor = CodeProcessor(settings)
    try:
        for file_path in files_to_process:
            try:
                logger.info(f"Processing file: {file_path}")
                processor.process_file(file_path, regen=args.regen)
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                with open(error_log_path, 'a') as f:
                    f.write(f"{file_path}\n")
    finally:
        processor.close()

if __name__ == "__main__":
    main()
