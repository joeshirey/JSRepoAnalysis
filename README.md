# JSRepoAnalysis: AI-Powered Code Quality Analyzer

JSRepoAnalysis is a powerful, command-line tool engineered for development teams that are serious about maintaining high standards of code quality and consistency. It analyzes local or remote codebases, performs a deep, AI-powered style and quality evaluation, and stores the results in a structured BigQuery database.

This provides a comprehensive and queryable history of a project's code health, enabling engineering managers, tech leads, and developers to track quality trends, identify areas for improvement, and ensure that all code adheres to a consistent standard of excellence.

## Key Features

- **Multi-Language Support**: Analyzes a wide range of programming languages, including Javascript, Typescript, Python, Java, Go, Rust, Ruby, C#, C++, and PHP.
- **Flexible Input Sources**: Process code from a single file, a local directory, or a CSV file containing a list of GitHub URLs.
- **AI-Powered Evaluation**: Leverages the Google Gemini model to perform a nuanced, context-aware style and quality evaluation that goes beyond traditional linters.
- **Accurate Product Categorization**: A sophisticated, two-stage engine accurately categorizes code samples. It uses a fast, rules-based approach first, with an LLM-based fallback for complex cases, ensuring precise product and technology mapping.
- **Rich Git Integration**: Automatically enriches the analysis with Git metadata, including the last commit date, full commit history, and a direct link to the file on GitHub.
- **Centralized BigQuery Storage**: Stores all analysis results in a structured BigQuery database, perfect for longitudinal analysis, data visualization, and building custom quality dashboards.
- **Efficient & Robust Processing**: Features incremental analysis to skip unchanged files, parallel processing for speed, and a robust error-logging and reprocessing mechanism.

## How It Works

The tool operates through a series of orchestrated steps:

1.  **File Ingestion**: The `main.py` script parses user arguments to gather a list of files to process from the specified source (local path, directory, or CSV). For remote files, it efficiently clones or updates the source repositories.
2.  **Parallel Processing**: A thread pool is used to process multiple files in parallel, significantly speeding up analysis of large projects.
3.  **Code & Git Analysis**: For each file, the `CodeProcessor` extracts key metadata, including Git history and Google Cloud region tags.
4.  **Product Categorization**: The `extract_product_info` tool determines the associated Google Cloud product. It first uses a highly accurate, rules-based engine defined in `product_hierarchy.yaml`. If that fails, it falls back to an LLM-based analysis for a definitive classification.
5.  **AI Quality Evaluation**: The `CodeEvaluator` sends the code to the Gemini model, which performs a detailed analysis against a comprehensive set of quality criteria defined in the `prompts/` directory.
6.  **Data Storage**: The complete analysis, including all metadata, product info, and AI evaluation scores, is saved as a structured record in the configured BigQuery table.

For a more detailed breakdown, see the [Technical Design Document](./docs/TECHNICAL_DESIGN.md).

## Installation

1.  **Prerequisites**:
    *   Python 3.10+
    *   `git` command-line tool
    *   Google Cloud SDK (`gcloud`) authenticated with a project that has the Vertex AI and BigQuery APIs enabled.

2.  **Clone the repository:**
    ```bash
    git clone https://github.com/joeshirey/JSRepoAnalysis.git
    cd JSRepoAnalysis
    ```

3.  **Set up the environment:**
    *   Create a Python virtual environment.
    *   Install the required dependencies using `uv`:
        ```bash
        uv pip install -r requirements.txt
        ```

4.  **Configure the application:**
    *   Copy the `.env.sample` file to `.env`:
        ```bash
        cp .env.sample .env
        ```
    *   Edit the `.env` file and provide the necessary values for your Google Cloud project, BigQuery dataset, etc.

## Usage

The tool is run from the command line via `main.py`.

**Analyze a single file and print results to the console:**
```bash
uv run main.py /path/to/your/file.py --eval-only
```

**Analyze an entire directory and save to BigQuery:**
```bash
uv run main.py /path/to/your/project/
```

**Analyze a list of GitHub URLs from a CSV file:**
```bash
uv run main.py --from-csv /path/to/your/links.csv
```

**Force re-analysis of all files, even if unchanged:**
```bash
uv run main.py /path/to/your/project/ --regen
```

**Reprocess files that failed in a previous run:**
```bash
uv run main.py --reprocess-log logs/your_error_log.log
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue. For more details, see the [product requirements](./docs/PRODUCT_REQUIREMENTS.md) and [technical design](./docs/TECHNICAL_DESIGN.md).