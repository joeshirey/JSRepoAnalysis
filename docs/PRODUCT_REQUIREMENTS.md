# Product Requirements Document: Code Quality Analyzer

## 1. Introduction

The Code Quality Analyzer is a command-line tool designed to analyze a local codebase of Javascript, Typescript, Python, Java, Go, Rust, Ruby, C#, C++, and PHP files. It gathers metadata, performs an AI-powered style and quality evaluation, and stores the comprehensive results in a structured Firestore database. This enables developers and teams to track code quality, identify areas for improvement, and maintain a consistent standard across their repositories.

## 2. User Personas

*   **Dana, the Engineering Manager:** Dana wants to get a high-level overview of the quality and consistency of multiple repositories her team manages. She needs a way to track style guide adherence and code quality over time.
*   **Raj, the Tech Lead:** Raj is responsible for maintaining a high standard of code quality. He wants a tool that can automatically analyze new code and provide objective feedback, and to see which files have been updated since the last analysis.
*   **Chloe, the Developer:** Chloe is working on a new feature and wants to ensure her code adheres to the team's style guide before submitting it for review.

## 3. Goals and Objectives

*   **Primary Goal:** To provide an automated tool that analyzes local code files and stores detailed quality and metadata analysis in a central database.
*   **Objective 1:** To process entire directories of code, recursively analyzing all supported file types.
*   **Objective 2:** To use AI to perform a nuanced style and quality evaluation on each code file.
*   **Objective 3:** To integrate with Git to fetch metadata about each file, such as its last update time and GitHub URL.
*   **Objective 4:** To use Firestore as a persistent, queryable database for storing the analysis results.
*   **Objective 5:** To provide an efficiency mechanism that avoids re-analyzing files that have not changed since their last analysis.
*   **Objective 6:** To provide a robust mechanism for reprocessing files that failed during a previous run.
*   **Objective 7:** To provide a way to process a list of files from a CSV of GitHub links.
*   **Objective 8:** To expand the test data to include a variety of scenarios.

## 4. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-1 | **File Processing** | The tool MUST be able to accept a path to either a single file or a directory as a command-line argument. |
| FR-2 | **Recursive Analysis** | If a directory is provided, the tool MUST recursively scan all subdirectories and analyze all supported file types. |
| FR-3 | **Git Integration** | For each file, the tool MUST gather Git metadata, including the last commit date and a link to the file on GitHub. |
| FR-4 | **Region Tag Extraction** | The tool MUST be able to identify and extract Google Cloud-style region tags (e.g., `[START ...]`) from the code. |
| FR-5 | **AI-Powered Evaluation** | The tool MUST use a generative AI model to perform a style and quality evaluation on the content of each file. |
| FR-6 | **Firestore Storage** | The results of the analysis for each file MUST be stored as a document in a Firestore database. |
| FR-7 | **Incremental Processing** | The tool MUST check if a file has been analyzed before and if its content has changed (based on the last Git commit date). It should skip analysis if the file is unchanged. |
| FR-8 | **Forced Regeneration** | The tool MUST provide a command-line flag (`--regen`) to force re-analysis of a file, even if it has not changed. |
| FR-9 | **Error Logging** | The tool MUST log any errors that occur during file processing to a dynamically named log file in the `logs/` directory. |
| FR-10 | **Reprocessing** | The tool MUST provide a command-line flag (`--reprocess-log`) to reprocess files from a specified error log. |
| FR-11 | **Evaluation-Only Mode** | The tool MUST provide a command-line flag (`--eval_only`) to analyze a single file and print the results to the console without any database interaction. |
| FR-12 | **CSV Processing** | The tool MUST be able to accept a path to a CSV file of GitHub links as a command-line argument. |
| FR-13 | **Dynamic Branch Detection** | The tool MUST dynamically determine the default branch of a repository when cloning or pulling, to avoid errors when the default branch is not named `main`. |
| FR-14 | **Expanded Test Data** | The tool MUST include a variety of test CSV files to ensure robust testing. |

## 5. Out of Scope (Non-Goals)

*   **A Graphical User Interface (GUI):** This is a command-line only tool.
*   **Real-time Analysis:** The tool is designed to be run on demand, not as a real-time linter in an IDE.
*   **Automated Code Fixing:** The tool provides analysis but does not attempt to automatically fix any issues it finds.
