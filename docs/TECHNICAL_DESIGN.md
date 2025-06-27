# Technical Design Document: JS/Python Codebase Analyzer

## 1. Introduction

This document outlines the technical design and architecture of the JS/Python Codebase Analyzer. It is intended for engineers who need to understand, maintain, or extend the system.

## 2. Architecture and System Design

The system is a monolithic Python application designed to be run from the command line. It takes a file or directory path as input, orchestrates a series of processing steps, and uses Firestore as its data backend.

### Core Components

*   **`main.py`**: The main entry point and orchestrator of the application. It handles command-line argument parsing (`argparse`), file system traversal (`os.walk`), and calls the various processing tools.
*   **`tools/`**: This directory contains the core logic of the application, separated into distinct modules.
    *   **`git_file_processor.py`**: Contains the `get_git_data` function, which uses the `git` command-line tool via `subprocess` to extract metadata about a file, including its last commit date and its URL on GitHub.
    *   **`extract_region_tags.py`**: Contains the `extract_region_tags` function, which reads a file and uses regular expressions to find and extract all Google Cloud-style region tags.
    *   **`evaluate_code_file.py`**: Contains the `evaluate_code` function, which is responsible for the AI-powered analysis. It reads a prompt template from the `prompts/` directory, injects the code into the prompt, and uses the `vertexai` library to call the configured Gemini model.
    *   **`firestore.py`**: Contains the `FirestoreClient` class, which encapsulates all interactions with the Firestore database, including creating and reading documents.
*   **`prompts/`**: This directory contains the text files used as templates for the AI evaluation prompts.
*   **`.env`**: This file is used to store environment variables, such as the Firestore database name and Vertex AI configuration, which are loaded at runtime using `python-dotenv`.

## 3. Data Flow

1.  The user executes `main.py` from the command line, providing a file or directory path.
2.  `main.py` parses the arguments.
3.  For each file to be processed:
    a.  `get_git_data()` is called to get the file's Git history.
    b.  A unique document ID is generated from the GitHub URL.
    c.  The Firestore database is checked to see if a document with this ID already exists.
    d.  If the document exists and the `--regen` flag is not present, the last commit date from Git is compared to the date stored in Firestore. If they match, the file is skipped.
    e.  `extract_region_tags()` is called to get a list of all region tags in the file.
    f.  `evaluate_code()` is called. This function reads the prompt from `prompts/consolidated_eval.txt`, injects the file's content, and sends it to the Gemini API via the Vertex AI SDK.
    g.  The raw code of the file is read from the file system.
    h.  All the collected data (Git info, region tags, AI evaluation, raw code, and a timestamp) is combined into a single Python dictionary.
    i.  This dictionary is passed to the `create()` function in the `firestore.py` module, which saves it as a document in the appropriate Firestore collection (either "Javascript" or "Python").

## 4. Key Technologies

*   **Language:** Python 3
*   **Command-Line Parsing:** `argparse`
*   **AI/LLM:** Google Gemini, via the `google-cloud-aiplatform` SDK.
*   **Database:** Google Cloud Firestore
*   **Configuration:** `python-dotenv` for managing environment variables.
*   **Version Control Integration:** `git` (via `subprocess`).

## 5. Future Considerations

*   **Error Handling:** The error handling is basic and relies on writing to a local `errors.log` file. A more robust system could involve a dead-letter queue or a dedicated error collection in Firestore.
*   **Batch Processing:** For very large codebases, the current sequential processing could be slow. The system could be refactored to use a `ThreadPoolExecutor` to process files in parallel.
*   **Decoupling from Git:** The system currently requires the files to be within a Git repository to function correctly. This could be made optional to allow analysis of arbitrary, non-versioned code.
