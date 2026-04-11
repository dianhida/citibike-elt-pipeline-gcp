{{ config(
    schema='staging'
) }}

SELECT
    ride_id,
    rideable_type,
    DATE(started_at) AS trip_date   ,
    ended_at,
    FORMAT_TIMESTAMP('%Y-%m', started_at) AS trip_month,
    FORMAT_TIMESTAMP('%Y-%W', started_at) AS trip_week,
    TIMESTAMP_DIFF(ended_at, started_at, SECOND) AS trip_duration_sec,
    
    start_station_name,
    start_station_id,
    end_station_name,
    end_station_id,

    start_lat,
    start_lng,
    end_lat,
    end_lng,

    member_casual
FROM {{ source('raw', 'trips_raw') }}
WHERE ride_id IS NOT NULL