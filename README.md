# Code Quality Analyzer

This tool analyzes a local codebase of Javascript, Python, Java, Go, Rust, Ruby, C#, C++, and PHP files, performs an AI-powered quality evaluation, and stores the results in a BigQuery table.

## Documentation

For a full understanding of the project's purpose, architecture, and how to contribute, please see the documentation in the `docs/` directory:

*   **[Product Requirements Document](./docs/PRODUCT_REQUIREMENTS.md)**
*   **[Technical Design Document](./docs/TECHNICAL_DESIGN.md)**

## Setup and Installation

### 1. Prerequisites

*   Python 3.9+
*   Google Cloud SDK installed and authenticated (`gcloud auth application-default login`)

### 2. Clone the Repository

```sh
git clone https://github.com/joeshirey/JSRepoAnalysis.git
cd JSRepoAnalysis
```

### 3. Install Dependencies

It is recommended to use a Python virtual environment.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure Environment Variables

The tool uses a `.env` file to manage configuration.

1.  Copy the example file:
    ```sh
    cp .env.sample .env
    ```
2.  Edit the `.env` file and provide values for the following variables:
    *   `GOOGLE_CLOUD_PROJECT`: Your Google Cloud Project ID.
    *   `GOOGLE_CLOUD_LOCATION`: The Google Cloud region for Vertex AI (e.g., `us-central1`).
    *   `VERTEXAI_MODEL_NAME`: The name of the Gemini model to use (e.g., `gemini-1.5-flash-001`).
    *   `BIGQUERY_DATASET`: The name of the BigQuery dataset to use.
    *   `BIGQUERY_TABLE`: The name of the BigQuery table to use.
    *   `GOOGLE_GENAI_USE_VERTEXAI`: Set to `True` to use Vertex AI.

## How to Run

The tool can analyze a single file, an entire directory, or reprocess files from an error log.

### Analyze a Single File or Directory

```sh
# Analyze a single file
python main.py /path/to/your/file.js

# Analyze a directory
python main.py /path/to/your/directory/
```

### Evaluate a Single File

To quickly evaluate a single file and print the results to the console without saving them to Firestore, use the `--eval_only` flag:

```sh
python main.py --eval_only /path/to/your/file.js
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

*   `file_link`: (Optional) The path to the code file or directory to analyze.
*   `--regen`: Forces the tool to re-analyze files and update the corresponding record in BigQuery.
*   `--db <table_name>`: Overrides the `BIGQUERY_TABLE` environment variable.
*   `--reprocess-log <log_file_path>`: Reprocesses files listed in the specified error log.
*   `--eval_only`: Analyzes a single file and prints the results to the console without saving to BigQuery.

## Project Structure

*   `main.py`: The main entry point for the command-line tool.
*   `config.py`: Manages environment variables and configuration settings.
*   `setup.py`: The setup script for the project, used for packaging and distribution.
*   `docs/`: Contains the Product Requirements and Technical Design documents.
*   `strategies/`: Contains the language-specific analysis strategies.
*   `tools/`: Contains the core logic for file processing, Git integration, and AI evaluation.
*   `utils/`: Contains utility modules for logging, exception handling, and data classes.
*   `prompts/`: Contains the text files used as templates for the AI evaluation prompts.
