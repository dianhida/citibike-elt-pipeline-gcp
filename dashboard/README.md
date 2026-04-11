# Dashboard

## Purpose

This folder is for dashboard artifacts (e.g., screenshots, exported configs) that visualize the transformed data in BigQuery.

Typical source tables for BI are produced by dbt into:

- `mart.fct_trips`
- `mart.agg_trips_by_month`
- `mart.agg_trips_by_type`

## Looker Studio

To build the dashboard:

1. Connect Looker Studio to BigQuery in your GCP project
2. Select the mart tables above
3. Create visuals such as:
   - total trips
   - trip distribution by `rideable_type`
   - monthly trends (`trip_month`)
   - average duration trends
