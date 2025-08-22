# JSRepoAnalysis: AI-Powered Code Quality and Categorization Engine

JSRepoAnalysis is a powerful, command-line tool engineered for development teams that are serious about maintaining high standards of code quality and consistency. It analyzes local or remote codebases, performs a deep, AI-powered style and quality evaluation via a dedicated external API, and stores the structured results in a BigQuery database.

This provides a comprehensive and queryable history of a project's code health, enabling engineering managers, tech leads, and developers to track quality trends, identify areas for improvement, and ensure that all code adheres to a consistent standard of excellence.

## Key Features

- **Multi-Language Support**: Analyzes a wide range of programming languages, including Javascript, Typescript, Python, Java, Go, Rust, Ruby, C#, C++, and PHP.
- **Flexible Input Sources**: Process code from a single file, a local directory, or a CSV file containing a list of GitHub URLs.
- **AI-Powered Evaluation**: Leverages a dedicated external API to perform a nuanced, context-aware style and quality evaluation that goes beyond traditional linters.
- **Accurate Product Categorization**: The same external API provides highly accurate product and technology categorization for each code sample.
- **Rich Git Integration**: Automatically enriches the analysis with Git metadata, including the last commit date, full commit history, and a direct link to the file on GitHub.
- **Centralized BigQuery Storage**: Stores all analysis results in a structured BigQuery database, perfect for longitudinal analysis, data visualization, and building custom quality dashboards.
- **Efficient & Robust Processing**: Features incremental analysis to skip unchanged files, parallel processing for speed, and a robust error-logging and reprocessing mechanism.
- **Categorization-Only Mode**: Includes a special mode to run only the product categorization engine (via the API) and output the results directly to a CSV file, bypassing the full AI evaluation and database writes.

## How It Works

The tool operates through a series of orchestrated steps:

1.  **File Ingestion**: The `main.py` script parses user arguments to gather a list of files to process from the specified source (local path, directory, or CSV). For remote files, it efficiently clones or updates the source repositories.
2.  **Parallel Processing**: A thread pool is used to process multiple files in parallel, significantly speeding up analysis of large projects.
3.  **Code & Git Analysis**: For each file, the `CodeProcessor` extracts key metadata, including Git history and the raw code content.
4.  **External API Analysis**: The `CodeProcessor` sends the code and its metadata to a dedicated external analysis API. This API performs two key functions:
    *   **Product Categorization**: It determines the associated Google Cloud product and technology.
    *   **AI Quality Evaluation**: It uses a powerful AI model to perform a detailed analysis against a comprehensive set of quality criteria.
5.  **Data Storage**: The `CodeProcessor` receives a complete JSON object from the API containing all analysis results. It combines this with the local Git metadata and saves the final, structured record to the configured BigQuery table.

For a more detailed breakdown, see the [Technical Design Document](./docs/TECHNICAL_DESIGN.md).

## Installation

1.  **Prerequisites**:
    *   Python 3.12+
    *   `git` command-line tool
    *   Google Cloud SDK (`gcloud`) authenticated with a project that has the Vertex AI and BigQuery APIs enabled.
    *   `uv` - A fast Python package installer and resolver. If you don't have it, you can install it with `pip install uv`.

2.  **Clone the repository:**
    ```bash
    git clone https://github.com/joeshirey/JSRepoAnalysis.git
    cd JSRepoAnalysis
    ```

3.  **Set up the environment:**
    *   Create a Python virtual environment:
        ```bash
        python -m venv .venv
        source .venv/bin/activate
        ```
    *   Install the required dependencies using `uv`:
        ```bash
        uv pip install -r requirements.txt
        ```

4.  **Configure the application:**
    *   Copy the `.env.sample` file to `.env`:
        ```bash
        cp .env.sample .env
        ```
    *   Edit the `.env` file and provide the necessary values for your environment.

| Variable                  | Description                                                                                             |
| ------------------------- | ------------------------------------------------------------------------------------------------------- |
| `GOOGLE_CLOUD_PROJECT`    | Your Google Cloud project ID.                                                                           |
| `GOOGLE_CLOUD_LOCATION`   | The Google Cloud region for your project (e.g., `us-central1`).                                         |
| `VERTEXAI_MODEL_NAME`     | The specific Vertex AI model to be used by the external API (e.g., `gemini-1.5-flash-001`).              |
| `BIGQUERY_DATASET`        | The name of your BigQuery dataset where the results will be stored.                                     |
| `BIGQUERY_TABLE`          | The name of the BigQuery table for the analysis results.                                                |
| `API_URL`                 | **Crucial:** The URL of the external analysis API that performs the code evaluation and categorization. |
| `GOOGLE_GENAI_USE_VERTEXAI`| Set to `true` to use Vertex AI as the backend for the generative AI models.                               |


## Usage

The tool is run from the command line via `main.py`.

**Analyze a single file and print the full API JSON response to the console:**
```bash
python main.py /path/to/your/file.py --eval-only
```

**Analyze an entire directory and save to BigQuery:**
```bash
python main.py /path/to/your/project/
```

**Analyze a list of GitHub URLs from a CSV file:**
```bash
python main.py --from-csv /path/to/your/links.csv
```

**Force re-analysis of all files, even if unchanged:**
```bash
python main.py /path/to/your/project/ --regen
```

**Reprocess files that failed in a previous run:**
```bash
python main.py --reprocess-log logs/your_error_log.log
```

**Run product categorization only and output to CSV:**
```bash
python main.py /path/to/your/project/ --categorize-only
```

## BigQuery Schema

The analysis results are stored in a BigQuery table with a corresponding view designed for easier analysis.

*   **`repo_analysis` (Table)**: This is the main table where raw analysis data is stored. It includes top-level columns for frequently queried fields like `github_link`, `product_name`, and `language`. More complex data, like the full commit history and the detailed AI evaluation, are stored in `JSON` columns.

*   **`repo_analysis_view` (View)**: This is the **recommended interface for analysis**. It provides a clean, flattened, and de-duplicated view of the data. It unnests the `criteria_breakdown` from the evaluation JSON, exposing each quality criterion's score and assessment as a separate column. It also ensures that only the single most recent analysis for each file is shown, providing a stable dataset for dashboards and reports.

For the exact schema, see the SQL files in the `BQ/` directory.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue. For more details, see the [product requirements](./docs/PRODUCT_REQUIREMENTS.md) and [technical design](./docs/TECHNICAL_DESIGN.md).