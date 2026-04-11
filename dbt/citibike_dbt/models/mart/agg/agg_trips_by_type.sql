{{ config(
    schema='mart'
) }}

SELECT
    rideable_type,
    COUNT(*) AS total_trips,
    AVG(trip_duration_sec) AS avg_duration_sec
FROM {{ ref('stg_trips') }}
GROUP BY 1