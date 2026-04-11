{{ config(
    schema='mart',
    materialized='table',
    partition_by={"field": "trip_date", "data_type": "date"},
    cluster_by=["rideable_type", "member_casual"]
) }}

SELECT
    trip_date,
    trip_month,
    trip_week,
    rideable_type,
    member_casual,
    trip_duration_sec
FROM {{ ref('stg_trips') }}