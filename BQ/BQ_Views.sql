CREATE OR REPLACE VIEW `panoply-ai-dev.samples_views.js_view` AS
SELECT
    -- Extract region tags and parse timestamps
    JSON_EXTRACT_ARRAY(t.data, '$.region_tags') AS region_tags,
    PARSE_TIMESTAMP('%Y-%m-%d %H:%M', JSON_EXTRACT_SCALAR(t.data, '$.evaluation_date')) AS evaluation_date,
    PARSE_TIMESTAMP('%Y-%m-%d', JSON_EXTRACT_SCALAR(t.data, '$.git_info.last_updated')) AS last_updated_date,

    -- Source product name and category directly from evaluation_data
    JSON_EXTRACT_SCALAR(t.data, '$.evaluation_data.product_name') AS product_name,
    COALESCE(JSON_EXTRACT_SCALAR(t.data, '$.evaluation_data.product_category'), 'N/A') AS product_category,

    -- Extract Git info and other metadata
    JSON_EXTRACT_SCALAR(t.data, '$.git_info.github_link') AS github_link,
    JSON_EXTRACT(t.data, '$.git_info') AS git_info_raw_json,
    JSON_EXTRACT(t.data, '$.evaluation_data') AS evaluation_data_raw_json,
    JSON_EXTRACT_SCALAR(t.data, '$.raw_code') AS raw_code,
    CAST(JSON_EXTRACT_SCALAR(t.data, '$.evaluation_data.overall_compliance_score') AS INT64) AS overall_compliance_score,
    JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.identified_generic_problem_categories') AS identified_generic_problem_categories,

    -- Unnest and extract scores & assessments for each criterion

    -- Runnability & Configuration
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'runnability_and_configuration'
    ) AS runnability_and_configuration_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'runnability_and_configuration'
    ) AS runnability_and_configuration_assessment,

    -- API Effectiveness & Correctness
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'api_effectiveness_and_correctness'
    ) AS api_effectiveness_and_correctness_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'api_effectiveness_and_correctness'
    ) AS api_effectiveness_and_correctness_assessment,

    -- Comments & Code Clarity
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'comments_and_code_clarity'
    ) AS comments_and_code_clarity_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'comments_and_code_clarity'
    ) AS comments_and_code_clarity_assessment,

    -- Formatting & Consistency
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'formatting_and_consistency'
    ) AS formatting_and_consistency_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'formatting_and_consistency'
    ) AS formatting_and_consistency_assessment,

    -- Language Best Practices
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'language_best_practices'
    ) AS language_best_practices_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'language_best_practices'
    ) AS language_best_practices_assessment,

    -- LLM Training Fitness & Explicitness
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'llm_training_fitness_and_explicitness'
    ) AS llm_training_fitness_and_explicitness_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'llm_training_fitness_and_explicitness'
    ) AS llm_training_fitness_and_explicitness_assessment,

    -- Static sample language
    "JavaScript" AS sample_language
FROM
    `panoply-ai-dev.firestore_javascript_existing_samples.javascript_existing_samples_raw_latest` AS t
WHERE
    -- Pre-filter rows where region_tags exist and are not empty
    JSON_EXTRACT_ARRAY(t.data, '$.region_tags') IS NOT NULL
    AND ARRAY_LENGTH(JSON_EXTRACT_ARRAY(t.data, '$.region_tags')) > 0;

CREATE OR REPLACE VIEW `panoply-ai-dev.samples_views.python_view` AS
SELECT
    -- Extract region tags and parse timestamps
    JSON_EXTRACT_ARRAY(t.data, '$.region_tags') AS region_tags,
    PARSE_TIMESTAMP('%Y-%m-%d %H:%M', JSON_EXTRACT_SCALAR(t.data, '$.evaluation_date')) AS evaluation_date,
    PARSE_TIMESTAMP('%Y-%m-%d', JSON_EXTRACT_SCALAR(t.data, '$.git_info.last_updated')) AS last_updated_date,

    -- Source product name and category directly from evaluation_data
    JSON_EXTRACT_SCALAR(t.data, '$.evaluation_data.product_name') AS product_name,
    COALESCE(JSON_EXTRACT_SCALAR(t.data, '$.evaluation_data.product_category'), 'N/A') AS product_category,

    -- Extract Git info and other metadata
    JSON_EXTRACT_SCALAR(t.data, '$.git_info.github_link') AS github_link,
    JSON_EXTRACT(t.data, '$.git_info') AS git_info_raw_json,
    JSON_EXTRACT(t.data, '$.evaluation_data') AS evaluation_data_raw_json,
    JSON_EXTRACT_SCALAR(t.data, '$.raw_code') AS raw_code,
    CAST(JSON_EXTRACT_SCALAR(t.data, '$.evaluation_data.overall_compliance_score') AS INT64) AS overall_compliance_score,
    JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.identified_generic_problem_categories') AS identified_generic_problem_categories,

    -- Unnest and extract scores & assessments for each criterion

    -- Runnability & Configuration
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'runnability_and_configuration'
    ) AS runnability_and_configuration_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'runnability_and_configuration'
    ) AS runnability_and_configuration_assessment,

    -- API Effectiveness & Correctness
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'api_effectiveness_and_correctness'
    ) AS api_effectiveness_and_correctness_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'api_effectiveness_and_correctness'
    ) AS api_effectiveness_and_correctness_assessment,

    -- Comments & Code Clarity
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'comments_and_code_clarity'
    ) AS comments_and_code_clarity_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'comments_and_code_clarity'
    ) AS comments_and_code_clarity_assessment,

    -- Formatting & Consistency
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'formatting_and_consistency'
    ) AS formatting_and_consistency_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'formatting_and_consistency'
    ) AS formatting_and_consistency_assessment,

    -- Language Best Practices
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'language_best_practices'
    ) AS language_best_practices_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'language_best_practices'
    ) AS language_best_practices_assessment,

    -- LLM Training Fitness & Explicitness
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'llm_training_fitness_and_explicitness'
    ) AS llm_training_fitness_and_explicitness_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'llm_training_fitness_and_explicitness'
    ) AS llm_training_fitness_and_explicitness_assessment,

    -- Static sample language
    "Python" AS sample_language
FROM
    `panoply-ai-dev.firestore_python_existing_samples.python_existing_samples_raw_latest` AS t
WHERE
    -- Pre-filter rows where region_tags exist and are not empty
    JSON_EXTRACT_ARRAY(t.data, '$.region_tags') IS NOT NULL
    AND ARRAY_LENGTH(JSON_EXTRACT_ARRAY(t.data, '$.region_tags')) > 0;

CREATE OR REPLACE VIEW `panoply-ai-dev.samples_views.all_samples_view` AS
SELECT
  *
FROM
  `panoply-ai-dev.samples_views.python_view`

UNION ALL

SELECT
  *
FROM
  `panoply-ai-dev.samples_views.js_view`;

CREATE OR REPLACE VIEW `panoply-ai-dev.samples_views.js_view_generated` AS
SELECT
    -- Extract region tags and parse timestamps
    JSON_EXTRACT_ARRAY(t.data, '$.region_tags') AS region_tags,
    PARSE_TIMESTAMP('%Y-%m-%d %H:%M', JSON_EXTRACT_SCALAR(t.data, '$.evaluation_date')) AS evaluation_date,
    PARSE_TIMESTAMP('%Y-%m-%d', JSON_EXTRACT_SCALAR(t.data, '$.git_info.last_updated')) AS last_updated_date,

    -- Source product name and category directly from evaluation_data
    JSON_EXTRACT_SCALAR(t.data, '$.evaluation_data.product_name') AS product_name,
    COALESCE(JSON_EXTRACT_SCALAR(t.data, '$.evaluation_data.product_category'), 'N/A') AS product_category,

    -- Extract Git info and other metadata
    JSON_EXTRACT_SCALAR(t.data, '$.git_info.github_link') AS github_link,
    JSON_EXTRACT(t.data, '$.git_info') AS git_info_raw_json,
    JSON_EXTRACT(t.data, '$.evaluation_data') AS evaluation_data_raw_json,
    JSON_EXTRACT_SCALAR(t.data, '$.raw_code') AS raw_code,
    CAST(JSON_EXTRACT_SCALAR(t.data, '$.evaluation_data.overall_compliance_score') AS INT64) AS overall_compliance_score,
    JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.identified_generic_problem_categories') AS identified_generic_problem_categories,

    -- Unnest and extract scores & assessments for each criterion

    -- Runnability & Configuration
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'runnability_and_configuration'
    ) AS runnability_and_configuration_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'runnability_and_configuration'
    ) AS runnability_and_configuration_assessment,

    -- API Effectiveness & Correctness
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'api_effectiveness_and_correctness'
    ) AS api_effectiveness_and_correctness_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'api_effectiveness_and_correctness'
    ) AS api_effectiveness_and_correctness_assessment,

    -- Comments & Code Clarity
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'comments_and_code_clarity'
    ) AS comments_and_code_clarity_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'comments_and_code_clarity'
    ) AS comments_and_code_clarity_assessment,

    -- Formatting & Consistency
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'formatting_and_consistency'
    ) AS formatting_and_consistency_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'formatting_and_consistency'
    ) AS formatting_and_consistency_assessment,

    -- Language Best Practices
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'language_best_practices'
    ) AS language_best_practices_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'language_best_practices'
    ) AS language_best_practices_assessment,

    -- LLM Training Fitness & Explicitness
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'llm_training_fitness_and_explicitness'
    ) AS llm_training_fitness_and_explicitness_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'llm_training_fitness_and_explicitness'
    ) AS llm_training_fitness_and_explicitness_assessment,

    -- Static sample language
    "Javascript" AS sample_language
FROM
    `panoply-ai-dev.firestore_javascript_generated_samples.javascript_generated_samples_raw_latest` AS t
WHERE
    -- Pre-filter rows where region_tags exist and are not empty
    JSON_EXTRACT_ARRAY(t.data, '$.region_tags') IS NOT NULL
    AND ARRAY_LENGTH(JSON_EXTRACT_ARRAY(t.data, '$.region_tags')) > 0;

CREATE OR REPLACE VIEW `panoply-ai-dev.samples_views.python_view_generated` AS
SELECT
    -- Extract region tags and parse timestamps
    JSON_EXTRACT_ARRAY(t.data, '$.region_tags') AS region_tags,
    PARSE_TIMESTAMP('%Y-%m-%d %H:%M', JSON_EXTRACT_SCALAR(t.data, '$.evaluation_date')) AS evaluation_date,
    PARSE_TIMESTAMP('%Y-%m-%d', JSON_EXTRACT_SCALAR(t.data, '$.git_info.last_updated')) AS last_updated_date,

    -- Source product name and category directly from evaluation_data
    JSON_EXTRACT_SCALAR(t.data, '$.evaluation_data.product_name') AS product_name,
    COALESCE(JSON_EXTRACT_SCALAR(t.data, '$.evaluation_data.product_category'), 'N/A') AS product_category,

    -- Extract Git info and other metadata
    JSON_EXTRACT_SCALAR(t.data, '$.git_info.github_link') AS github_link,
    JSON_EXTRACT(t.data, '$.git_info') AS git_info_raw_json,
    JSON_EXTRACT(t.data, '$.evaluation_data') AS evaluation_data_raw_json,
    JSON_EXTRACT_SCALAR(t.data, '$.raw_code') AS raw_code,
    CAST(JSON_EXTRACT_SCALAR(t.data, '$.evaluation_data.overall_compliance_score') AS INT64) AS overall_compliance_score,
    JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.identified_generic_problem_categories') AS identified_generic_problem_categories,

    -- Unnest and extract scores & assessments for each criterion

    -- Runnability & Configuration
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'runnability_and_configuration'
    ) AS runnability_and_configuration_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'runnability_and_configuration'
    ) AS runnability_and_configuration_assessment,

    -- API Effectiveness & Correctness
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'api_effectiveness_and_correctness'
    ) AS api_effectiveness_and_correctness_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'api_effectiveness_and_correctness'
    ) AS api_effectiveness_and_correctness_assessment,

    -- Comments & Code Clarity
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'comments_and_code_clarity'
    ) AS comments_and_code_clarity_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'comments_and_code_clarity'
    ) AS comments_and_code_clarity_assessment,

    -- Formatting & Consistency
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'formatting_and_consistency'
    ) AS formatting_and_consistency_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'formatting_and_consistency'
    ) AS formatting_and_consistency_assessment,

    -- Language Best Practices
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'language_best_practices'
    ) AS language_best_practices_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'language_best_practices'
    ) AS language_best_practices_assessment,

    -- LLM Training Fitness & Explicitness
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'llm_training_fitness_and_explicitness'
    ) AS llm_training_fitness_and_explicitness_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'llm_training_fitness_and_explicitness'
    ) AS llm_training_fitness_and_explicitness_assessment,

    -- Static sample language
    "Python" AS sample_language
FROM
    `panoply-ai-dev.firestore_python_generated_samples.python_generated_samples_raw_latest` AS t
WHERE
    -- Pre-filter rows where region_tags exist and are not empty
    JSON_EXTRACT_ARRAY(t.data, '$.region_tags') IS NOT NULL
    AND ARRAY_LENGTH(JSON_EXTRACT_ARRAY(t.data, '$.region_tags')) > 0;

CREATE OR REPLACE VIEW `panoply-ai-dev.samples_views.all_samples_view_generated` AS
SELECT
  *
FROM
  `panoply-ai-dev.samples_views.python_view_generated`

UNION ALL

SELECT
  *
FROM
  `panoply-ai-dev.samples_views.js_view_generated`;
