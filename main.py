import argparse
import os
import logging
import json
import csv
import re
import shutil
import subprocess
from datetime import datetime
from config import settings
from tools.code_processor import CodeProcessor
from strategies.strategy_factory import get_strategy
from utils.logger import logger
from utils.exceptions import NoRegionTagsError

def get_files_from_csv(csv_path):
    """
    Reads a CSV file of GitHub links, clones the repos, and returns a list of local file paths.
    """
    clone_dir = "temp_clones"
    if os.path.exists(clone_dir):
        shutil.rmtree(clone_dir)
    os.makedirs(clone_dir)

    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        github_links = [row[0] for row in reader]

    repos = set()
    for link in github_links:
        match = re.search(r"https://github.com/([^/]+/[^/]+)", link)
        if match:
            repos.add(match.group(1))

    for repo in repos:
        repo_url = f"https://github.com/{repo}.git"
        target_dir = os.path.join(clone_dir, repo)
        logger.info(f"Cloning {repo_url} into {target_dir}...")
        subprocess.run(["git", "clone", repo_url, target_dir], check=True)

    local_files = []
    for link in github_links:
        match = re.search(r"https://github.com/([^/]+/[^/]+)/blob/([^/]+)/(.+)", link)
        if match:
            repo_name, _, file_path = match.groups()
            local_path = os.path.join(clone_dir, repo_name, file_path)
            if os.path.exists(local_path):
                local_files.append(local_path)
            else:
                logger.warning(f"File not found after cloning: {local_path}")

    return local_files

def main():
    parser = argparse.ArgumentParser(description="Process a code file or directory.")
    parser.add_argument("file_link", nargs='?', default=None, help="Path to the code file or directory.")
    parser.add_argument("--from-csv", help="Path to a CSV file with GitHub links to process.")
    parser.add_argument("--regen", action="store_true", help="Overwrite existing BigQuery entry if true.")
    parser.add_argument("--db", help="BigQuery table name (overrides environment variable).")
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

    # Override the BigQuery table name if provided on the command line.
    if args.db:
        settings.BIGQUERY_TABLE = args.db

    if not args.file_link and not args.reprocess_log and not args.from_csv:
        parser.error("Either file_link, --reprocess-log, or --from-csv is required.")

    # Create a dynamic log file name based on the run parameters.
    source = "csv" if args.from_csv else "reprocess" if args.reprocess_log else "dir" if os.path.isdir(args.file_link) else "file"
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
    if args.from_csv:
        files_to_process = get_files_from_csv(args.from_csv)
    elif args.reprocess_log:
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
