CREATE OR REPLACE VIEW `project.datastore.view_name` AS
SELECT
    JSON_EXTRACT_ARRAY(t.data, '$.region_tags') AS region_tags,
    PARSE_TIMESTAMP('%Y-%m-%d %H:%M', JSON_EXTRACT_SCALAR(t.data, '$.evaluation_date')) AS evaluation_date,
    PARSE_TIMESTAMP('%Y-%m-%d', JSON_EXTRACT_SCALAR(t.data, '$.git_info.last_updated')) AS last_updated_date,
    REGEXP_EXTRACT(JSON_EXTRACT_SCALAR(t.data, '$.git_info.github_link'), r'\/blob\/main\/([^\/]+)\/') AS product_area,
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
    `projectid.datastore.samples_raw_latest` AS t
WHERE
    -- Pre-filter the source data as before
    JSON_EXTRACT_ARRAY(t.data, '$.region_tags') IS NOT NULL
    AND ARRAY_LENGTH(JSON_EXTRACT_ARRAY(t.data, '$.region_tags')) > 0;