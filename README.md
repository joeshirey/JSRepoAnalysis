# Code Quality Analyzer

This tool analyzes a local codebase of Javascript, Python, Java, Go, Rust, Ruby, C#, C++, PHP, and Terraform files, performs an AI-powered quality evaluation, and stores the results in a BigQuery table.

## Documentation

For a full understanding of the project's purpose, architecture, and how to contribute, please see the documentation in the `docs/` directory:

* **[Product Requirements Document](./docs/PRODUCT_REQUIREMENTS.md)**
* **[Technical Design Document](./docs/TECHNICAL_DESIGN.md)**

## Setup and Installation

### Prerequisites

* Python 3.9+
* Google Cloud SDK installed and authenticated (`gcloud auth application-default login`)

### Clone the Repository

```sh
git clone https://github.com/joeshirey/JSRepoAnalysis.git
cd JSRepoAnalysis
```

### Install Dependencies

It's recommended to use a Python virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure Environment Variables

The tool uses a `.env` file to manage configuration:

1. **Copy the example file:**

    ```sh
    cp .env.sample .env
    ```

2. **Edit the `.env` file** and provide values for the following:
    * `GOOGLE_CLOUD_PROJECT`: Your Google Cloud Project ID.
    * `GOOGLE_CLOUD_LOCATION`: The Google Cloud region for Vertex AI (e.g., `us-central1`).
    * `VERTEXAI_MODEL_NAME`: The Gemini model to use (e.g., `gemini-1.5-flash-001`).
    * `BIGQUERY_DATASET`: The name of your BigQuery dataset.
    * `BIGQUERY_TABLE`: The name of your BigQuery table.
    * `GOOGLE_GENAI_USE_VERTEXAI`: Set to `True` to use Vertex AI.
    * `REPO_SAMPLES_DIR`: The local directory for cloning repositories from the CSV file (defaults to `~/samples`).

## BigQuery Schema

The SQL definitions for the BigQuery table and the recommended analysis view are located in the `BQ/` directory.

* **`create_table.sql`**: Contains the `CREATE OR REPLACE TABLE` statement for the main data table (`repo_analysis`). This table is structured with top-level columns for efficient querying and filtering, while storing complex, nested data (like commit history and evaluation results) as `JSON`.
* **`create_view.sql`**: Contains the `CREATE OR REPLACE VIEW` statement for the recommended analysis view (`repo_analysis_view`). This view flattens the JSON data from the main table, unnests the evaluation criteria, and ensures that only the most recent evaluation for each file is shown, providing a simplified and reliable data source for dashboards and analysis.

## How to Run

The tool can analyze a single file, an entire directory, a CSV of GitHub links, or reprocess files from an error log.

### Analyze a Single File or Directory

```sh
# Analyze a single file
python main.py /path/to/your/file.js

# Analyze a directory
python main.py /path/to/your/directory/
```

### Analyze from a CSV

To analyze a list of files from a CSV, use the `--from-csv` flag. The tool will clone the repositories if they don't exist, or pull the latest changes if they do. It now automatically detects the default branch of each repository.

```sh
python main.py --from-csv inventory.csv
```

### Evaluate a Single File

To quickly evaluate a single file and print the results to the console without saving them to BigQuery, use the `--eval-only` flag:

```sh
python main.py --eval-only /path/to/your/file.js
```

### Reprocessing Errored Files

If any files fail during a run, an error log will be created in the `logs/` directory. You can reprocess these files using the `--reprocess-log` flag:

```sh
python main.py --reprocess-log logs/errors_2025-06-27.log
```

You can also combine this with other flags, which will be applied to all files in the log:

```sh
python main.py --reprocess-log logs/errors_2025-06-27.log --regen --db "my-other-db"
```

## Command-Line Arguments

* `file_link`: (Optional) The path to the code file or directory to analyze.
* `--from-csv`: (Optional) The path to a CSV file with GitHub links to process.
* `--regen`: Forces the tool to re-analyze files and update the corresponding record in BigQuery.
* `--db <table_name>`: Overrides the `BIGQUERY_TABLE` environment variable.
* `--reprocess-log <log_file_path>`: Reprocesses files listed in the specified error log.
* `--eval-only`: Analyzes a single file and prints the results to the console without saving to BigQuery.
* `--workers`: The number of parallel threads to use for cloning and processing.

## Project Structure

* `main.py`: Main entry point for the command-line tool.
* `config.py`: Manages environment variables and configuration.
* `setup.py`: Setup script for packaging and distribution.
* `docs/`: Contains Product Requirements and Technical Design documents.
* `strategies/`: Contains language-specific analysis strategies.
* `tools/`: Core logic for file processing, Git integration, and AI evaluation.
* `utils/`: Utility modules for logging, exceptions, and data classes.
* `prompts/`: Templates for AI evaluation prompts.
* `inventory.csv`: Sample CSV file for use with the `--from-csv` flag.
