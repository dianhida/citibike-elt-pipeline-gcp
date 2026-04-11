# dbt project (`citibike_dbt`)

## What this does

This dbt project transforms the raw BigQuery table loaded by `ingestion/load_to_bq.py`:

- **Source**: `raw.trips_raw` (configured in `models/staging/schema.yml`)
- **Staging**: `staging.stg_trips` (cleaned + derived fields)
- **Mart**:
  - `mart.fct_trips`
  - `mart.agg_trips_by_month`
  - `mart.agg_trips_by_type`

## Where the dbt profile lives

In this repo, the dbt profile is at:

- `dbt/profiles.yml` (repo root `dbt/` folder)

When run inside the Airflow container, the DAG uses:

- `dbt ... --profiles-dir /opt/airflow/dbt`

and Docker mounts `../dbt` → `/opt/airflow/dbt`, so the profile is found correctly.

## Run locally

From repo root (recommended to use the repo venv):

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

If you want to run dbt outside Docker, make sure `dbt/profiles.yml` points `keyfile:` to a **local path** (because `/opt/airflow/...` is a container path).

Then:

```bash
cd dbt/citibike_dbt
dbt run --profiles-dir ../
dbt test --profiles-dir ../
```

