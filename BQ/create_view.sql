CREATE OR REPLACE VIEW `panoply-ai-dev.Samples_Health.repo_analysis_view` AS
WITH RankedAnalysis AS (
    SELECT
        *,
        ROW_NUMBER() OVER(PARTITION BY github_link ORDER BY evaluation_date DESC) as rn
    FROM
        `panoply-ai-dev.Samples_Health.repo_analysis`
)
SELECT
    -- Direct columns from the new table
    t.region_tags,
    t.evaluation_date,
    t.last_updated AS last_updated_date,
    t.product_name,
    t.product_category,
    t.github_link,
    t.commit_history AS git_info_raw_json, -- Renaming for consistency with old view
    t.evaluation_data AS evaluation_data_raw_json, -- Renaming for consistency
    t.raw_code,
    t.overall_compliance_score,
    t.language AS sample_language,
    t.validation_details,
    t.Generated,

    -- Extract identified generic problem categories from the JSON
    JSON_EXTRACT_ARRAY(t.evaluation_data, '$.identified_generic_problem_categories') AS identified_generic_problem_categories,

    -- Unnest and extract scores & assessments for each criterion from the JSON
    -- Runnability & Configuration
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'runnability_and_configuration'
    ) AS runnability_and_configuration_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'runnability_and_configuration'
    ) AS runnability_and_configuration_assessment,

    -- API Effectiveness & Correctness
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'api_effectiveness_and_correctness'
    ) AS api_effectiveness_and_correctness_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'api_effectiveness_and_correctness'
    ) AS api_effectiveness_and_correctness_assessment,

    -- Comments & Code Clarity
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'comments_and_code_clarity'
    ) AS comments_and_code_clarity_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'comments_and_code_clarity'
    ) AS comments_and_code_clarity_assessment,

    -- Formatting & Consistency
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'formatting_and_consistency'
    ) AS formatting_and_consistency_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'formatting_and_consistency'
    ) AS formatting_and_consistency_assessment,

    -- Language Best Practices
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'language_best_practices'
    ) AS language_best_practices_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'language_best_practices'
    ) AS language_best_practices_assessment,

    -- LLM Training Fitness & Explicitness
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'llm_training_fitness_and_explicitness'
    ) AS llm_training_fitness_and_explicitness_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'llm_training_fitness_and_explicitness'
    ) AS llm_training_fitness_and_explicitness_assessment
FROM
    RankedAnalysis AS t
WHERE
    t.rn = 1
    AND t.region_tags IS NOT NULL
    AND ARRAY_LENGTH(t.region_tags) > 0
    AND t.Generated IS NOT TRUE;




CREATE OR REPLACE VIEW `panoply-ai-dev.Samples_Health.repo_analysis_view_gen` AS
WITH RankedAnalysis AS (
    SELECT
        *,
        ROW_NUMBER() OVER(PARTITION BY github_link ORDER BY evaluation_date DESC) as rn
    FROM
        `panoply-ai-dev.Samples_Health.repo_analysis`
)
SELECT
    -- Direct columns from the new table
    t.region_tags,
    t.evaluation_date,
    t.last_updated AS last_updated_date,
    t.product_name,
    t.product_category,
    t.github_link,
    t.commit_history AS git_info_raw_json, -- Renaming for consistency with old view
    t.evaluation_data AS evaluation_data_raw_json, -- Renaming for consistency
    t.raw_code,
    t.overall_compliance_score,
    t.language AS sample_language,
    t.validation_details,
    t.Generated,

    -- Extract identified generic problem categories from the JSON
    JSON_EXTRACT_ARRAY(t.evaluation_data, '$.identified_generic_problem_categories') AS identified_generic_problem_categories,

    -- Unnest and extract scores & assessments for each criterion from the JSON
    -- Runnability & Configuration
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'runnability_and_configuration'
    ) AS runnability_and_configuration_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'runnability_and_configuration'
    ) AS runnability_and_configuration_assessment,

    -- API Effectiveness & Correctness
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'api_effectiveness_and_correctness'
    ) AS api_effectiveness_and_correctness_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'api_effectiveness_and_correctness'
    ) AS api_effectiveness_and_correctness_assessment,

    -- Comments & Code Clarity
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'comments_and_code_clarity'
    ) AS comments_and_code_clarity_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'comments_and_code_clarity'
    ) AS comments_and_code_clarity_assessment,

    -- Formatting & Consistency
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'formatting_and_consistency'
    ) AS formatting_and_consistency_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'formatting_and_consistency'
    ) AS formatting_and_consistency_assessment,

    -- Language Best Practices
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'language_best_practices'
    ) AS language_best_practices_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'language_best_practices'
    ) AS language_best_practices_assessment,

    -- LLM Training Fitness & Explicitness
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'llm_training_fitness_and_explicitness'
    ) AS llm_training_fitness_and_explicitness_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.evaluation_data, '$.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'llm_training_fitness_and_explicitness'
    ) AS llm_training_fitness_and_explicitness_assessment
FROM
    RankedAnalysis AS t
WHERE
    t.rn = 1
    AND t.region_tags IS NOT NULL
    AND ARRAY_LENGTH(t.region_tags) > 0
    AND t.Generated = TRUE;
