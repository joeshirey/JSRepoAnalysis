# JS/Python Codebase Analyzer

This tool analyzes a local codebase of JavaScript, TypeScript, and Python files, performs an AI-powered quality evaluation, and stores the results in a Firestore database.

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
    *   `PROJECT_ID`: Your Google Cloud Project ID.
    *   `VERTEXAI_LOCATION`: The Google Cloud region for Vertex AI (e.g., `us-central1`).
    *   `VERTEXAI_MODEL_NAME`: The name of the Gemini model to use (e.g., `gemini-1.5-flash-001`).
    *   `FIRESTORE_DB`: The name of the Firestore database to use.

## How to Run

The tool can analyze either a single file or an entire directory.

### Analyze a Single File

```sh
python main.py /path/to/your/file.js
```

### Analyze a Directory

The tool will recursively scan the directory and process all supported files (`.js`, `.ts`, `.py`).

```sh
python main.py /path/to/your/directory/
```

### Force Regeneration

To force the tool to re-analyze files that have already been processed and stored in Firestore, use the `--regen` flag.

```sh
python main.py --regen /path/to/your/directory/
```
