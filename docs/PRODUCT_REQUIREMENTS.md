# Product Requirements: Code Quality Analyzer

## 1. Overview

The **Code Quality Analyzer** is a powerful, command-line tool engineered for development teams that are serious about maintaining high standards of code quality and consistency. It is designed to analyze a local or remote codebase of Javascript, Typescript, Python, Java, Go, Rust, Ruby, C#, C++, and PHP files, performing a deep, AI-powered analysis that goes beyond traditional static analysis. By gathering detailed metadata, performing a nuanced style and quality evaluation, and storing the results in a structured BigQuery database, the tool provides a comprehensive and queryable history of a project's code health. This enables engineering managers, tech leads, and developers to track quality trends, identify areas for improvement, and ensure that all code, regardless of who wrote it, adheres to a consistent standard of excellence.

## 2. User Personas

*   **Dana, the Engineering Manager:** Dana oversees multiple development teams and is responsible for the overall quality and velocity of her organization. She needs a high-level, data-driven view of the health of her team's repositories. She wants to be able to track quality metrics over time, identify which projects may need additional resources or training, and ensure that all teams are adhering to the company's coding standards. She is not an expert in every language her teams use, so she needs a tool that can provide a consistent and objective measure of quality across different technology stacks.

*   **Raj, the Tech Lead:** Raj is the go-to expert for his team's codebase and is passionate about maintaining a high standard of code quality. He is responsible for reviewing pull requests and ensuring that new code is clean, maintainable, and well-documented. He wants a tool that can automate the initial, and often tedious, process of checking for style guide adherence and common anti-patterns. This would allow him to focus his attention on the more complex, architectural aspects of a code review. He also wants to be able to see which files have been updated since the last analysis, so he can quickly identify and review the changes.

*   **Chloe, the Developer:** Chloe is a software engineer who is focused on building new features and fixing bugs. She wants to write high-quality code that is easy for her teammates to understand and maintain, but she doesn't want to spend a lot of time manually checking for style guide violations. She wants a tool that she can run locally to get instant, objective feedback on her code before she submits it for review. This would help her to catch any issues early, reduce the number of back-and-forth comments in a pull request, and ultimately, ship her code faster.

## 3. Goals and Objectives

*   **Primary Goal:** To provide a powerful, automated tool that performs a deep analysis of local and remote code files and stores the detailed quality and metadata analysis in a central, queryable BigQuery database.
*   **Objective 1: Comprehensive Code Processing:** To process entire directories of code, recursively analyzing all supported file types, as well as processing a list of files from a CSV of GitHub links.
*   **Objective 2: AI-Powered Evaluation:** To leverage the power of generative AI to perform a nuanced and context-aware style and quality evaluation on each code file, providing insights that go beyond what traditional linters can offer.
*   **Objective 3: Rich Metadata Integration:** To seamlessly integrate with Git to fetch and store rich metadata about each file, such as its last update time, commit history, and a direct link to the file on GitHub.
*   **Objective 4: Centralized, Queryable Storage:** To use BigQuery as a robust and scalable data warehouse for storing the analysis results, enabling powerful and flexible querying, and providing a solid foundation for building insightful dashboards and reports.
*   **Objective 5: Efficient, Incremental Analysis:** To provide a smart and efficient processing mechanism that avoids re-analyzing files that have not changed since their last analysis, saving time and computational resources.
*   **Objective 6: Robust Error Handling and Reprocessing:** To provide a robust mechanism for logging and reprocessing files that failed during a previous run, ensuring that no file is left behind.
*   **Objective 7: Expanded Language Support and Test Data:** To continuously expand the list of supported languages and to maintain a comprehensive suite of test data that covers a wide variety of scenarios and edge cases.

## 4. Functional Requirements

| ID | Requirement | User Story |
|----|-------------|------------|
| FR-1 | **Flexible File Processing** | As a user, I want to be able to provide a path to a single file, a directory, or a CSV of GitHub links, so that I can easily analyze the code that I care about. |
| FR-2 | **Recursive Analysis** | As a user, when I provide a directory path, I want the tool to recursively scan all subdirectories and analyze all supported file types, so that I can get a complete picture of my project's code quality. |
| FR-3 | **Rich Git Integration** | As a user, I want the tool to automatically gather Git metadata for each file, including the last commit date and a link to the file on GitHub, so that I can easily track the history of a file and see who made the last change. |
| FR-4 | **Region Tag Extraction** | As a user, I want the tool to be able to identify and extract Google Cloud-style region tags from the code, so that I can easily identify and categorize code snippets. |
| FR-5 | **Nuanced AI-Powered Evaluation** | As a user, I want the tool to use a powerful generative AI model to perform a detailed style and quality evaluation on my code, so that I can get objective and actionable feedback that goes beyond what a traditional linter can provide. |
| FR-6 | **Centralized BigQuery Storage** | As a user, I want the results of the analysis to be stored in a structured BigQuery database, so that I can easily query the data, build dashboards, and track quality trends over time. |
| FR-7 | **Efficient Incremental Processing** | As a user, I want the tool to be smart enough to skip the analysis of files that have not changed since their last analysis, so that I can save time and money. |
| FR-8 | **Forced Regeneration** | As a user, I want to be able to force the re-analysis of a file, even if it hasn't changed, so that I can easily update the analysis results after making changes to the evaluation criteria. |
| FR-9 | **Robust Error Logging** | As a user, I want the tool to log any errors that occur during file processing to a dedicated log file, so that I can easily identify and troubleshoot any issues. |
| FR-10 | **Easy Reprocessing** | As a user, I want to be able to easily reprocess any files that failed during a previous run, so that I can ensure that all of my files are analyzed. |
| FR-11 | **Quick Evaluation-Only Mode** | As a developer, I want to be able to quickly analyze a single file and see the results in my console, without having to wait for the data to be written to the database, so that I can get instant feedback on my code. |
| FR-12 | **Dynamic Branch Detection** | As a user, I want the tool to be able to automatically detect the default branch of a repository, so that I don't have to worry about the tool failing if the default branch is not named `main`. |
| FR-13 | **Comprehensive Test Data** | As a developer, I want the tool to have a comprehensive suite of test data, including a variety of test CSV files, so that I can be confident that the tool is working correctly and that any new changes I make are not breaking existing functionality. |

## 5. Out of Scope (Non-Goals)

*   **A Graphical User Interface (GUI):** This is a command-line only tool, designed to be used in a terminal or as part of an automated CI/CD pipeline.
*   **Real-time Analysis:** The tool is designed to be run on demand, not as a real-time linter in an IDE.
*   **Automated Code Fixing:** The tool provides analysis and feedback, but it does not attempt to automatically fix any issues it finds. The goal is to empower developers to make their own informed decisions about how to improve their code.