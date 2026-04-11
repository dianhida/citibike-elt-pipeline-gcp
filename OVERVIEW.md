# 🚲 Citi Bike Pipeline (Overview)

## What this repo is

This project demonstrates a modern batch ELT pipeline on Google Cloud:

- **Raw data source**: Citi Bike monthly trip data (ZIP → CSV)
- **Data lake**: Google Cloud Storage (GCS)
- **Data warehouse**: BigQuery (raw + transformed datasets)
- **Transformations**: dbt models (staging + marts)
- **Orchestration**: Airflow (Docker Compose)
- **Infra**: Terraform provisions the bucket + dataset

If you’re looking for the step-by-step setup/run instructions, use the **technical runbook**:

- `README.md`

**Two setup styles** (detailed table + version matrix in `README.md`):

- **Local (no Docker)**: use **`.env`** + **`GOOGLE_APPLICATION_CREDENTIALS`** for Python ingestion/load; align **`dbt/profiles.yml` `keyfile`** with that key path for `dbt run`.
- **Airflow + Docker**: place **`dbt/keys/my-creds.json`** and rely on the mounted **`dbt/profiles.yml`** (container paths under `/opt/airflow/...`).

---

## What you get out of it

- A reproducible pipeline you can trigger from Airflow:
  - **Ingest** → **Load to BigQuery** → **dbt run** → **dbt test**
- BigQuery tables suitable for BI (Looker Studio / Tableau / etc.)

---

## High-level data flow

1. Download monthly ZIP archives from `BASE_URL`
2. Extract CSV files and upload to `gs://<bucket>/raw/<month>/...`
3. Load into BigQuery: `<project>.<dataset>.trips_raw` (partitioned + clustered)
4. Transform using dbt into:
   - `staging.*` (cleaned trips)
   - `mart.*` (facts + aggregates)
5. Visualize through Looker Studio using the data mart above (to be exact, the used table is agg_trips_by_month)
---

## Where to look

- **Infrastructure**: `terraform/`
- **Ingestion + load**: `ingestion/`
- **Transformations**: `dbt/`
- **Orchestration**: `airflow/`
- **Dashboard assets** (if any): `dashboard/`

