# Ingestion (GCS upload + BigQuery load)

## What runs here

This folder contains two Python entrypoints used by Airflow (and runnable locally):

- `ingest_to_gcs.py`
  - downloads monthly ZIPs from `BASE_URL`
  - extracts CSVs
  - uploads to `gs://<GCS_BUCKET>/raw/<month>/...`
- `load_to_bq.py`
  - loads CSVs from `gs://<GCS_BUCKET>/raw/<month>/*.csv`
  - writes to BigQuery table `<project>.<dataset>.trips_raw`
  - partitions by `started_at` (DAY) and clusters on station IDs

The `data/` directory is for **local downloads and extracted CSVs** only. It is **gitignored** (except `.gitkeep`) because ZIP/CSV sets can be **gigabytes**—do not commit them.

## Runtime configuration (env vars)

These scripts read env vars via `python-dotenv` (they call `load_dotenv()`), so you can use a local `.env` at repo root.

Common env vars:

- `GCP_PROJECT_ID`: BigQuery project ID
- `GCS_BUCKET`: GCS bucket name
- `BASE_URL`: download base URL (default in compose is `https://s3.amazonaws.com/tripdata`)
- `MONTHS`: comma-separated months like `202501,202502,202503`
- `BQ_DATASET` (optional): defaults to `citibike`
- `GOOGLE_APPLICATION_CREDENTIALS`: path to service account JSON key

## Important behavior

`ingest_to_gcs.py` currently deletes the bucket if it exists (`remove_bucket_if_exists`) before recreating it.

- If you provision the bucket via Terraform, consider removing/disabling this for safer runs.

## Run locally (using `.venv`)

From repo root:

```bash
source .venv/bin/activate
pip install -r requirements.txt

export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/my-creds.json"
export $(cat .env | xargs)

python ingestion/ingest_to_gcs.py
python ingestion/load_to_bq.py
```

