# Technical Design Document: Code Quality Analyzer

## 1. Introduction

This document outlines the technical design and architecture of the Code Quality Analyzer. It is intended for engineers who need to understand, maintain, or extend the system.

## 2. Architecture and System Design

The system is a monolithic Python application designed to be run from the command line. It takes a file path, a directory path, a CSV file of GitHub links, or a log file as input, orchestrates a series of processing steps, and uses BigQuery as its data backend.

### Core Components

*   **`main.py`**: The main entry point and orchestrator of the application. It handles command-line argument parsing (`argparse`), file system traversal (`os.walk`), and calls the `CodeProcessor`. It also includes a special `--eval-only` mode for quickly analyzing a single file without database interaction.
*   **`get_files_from_csv`**: This function, located in `main.py`, is responsible for processing a CSV file of GitHub links. It reads the CSV, extracts the repository names, and then uses a `ThreadPoolExecutor` to clone or update the repositories in parallel. It now dynamically determines the default branch of each repository by calling `git remote show` and parsing the output, which makes the cloning process more robust and avoids errors when a repository's default branch is not named `main`.
*   **`tools/code_processor.py`**: The `CodeProcessor` class is the core of the application, responsible for orchestrating the analysis of a single file. It is composed of smaller, more focused components and supports lazy initialization of the Firestore repository.
*   **`strategies/`**: This directory contains the language-specific logic.
    *   **`strategy_factory.py`**: A factory function that returns a `LanguageStrategy` instance based on the file extension.
    *   **`language_strategy.py`**: A single, generic strategy class that is initialized with the language name and uses the `CodeEvaluator` to perform the analysis.
*   **`tools/`**: This directory contains the core logic of the application, separated into distinct modules.
    *   **`git_file_processor.py`**: Contains the `GitFileProcessor` class, which uses the `git` command-line tool via `subprocess` to extract metadata about a file.
    *   **`extract_region_tags.py`**: Contains the `RegionTagExtractor` class, which reads a file and uses regular expressions to find and extract all Google Cloud-style region tags.
    *   **`evaluate_code_file.py`**: Contains the `CodeEvaluator` class, which is responsible for the AI-powered analysis. It reads a prompt template from the `prompts/` directory, injects the code into the prompt, and uses the `vertexai` library to call the configured Gemini model.
    *   **`bigquery.py`**: Contains the `BigQueryRepository` class, which encapsulates all interactions with the BigQuery table.
*   **`utils/`**: This directory contains utility modules.
    *   **`logger.py`**: Configures a centralized logger for the application.
    *   **`exceptions.py`**: Defines custom exception classes for the application.
    *   **`data_classes.py`**: Defines the `AnalysisResult` data class, which provides a structured way to store the analysis results.
*   **`prompts/`**: This directory contains the text files used as templates for the AI evaluation prompts.
*   **`config.py`**: This file uses `pydantic-settings` to load environment variables from the `.env` file into a `Settings` object. The key variables are `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `VERTEXAI_MODEL_NAME`, `BIGQUERY_DATASET`, and `BIGQUERY_TABLE`.

### BigQuery Schema

The application uses a structured BigQuery table and a flattened view to store and analyze the data. The SQL definitions are located in the `BQ/` directory.

*   **`repo_analysis` (Table)**: This is the main table where all the raw analysis data is stored. It is designed to be write-efficient and uses a structured schema with top-level columns for frequently queried fields like `github_link`, `product_category`, and `language`. Complex, semi-structured data, such as the full commit history and the detailed evaluation results from the AI model, are stored in `JSON` columns. This design provides a good balance between query performance and the flexibility to handle evolving data from the AI model.

*   **`repo_analysis_view` (View)**: This view is the recommended interface for data analysis and visualization. It provides a clean, flattened representation of the data by:
    1.  Unnesting the `criteria_breakdown` from the `evaluation_data` JSON column to expose each criterion's score and assessment as a top-level column.
    2.  Using a `ROW_NUMBER()` window function to de-duplicate the records, ensuring that only the most recent evaluation for each unique `github_link` is included in the view. This provides a stable and reliable dataset for building dashboards and performing analysis.

## 3. Data Flow

1.  The user executes `main.py`, providing a file path, a directory path, a CSV of GitHub links, or a log file to reprocess.
2.  `main.py` parses the arguments and gathers a list of files to process.
3.  If the `--from-csv` flag is used, the `get_files_from_csv` function is called to clone or update the repositories.
4.  The `CodeProcessor` is initialized.
5.  For each file in the list:
    a.  The `CodeProcessor` calls the `strategy_factory` to get the appropriate `LanguageStrategy`.
    b.  It then calls the various tools to extract Git info, region tags, and perform the AI evaluation.
    c.  The results are stored in an `AnalysisResult` data class.
    d.  The `BigQueryRepository` is used to save the `AnalysisResult` to BigQuery.
6.  If any errors occur during processing, they are logged to a dynamically named log file in the `logs/` directory.

## 4. Key Technologies

*   **Language:** Python 3
*   **Command-Line Parsing:** `argparse`
*   **AI/LLM:** Google Gemini, via the `google-cloud-aiplatform` SDK.
*   **Database:** Google Cloud BigQuery
*   **Configuration:** `pydantic-settings` for managing environment variables.
*   **Version Control Integration:** `git` (via `subprocess`).
*   **Parallel Processing**: `ThreadPoolExecutor` for cloning and processing files in parallel.

## 5. Future Considerations

*   **Decoupling from Git:** The system currently requires the files to be within a Git repository to function correctly. This could be made optional to allow analysis of arbitrary, non-versioned code.
