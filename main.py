import argparse
import os
import logging
import json
import csv
import re
import shutil
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from config import settings
from tools.code_processor import CodeProcessor
from strategies.strategy_factory import get_strategy
from utils.logger import logger
from utils.exceptions import NoRegionTagsError

def get_files_from_csv(csv_path, max_workers):
    """
    Reads a CSV file of GitHub links, clones or updates the repos in parallel, 
    and returns a list of local file paths.
    """
    clone_dir = os.environ.get("REPO_SAMPLES_DIR", "/Users/joeshirey/samples")
    if not os.path.exists(clone_dir):
        os.makedirs(clone_dir)

    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        github_links = [row[2] for row in reader]

    repos = set()
    for link in github_links:
        match = re.search(r"https://github.com/([^/]+/[^/]+)", link)
        if match:
            repos.add(match.group(1))

    def get_default_branch(repo_url):
        try:
            result = subprocess.run(["git", "remote", "show", repo_url], check=True, capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if 'HEAD branch' in line:
                    return line.split(': ')[1]
            return 'main' # Fallback
        except subprocess.CalledProcessError as e:
            logger.error(f"Could not determine default branch for {repo_url}: {e.stderr}")
            return 'main' # Fallback

    def clone_or_update_repo(repo):
        repo_url = f"https://github.com/{repo}.git"
        target_dir = os.path.join(clone_dir, repo)
        
        try:
            if os.path.exists(target_dir):
                logger.info(f"Repository {repo} already exists. Pulling latest changes...")
                default_branch = get_default_branch(repo_url)
                subprocess.run(["git", "-C", target_dir, "checkout", default_branch], check=True, capture_output=True, text=True)
                subprocess.run(["git", "-C", target_dir, "pull"], check=True, capture_output=True, text=True)
            else:
                logger.info(f"Cloning {repo_url} into {target_dir}...")
                subprocess.run(["git", "clone", repo_url, target_dir], check=True, capture_output=True, text=True)
            return f"Successfully processed {repo}"
        except subprocess.CalledProcessError as e:
            return f"Error processing repository {repo}: {e.stderr}"
        except Exception as e:
            return f"An unexpected error occurred with repository {repo}: {e}"

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_repo = {executor.submit(clone_or_update_repo, repo): repo for repo in repos}
        for future in as_completed(future_to_repo):
            repo = future_to_repo[future]
            try:
                result = future.result()
                logger.info(result)
            except Exception as exc:
                logger.error(f'{repo} generated an exception: {exc}')

    local_files = []
    for link in github_links:
        match = re.search(r"https://github.com/([^/]+/[^/]+)/blob/[^/]+/(.+)", link)
        if match:
            repo_name, file_path = match.groups()
            file_path = file_path.split('#')[0]
            local_path = os.path.join(clone_dir, repo_name, file_path)
            if os.path.exists(local_path):
                local_files.append(local_path)
            else:
                logger.warning(f"File not found after cloning: {local_path}")

    return local_files

def process_file_wrapper(processor, file_path, regen, error_logger, processed_counts, skipped_counts, errored_counts):
    file_extension = os.path.splitext(file_path)[1]
    strategy = get_strategy(file_path, settings)
    
    if strategy:
        try:
            logger.info(f"Processing file: {file_path}")
            processor.process_file(file_path, regen=regen)
            processed_counts[file_extension] += 1
            logger.info(f"Finished processing file: {file_path}")
        except NoRegionTagsError as e:
            logger.info(f"Skipping file {file_path}: {e}")
            skipped_counts[file_extension] += 1
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            error_logger.error(file_path)
            errored_counts[file_extension] += 1
    else:
        logger.info(f"Skipping unsupported file type: {file_path}")
        skipped_counts[file_extension] += 1

def main():
    parser = argparse.ArgumentParser(description="Process a code file or directory.")
    parser.add_argument("file_link", nargs='?', default=None, help="Path to the code file or directory.")
    parser.add_argument("--from-csv", help="Path to a CSV file with GitHub links to process.")
    parser.add_argument("--regen", action="store_true", help="Overwrite existing BigQuery entry if true.")
    parser.add_argument("--db", help="BigQuery table name (overrides environment variable).")
    parser.add_argument("--reprocess-log", help="Path to a log file to reprocess.")
    parser.add_argument("--eval-only", action="store_true", help="Only evaluate a single file and print the result.")
    parser.add_argument("--workers", type=int, default=10, help="Number of parallel threads to use.")
    args = parser.parse_args()

    if args.eval_only:
        if not args.file_link or not os.path.isfile(args.file_link):
            parser.error("--eval-only requires a single file path.")
        
        processor = CodeProcessor(settings)
        try:
            result = processor.analyze_file_only(args.file_link)
            if result:
                print(json.dumps(result, indent=4))
        except Exception as e:
            logger.error(f"Error during evaluation: {e}")
        return

    if args.db:
        settings.BIGQUERY_TABLE = args.db

    if not any([args.file_link, args.reprocess_log, args.from_csv]):
        parser.error("Either file_link, --reprocess-log, or --from-csv is required.")

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

    files_to_process = []
    if args.from_csv:
        files_to_process = get_files_from_csv(args.from_csv, args.workers)
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
                files_to_process.append(file_path)

    if not files_to_process:
        logger.info("No files to process.")
        return

    processed_counts = defaultdict(int)
    skipped_counts = defaultdict(int)
    errored_counts = defaultdict(int)
    
    processor = CodeProcessor(settings)
    try:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = [executor.submit(process_file_wrapper, processor, file, args.regen, error_logger, processed_counts, skipped_counts, errored_counts) for file in files_to_process]
            for future in as_completed(futures):
                future.result()
    finally:
        processor.close()

    total_processed = sum(processed_counts.values())
    total_skipped = sum(skipped_counts.values())
    total_errored = sum(errored_counts.values())

    logger.info("\n--- Processing Summary ---")
    logger.info(f"Total files processed: {total_processed}")
    if total_processed > 0:
        for ext, count in sorted(processed_counts.items()):
            logger.info(f"  - {ext if ext else 'other'}: {count}")
    
    logger.info(f"\nTotal files skipped: {total_skipped}")
    if total_skipped > 0:
        for ext, count in sorted(skipped_counts.items()):
            logger.info(f"  - {ext if ext else 'other'}: {count}")

    logger.info(f"\nTotal files errored: {total_errored}")
    if total_errored > 0:
        for ext, count in sorted(errored_counts.items()):
            logger.info(f"  - {ext if ext else 'other'}: {count}")
    logger.info("------------------------\n")

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

