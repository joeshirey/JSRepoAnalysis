MERGE `project.BQ_dataset.table` AS T
USING (
    -- This subquery selects and transforms the new data from your raw JSON table.
    -- It's the same logic as your previous SELECT statement.
    SELECT
        JSON_EXTRACT_ARRAY(t.data, '$.region_tags') AS region_tags,
        PARSE_TIMESTAMP('%Y-%m-%d %H:%M', JSON_EXTRACT_SCALAR(t.data, '$.evaluation_date')) AS evaluation_date,
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
            WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'API Effectiveness (googleapis/googleapis)'
        ) AS api_effectiveness_score,
        (
            SELECT JSON_EXTRACT_SCALAR(criterion, '$.assessment')
            FROM UNNEST(JSON_EXTRACT_ARRAY(t.data, '$.evaluation_data.criteria_breakdown')) AS criterion
            WHERE JSON_EXTRACT_SCALAR(criterion, '$.criterion_name') = 'API Effectiveness (googleapis/googleapis)'
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
        ) AS language_assessment
    FROM
        `project.BQ_dataset.table` AS t
    WHERE
        -- Pre-filter the source data as before
        JSON_EXTRACT_ARRAY(t.data, '$.region_tags') IS NOT NULL
        AND ARRAY_LENGTH(JSON_EXTRACT_ARRAY(t.data, '$.region_tags')) > 0
) AS S
ON
    -- Define the condition for a match: github_link AND evaluation_date must be the same.
    T.github_link = S.github_link AND T.evaluation_date = S.evaluation_date

WHEN NOT MATCHED BY TARGET THEN
    -- If no match is found, insert the new record from the source.
    INSERT (
        region_tags,
        evaluation_date,
        product_area,
        github_link,
        git_info_raw_json,
        evaluation_data_raw_json,
        overall_compliance_score,
        identified_generic_problem_categories,
        runnability_score,
        runnability_assessment,
        api_effectiveness_score,
        api_effectiveness_assessment,
        code_clarity_score,
        code_clarity_assessment,
        consistency_score,
        consistency_assessment,
        language_score,
        language_assessment
    )
    VALUES (
        S.region_tags,
        S.evaluation_date,
        S.product_area,
        S.github_link,
        S.git_info_raw_json,
        S.evaluation_data_raw_json,
        S.overall_compliance_score,
        S.identified_generic_problem_categories,
        S.runnability_score,
        S.runnability_assessment,
        S.api_effectiveness_score,
        S.api_effectiveness_assessment,
        S.code_clarity_score,
        S.code_clarity_assessment,
        S.consistency_score,
        S.consistency_assessment,
        S.language_score,
        S.language_assessment
    );