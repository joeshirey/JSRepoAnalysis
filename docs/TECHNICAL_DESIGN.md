# Technical Design Document: Code Quality Analyzer

## 1. Introduction

This document outlines the technical design and architecture of the Code Quality Analyzer. It is intended for engineers who need to understand, maintain, or extend the system.

## 2. Architecture and System Design

The system is a monolithic Python application designed to be run from the command line. It takes a file path, a directory path, or a log file as input, orchestrates a series of processing steps, and uses Firestore as its data backend.

### Core Components

*   **`main.py`**: The main entry point and orchestrator of the application. It handles command-line argument parsing (`argparse`), file system traversal (`os.walk`), and calls the `CodeProcessor`. It also includes a special `--eval_only` mode for quickly analyzing a single file without database interaction.
*   **`tools/code_processor.py`**: The `CodeProcessor` class is the core of the application, responsible for orchestrating the analysis of a single file. It is composed of smaller, more focused components and supports lazy initialization of the Firestore repository.
*   **`strategies/`**: This directory contains the language-specific logic.
    *   **`strategy_factory.py`**: A factory function that returns a `LanguageStrategy` instance based on the file extension.
    *   **`language_strategy.py`**: A single, generic strategy class that is initialized with the language name and uses the `CodeEvaluator` to perform the analysis.
*   **`tools/`**: This directory contains the core logic of the application, separated into distinct modules.
    *   **`git_file_processor.py`**: Contains the `GitFileProcessor` class, which uses the `git` command-line tool via `subprocess` to extract metadata about a file.
    *   **`extract_region_tags.py`**: Contains the `RegionTagExtractor` class, which reads a file and uses regular expressions to find and extract all Google Cloud-style region tags.
    *   **`evaluate_code_file.py`**: Contains the `CodeEvaluator` class, which is responsible for the AI-powered analysis. It reads a prompt template from the `prompts/` directory, injects the code into the prompt, and uses the `vertexai` library to call the configured Gemini model.
    *   **`firestore.py`**: Contains the `FirestoreRepository` class, which encapsulates all interactions with the Firestore database.
*   **`utils/`**: This directory contains utility modules.
    *   **`logger.py`**: Configures a centralized logger for the application.
    *   **`exceptions.py`**: Defines custom exception classes for the application.
    *   **`data_classes.py`**: Defines the `AnalysisResult` data class, which provides a structured way to store the analysis results.
*   **`prompts/`**: This directory contains the text files used as templates for the AI evaluation prompts.
*   **`.env`**: This file is used to store environment variables, which are loaded at runtime using `python-dotenv`.

## 3. Data Flow

1.  The user executes `main.py`, providing a file path, a directory path, or a log file to reprocess.
2.  `main.py` parses the arguments and gathers a list of files to process.
3.  The `CodeProcessor` is initialized.
4.  For each file in the list:
    a.  The `CodeProcessor` calls the `strategy_factory` to get the appropriate `LanguageStrategy`.
    b.  It then calls the various tools to extract Git info, region tags, and perform the AI evaluation.
    c.  The results are stored in an `AnalysisResult` data class.
    d.  The `FirestoreRepository` is used to save the `AnalysisResult` to Firestore.
5.  If any errors occur during processing, they are logged to a dynamically named log file in the `logs/` directory.

## 4. Key Technologies

*   **Language:** Python 3
*   **Command-Line Parsing:** `argparse`
*   **AI/LLM:** Google Gemini, via the `google-cloud-aiplatform` SDK.
*   **Database:** Google Cloud Firestore
*   **Configuration:** `python-dotenv` for managing environment variables.
*   **Version Control Integration:** `git` (via `subprocess`).

## 5. Future Considerations

*   **Batch Processing:** For very large codebases, the current sequential processing could be slow. The system could be refactored to use a `ThreadPoolExecutor` to process files in parallel.
*   **Decoupling from Git:** The system currently requires the files to be within a Git repository to function correctly. This could be made optional to allow analysis of arbitrary, non-versioned code.
