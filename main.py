import argparse
import os
import logging
import json
import csv
import re
import subprocess
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from urllib.parse import urlparse
from tqdm import tqdm
from config import settings
from tools.code_processor import CodeProcessor
from utils.logger import logger


def get_files_from_csv(csv_path, max_workers):
    """
    Reads a CSV file of GitHub links, clones or updates the repos in parallel,
    and returns a list of local file paths.
    """
    clone_dir = os.path.expanduser(os.environ.get("REPO_SAMPLES_DIR", "~/samples"))
    if not os.path.exists(clone_dir):
        os.makedirs(clone_dir)

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        github_links = [row["indexed_source_url"] for row in reader]

    repos = set()
    for link in github_links:
        match = re.search(r"https://github.com/([^/]+/[^/]+)", link)
        if match:
            repos.add(match.group(1))

    def get_default_branch(repo_url):
        try:
            result = subprocess.run(
                ["git", "remote", "show", repo_url],
                check=True,
                capture_output=True,
                text=True,
            )
            for line in result.stdout.splitlines():
                if "HEAD branch" in line:
                    return line.split(": ")[1]
            return "main"  # Fallback
        except subprocess.CalledProcessError as e:
            logger.error(
                f"Could not determine default branch for {repo_url}: {e.stderr}"
            )
            return "main"  # Fallback

    def clone_or_update_repo(repo):
        repo_url = f"https://github.com/{repo}.git"
        target_dir = os.path.join(clone_dir, repo)

        try:
            if os.path.exists(target_dir):
                default_branch = get_default_branch(repo_url)
                subprocess.run(
                    ["git", "-C", target_dir, "checkout", default_branch],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                subprocess.run(
                    ["git", "-C", target_dir, "pull"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            else:
                subprocess.run(
                    ["git", "clone", repo_url, target_dir],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            return f"Successfully processed {repo}"
        except subprocess.CalledProcessError as e:
            return f"Error processing repository {repo}: {e.stderr}"
        except Exception as e:
            return f"An unexpected error occurred with repository {repo}: {e}"

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_repo = {
            executor.submit(clone_or_update_repo, repo): repo for repo in repos
        }
        for future in as_completed(future_to_repo):
            repo = future_to_repo[future]
            try:
                future.result()
            except Exception as exc:
                logger.error(f"{repo} generated an exception: {exc}")

    local_files = []
    for link in github_links:
        try:
            parsed_url = urlparse(link)
            path_parts = parsed_url.path.strip("/").split("/")
            owner, repo_name = path_parts[0], path_parts[1]
            file_path = "/".join(path_parts[4:])

            local_path = os.path.join(clone_dir, owner, repo_name, file_path)
            if os.path.exists(local_path):
                local_files.append(local_path)
            else:
                logger.warning(f"File not found after cloning: {local_path}")
        except IndexError:
            logger.error(f"Could not parse owner, repo, or file path from URL: {link}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while parsing URL {link}: {e}")

    return local_files


def process_file_wrapper(
    processor: CodeProcessor,
    file_path: str,
    regen: bool,
    error_logger: logging.Logger,
    processed_counts: defaultdict,
    skipped_counts: defaultdict,
    errored_counts: defaultdict,
    consecutive_errors: list,
    error_lock: threading.Lock,
):
    """
    Wrapper function to process a single file, handle exceptions, and update counters.
    Invokes the CodeProcessor to perform analysis via an external API.
    """
    file_extension = os.path.splitext(file_path)[1]
    try:
        status = processor.process_file(file_path, regen=regen)
        if status == "processed":
            processed_counts[file_extension] += 1
        elif status == "skipped":
            skipped_counts[file_extension] += 1

        with error_lock:
            consecutive_errors[0] = 0

    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        error_logger.error(file_path)
        errored_counts[file_extension] += 1
        with error_lock:
            consecutive_errors[0] += 1
            if consecutive_errors[0] >= 5:
                logger.warning("Five consecutive errors detected. Pausing execution.")
                user_input = input("Enter 'resume' to continue or 'stop' to abort: ")
                if user_input.lower() == "stop":
                    # A more graceful shutdown might be needed depending on application complexity
                    os._exit(1)
                else:
                    logger.info("Resuming execution.")
                    consecutive_errors[0] = 0


def categorize_file_wrapper(processor, file_path, csv_writer):
    """Wrapper function to process a single file and write to CSV."""
    try:
        result = processor.categorize_file_only(file_path)
        if result:
            csv_writer.writerow(result)
    except Exception as e:
        logger.error(f"Error categorizing file {file_path}: {e}")


def categorize_only(input_path, max_workers):
    """
    Processes files for categorization only and writes the output to a CSV file.
    """
    now = datetime.now().strftime("%Y-%m-%d-%H-%M")
    output_filename = f"{now} - categorization.csv"
    output_path = os.path.join("logs", output_filename)

    os.makedirs("logs", exist_ok=True)

    files_to_process = []
    if os.path.isfile(input_path):
        if input_path.endswith(".csv"):
            files_to_process = get_files_from_csv(input_path, max_workers)
        else:
            files_to_process.append(input_path)
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for file in files:
                files_to_process.append(os.path.join(root, file))

    if not files_to_process:
        logger.info("No files to process.")
        return

    processor = CodeProcessor(settings)
    try:
        with open(output_path, "w", newline="") as csvfile:
            fieldnames = [
                "indexed_source_url",
                "region_tag",
                "repository_name",
                "product_category",
                "product_name",
                "llm_determined",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(categorize_file_wrapper, processor, file, writer)
                    for file in files_to_process
                }
                for future in tqdm(
                    as_completed(futures), total=len(futures), desc="Categorizing files"
                ):
                    future.result()

    finally:
        processor.close()
        print()  # Newline after progress bar

    logger.info(f"Categorization complete. Output written to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Process a code file or directory.")
    parser.add_argument(
        "file_link", nargs="?", default=None, help="Path to the code file or directory."
    )

    parser.add_argument(
        "--from-csv", help="Path to a CSV file with GitHub links to process."
    )
    parser.add_argument(
        "--regen",
        action="store_true",
        help="Overwrite existing BigQuery entry if true.",
    )
    parser.add_argument(
        "--db", help="BigQuery table name (overrides environment variable)."
    )
    parser.add_argument("--reprocess-log", help="Path to a log file to reprocess.")
    parser.add_argument(
        "--eval-only",
        action="store_true",
        help="Only evaluate a single file and print the result.",
    )
    parser.add_argument(
        "--categorize-only",
        action="store_true",
        help="Run in categorization-only mode.",
    )
    parser.add_argument(
        "--workers", type=int, default=10, help="Number of parallel threads to use."
    )
    args = parser.parse_args()

    if args.categorize_only:
        input_path = args.from_csv or args.file_link
        if not input_path:
            parser.error(
                "--categorize-only requires an input path from --from-csv or file_link."
            )
        categorize_only(input_path, args.workers)
        return

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

    source = (
        "csv"
        if args.from_csv
        else "reprocess"
        if args.reprocess_log
        else "dir"
        if os.path.isdir(args.file_link)
        else "file"
    )
    log_filename_parts = [datetime.now().strftime("%Y%m%d-%H%M%S"), source]
    if args.regen:
        log_filename_parts.append("regen")
    if args.db:
        log_filename_parts.append(args.db)
    log_filename = "_".join(log_filename_parts) + ".log"

    error_log_path = os.path.join("logs", log_filename)
    os.makedirs(os.path.dirname(error_log_path), exist_ok=True)
    error_logger = logging.getLogger("error_logger")
    error_logger.setLevel(logging.ERROR)
    error_handler = logging.FileHandler(error_log_path)
    error_handler.setFormatter(logging.Formatter("%(message)s"))
    error_logger.addHandler(error_handler)

    files_to_process = []
    if args.from_csv:
        files_to_process = get_files_from_csv(args.from_csv, args.workers)
    elif args.reprocess_log:
        try:
            with open(args.reprocess_log, "r") as f:
                files_to_process = [line.strip() for line in f if line.strip()]
            logger.info(
                f"Reprocessing {len(files_to_process)} files from {args.reprocess_log}"
            )
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
    consecutive_errors = [0]
    error_lock = threading.Lock()

    processor = CodeProcessor(settings)
    try:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(
                    process_file_wrapper,
                    processor,
                    file,
                    args.regen,
                    error_logger,
                    processed_counts,
                    skipped_counts,
                    errored_counts,
                    consecutive_errors,
                    error_lock,
                )
                for file in files_to_process
            }
            for future in tqdm(
                as_completed(futures), total=len(futures), desc="Processing files"
            ):
                future.result()
    finally:
        processor.close()
        print()  # Newline after progress bar

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
        archive_path = os.path.join(
            "logs", "archive", os.path.basename(args.reprocess_log)
        )
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        os.rename(args.reprocess_log, archive_path)
        logger.info(f"Archived log file to {archive_path}")

    if os.path.exists(error_log_path) and os.path.getsize(error_log_path) == 0:
        os.remove(error_log_path)
        logger.info("No errors, removing empty log file.")
    elif os.path.exists(error_log_path):
        logger.info(f"Errors were encountered. See {error_log_path} for details.")
        reprocess = input("Would you like to reprocess the failed files? (y/n): ")
        if reprocess.lower() == "y":
            print("\nTo reprocess, run the following command:")
            print(f"uv run main.py --reprocess-log {error_log_path} --regen")


if __name__ == "__main__":
    main()
