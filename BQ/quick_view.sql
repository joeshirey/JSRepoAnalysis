-- Create Python View

CREATE OR REPLACE VIEW `panoply-ai-dev.samples_views.python_view` AS
SELECT
    JSON_EXTRACT_ARRAY(t.data, '$.region_tags') AS region_tags,
    PARSE_TIMESTAMP('%Y-%m-%d %H:%M', JSON_EXTRACT_SCALAR(t.data, '$.evaluation_date')) AS evaluation_date,
    PARSE_TIMESTAMP('%Y-%m-%d', JSON_EXTRACT_SCALAR(t.data, '$.git_info.last_updated')) AS last_updated_date,
    CASE
        WHEN JSON_EXTRACT_SCALAR(t.data, '$.git_info.github_owner') = 'GoogleCloudPlatform'
        THEN REGEXP_EXTRACT(JSON_EXTRACT_SCALAR(t.data, '$.git_info.github_link'), r'\/blob\/main\/([^\/]+)\/')
        WHEN JSON_EXTRACT_SCALAR(t.data, '$.git_info.github_owner') = 'googleapis'
        THEN REGEXP_EXTRACT(JSON_EXTRACT_SCALAR(t.data, '$.git_info.github_link'), r'\/googleapis\/(?:java|nodejs|python)-([^\/]+)')
    END AS product_area,
    JSON_EXTRACT_SCALAR(t.data, '$.git_info.github_link') AS github_link,
    JSON_EXTRACT(t.data, '$.git_info') AS git_info_raw_json,
    JSON_EXTRACT(t.data, '$.evaluation_data') AS evaluation_data_raw_json,
    CAST(JSON_EXTRACT_SCALAR(t.data, '$.evaluation_data.overall_compliance_score') AS INT64) AS overall_compliance_score,
    JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.identified_generic_problem_categories') AS identified_generic_problem_categories,
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'Runnability & Configuration'
    ) AS runnability_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'Runnability & Configuration'
    ) AS runnability_assessment,
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'API Effectiveness'
    ) AS api_effectiveness_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'API Effectiveness'
    ) AS api_effectiveness_assessment,
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'Comments & Code Clarity'
    ) AS code_clarity_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'Comments & Code Clarity'
    ) AS code_clarity_assessment,
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'Formatting & Consistency'
    ) AS consistency_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'Formatting & Consistency'
    ) AS consistency_assessment,
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'Language Best Practices'
    ) AS language_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'Language Best Practices'
    ) AS language_assessment,
    "Python" AS sample_language
FROM
    `panoply-ai-dev.firestore_python_existing_samples.python_existing_samples_raw_latest` AS t
WHERE
    -- Pre-filter the source data as before
    JSON_EXTRACT_ARRAY(t.data, '$.region_tags') IS NOT NULL
    AND ARRAY_LENGTH(JSON_EXTRACT_ARRAY(t.data, '$.region_tags')) > 0

-- Create Javascript view
CREATE OR REPLACE VIEW `panoply-ai-dev.samples_views.js_view` AS
SELECT
    JSON_EXTRACT_ARRAY(t.data, '$.region_tags') AS region_tags,
    PARSE_TIMESTAMP('%Y-%m-%d %H:%M', JSON_EXTRACT_SCALAR(t.data, '$.evaluation_date')) AS evaluation_date,
    PARSE_TIMESTAMP('%Y-%m-%d', JSON_EXTRACT_SCALAR(t.data, '$.git_info.last_updated')) AS last_updated_date,
    CASE
        WHEN JSON_EXTRACT_SCALAR(t.data, '$.git_info.github_owner') = 'GoogleCloudPlatform'
        THEN REGEXP_EXTRACT(JSON_EXTRACT_SCALAR(t.data, '$.git_info.github_link'), r'\/blob\/main\/([^\/]+)\/')
        WHEN JSON_EXTRACT_SCALAR(t.data, '$.git_info.github_owner') = 'googleapis'
        THEN REGEXP_EXTRACT(JSON_EXTRACT_SCALAR(t.data, '$.git_info.github_link'), r'\/googleapis\/(?:java|nodejs|python)-([^\/]+)')
    END AS product_area,
    JSON_EXTRACT_SCALAR(t.data, '$.git_info.github_link') AS github_link,
    JSON_EXTRACT(t.data, '$.git_info') AS git_info_raw_json,
    JSON_EXTRACT(t.data, '$.evaluation_data') AS evaluation_data_raw_json,
    CAST(JSON_EXTRACT_SCALAR(t.data, '$.evaluation_data.overall_compliance_score') AS INT64) AS overall_compliance_score,
    JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.identified_generic_problem_categories') AS identified_generic_problem_categories,
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'Runnability & Configuration'
    ) AS runnability_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'Runnability & Configuration'
    ) AS runnability_assessment,
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'API Effectiveness'
    ) AS api_effectiveness_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'API Effectiveness'
    ) AS api_effectiveness_assessment,
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'Comments & Code Clarity'
    ) AS code_clarity_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'Comments & Code Clarity'
    ) AS code_clarity_assessment,
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'Formatting & Consistency'
    ) AS consistency_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'Formatting & Consistency'
    ) AS consistency_assessment,
    (
        SELECT CAST(JSON_EXTRACT_SCALAR(criterion, '$.score') AS INT64)
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'Language Best Practices'
    ) AS language_score,
    (
        SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
        FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
        WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'Language Best Practices'
    ) AS language_assessment,
    "Javascript" AS sample_language
FROM
    `panoply-ai-dev.firestore_javascript_existing_samples.javascript_existing_samples_raw_latest` AS t
WHERE
    -- Pre-filter the source data as before
    JSON_EXTRACT_ARRAY(t.data, '$.region_tags') IS NOT NULL
    AND ARRAY_LENGTH(JSON_EXTRACT_ARRAY(t.data, '$.region_tags')) > 0;


-- Create a consolidated view across both
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