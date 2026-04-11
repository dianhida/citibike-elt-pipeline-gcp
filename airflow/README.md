# Airflow (Orchestration)

## What runs here

This folder contains the Dockerized Airflow setup and the DAG that orchestrates the pipeline:

- `dags/pipeline_dag.py`: runs tasks in order:
  - `ingest_to_gcs` (Python)
  - `load_to_bq` (Python)
  - `dbt run` (BashOperator)
  - `dbt test` (BashOperator)
- `docker-compose.yaml`: starts Airflow (webserver + scheduler) + Postgres metadata DB

## Key configuration

### Images

- Airflow: `apache/airflow:2.7.3`
- Postgres: `postgres:13`

### Environment variables

Set in `docker-compose.yaml` (defaults included):

- `GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/keys/my-creds.json`
- `GCP_PROJECT_ID`
- `GCS_BUCKET`
- `BASE_URL`
- `MONTHS`

### Volumes (host → container)

These mounts are required for the DAG to work:

- `./dags` → `/opt/airflow/dags`
- `../ingestion` → `/opt/airflow/ingestion`
- `../dbt` → `/opt/airflow/dbt`
- `../dbt/keys` → `/opt/airflow/keys` (service account JSON)
- `../ingestion/data` → `/opt/airflow/data`

## How to run

From this directory:

```bash
docker compose up airflow-init
docker compose up
```

Then open the UI at `http://localhost:8080` (created user: `airflow` / `airflow`).

## What you can change safely

- **Pipeline months**: update `MONTHS` env var
- **Data source**: update `BASE_URL`
- **Project/bucket**: update `GCP_PROJECT_ID` / `GCS_BUCKET`
- **dbt execution**: see the `dbt run` / `dbt test` commands in `dags/pipeline_dag.py`

