CREATE OR REPLACE TABLE your_dataset.repo_analysis (
    -- Core Identification
    github_link STRING OPTIONS(description="The unique GitHub URL for the file."),
    file_path STRING OPTIONS(description="The relative path of the file within the repository."),
    github_owner STRING OPTIONS(description="The owner of the GitHub repository."),
    github_repo STRING OPTIONS(description="The name of the GitHub repository."),

    -- User-Requested Columns
    product_category STRING OPTIONS(description="The high-level product category."),
    product_name STRING OPTIONS(description="The specific product name."),

    -- Evaluation and Code
    language STRING OPTIONS(description="The programming language of the file."),
    overall_compliance_score INT64 OPTIONS(description="An integer score from 0-100, sourced from the evaluation_data, representing the code's overall compliance."),
    evaluation_data JSON OPTIONS(description="A JSON object containing the results of the code evaluation."),
    region_tags ARRAY<STRING> OPTIONS(description="An array of region tags extracted from the code."),
    raw_code STRING OPTIONS(description="The complete raw source code of the file."),

    -- Timestamps and Versioning
    evaluation_date TIMESTAMP OPTIONS(description="The timestamp when the analysis was performed."),
    last_updated DATE OPTIONS(description="The date of the last commit for this file."),
    branch_name STRING OPTIONS(description="The name of the git branch."),
    
    -- Commit History and File Metadata
    commit_history JSON OPTIONS(description="A JSON array of the file's commit history."),
    metadata JSON OPTIONS(description="A JSON object containing file metadata (size, created, modified).")
);
