# 🚲 Citibike Trips Data Engineering Project (GCP + BigQuery + Airflow + dbt + Terraform)

## 📌 Objective

Build an end-to-end ELT pipeline for Citi Bike trip data:

- **Ingest**: download monthly ZIPs, unzip to CSV, upload to **GCS**
- **Load**: load CSVs from GCS into **BigQuery** (partitioned + clustered)
- **Transform**: run **dbt** models (staging + mart) and tests
- **Orchestrate**: run everything in an **Airflow** DAG (Docker Compose)
- **Visualize**: (optional) connect mart tables to **Looker Studio**

This README is a **ground-truth setup guide** based on what’s in this repo (paths, env vars, mounts, and default names).

If you want a quick non-technical overview, see:

- `OVERVIEW.md`

---

## 🧱 Tech Stack

- **GCP**: Cloud Storage (GCS), BigQuery (BQ), IAM
- **IaC**: Terraform (GCS bucket + BQ dataset)
- **Orchestration**: Apache Airflow (Dockerized)
- **Transform**: dbt + BigQuery adapter (`dbt-bigquery`)
- **Ingestion/Load**: Python (`requests`, `google-cloud-storage`, `google-cloud-bigquery`)
- **BI**: Looker Studio (manual connection)

---

## Root concept: two ways to configure the pipeline

Pick **one** primary path depending on how you run things.

| | **Local (no Airflow, no Docker)** | **Airflow + Docker** |
|---|-----------------------------------|----------------------|
| **Config** | Use **`.env`** at repo root for ingestion/load (`load_dotenv()` reads it). Copy from `.env.example` and adjust values. | Compose sets env vars in `airflow/docker-compose.yaml` (`GCP_PROJECT_ID`, `GCS_BUCKET`, `BASE_URL`, `MONTHS`). You do **not** rely on `.env` inside the containers unless you add it yourself. |
| **GCP auth for Python** | Set **`GOOGLE_APPLICATION_CREDENTIALS`** to the absolute path of your service account JSON (anywhere on disk). | Put the real key at **`dbt/keys/my-creds.json`** (copy from `dbt/keys/my-creds.example.json`). Compose mounts `dbt/keys` → `/opt/airflow/keys` and sets `GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/keys/my-creds.json`. |
| **dbt** | Run from host: use **`dbt/profiles.yml`** with **`keyfile:`** pointing to a **host path** (same JSON as above). Use `--profiles-dir dbt` (or `../` from `dbt/citibike_dbt`). | **`dbt/profiles.yml`** stays under **`dbt/`** on the host; Docker mounts the whole **`dbt/`** tree to **`/opt/airflow/dbt`**. Keep **`keyfile: /opt/airflow/keys/my-creds.json`** in the profile so paths match the container. The DAG uses `--profiles-dir /opt/airflow/dbt`. |

**Summary**

- **Local direct Python + dbt**: **`.env`** + **`GOOGLE_APPLICATION_CREDENTIALS`** + a **`profiles.yml` `keyfile`** on your machine.
- **Airflow & Docker**: **`my-creds.json`** under **`dbt/keys/`** + **`dbt/profiles.yml`** layout as shipped (container paths under `/opt/airflow/...`).

Terraform always uses its own key path by default: **`terraform/keys/my-creds.json`** (copy from `terraform/keys/my-creds.example.json`).

---

## Version matrix (pinned / observed)

Values below match this repo’s **`requirements.txt`**, **`.venv`**, **Docker images**, and **Terraform lockfile** as of the last audit.

| Component | Version / image |
|-----------|------------------|
| Python (`.venv`) | 3.12.x (e.g. 3.12.12) |
| `requests` | 2.33.0 |
| `python-dotenv` | 1.2.2 |
| `google-cloud-storage` | 3.1.1 |
| `google-cloud-bigquery` | 3.40.1 |
| `dbt-core` | 1.11.7 |
| `dbt-bigquery` | 1.11.1 |
| Airflow (Docker) | `apache/airflow:2.7.3` |
| Postgres (Airflow metadata) | `postgres:13` |
| Terraform CLI | v1.14.3 (your install may differ slightly) |
| Terraform Google provider | `hashicorp/google` **7.16.0** |

Airflow containers also install unpinned extras via `_PIP_ADDITIONAL_REQUIREMENTS` (`dbt-bigquery`, `google-cloud-storage`, `google-cloud-bigquery`, `python-dotenv`, `requests`); for reproducible local runs, prefer **`.venv` + `requirements.txt`**.

---

## ✅ Recommended execution order (technical runbook)

Follow these in order:

1. **Prepare GCP account + credentials**
2. **Provision infrastructure with Terraform** (GCS bucket + BQ dataset)
3. **Run ingestion** (download + upload CSVs to GCS)
4. **Load raw data into BigQuery**
5. **Run dbt transformations + tests**
6. **Orchestrate with Airflow (Docker Compose)**
7. **Build the Looker Studio dashboard** (optional)

---

## 🗂️ Repo Structure (key files)

```
citibike_pipeline_gcp/
├── airflow/
│   ├── dags/
│   │   └── pipeline_dag.py              # Airflow DAG: ingest -> load -> dbt run -> dbt test
│   └── docker-compose.yaml              # Airflow stack + mounts + env vars
├── ingestion/
│   ├── ingest_to_gcs.py                 # downloads ZIPs -> uploads CSVs to gs://.../raw/<month>/
│   └── load_to_bq.py                    # loads from GCS -> BQ table (partition + clustering)
├── dbt/
│   ├── profiles.yml                     # dbt profile (used inside Airflow container)
│   ├── keys/
│   │   └── my-creds.json                # service account key for dbt/airflow
│   └── citibike_dbt/                    # dbt project + models
├── terraform/
│   ├── main.tf                          # creates GCS bucket + BQ dataset
│   ├── variables.tf                     # default project/bucket/dataset + credentials path
│   └── keys/
│       └── my-creds.json                # service account key for Terraform
├── requirements.txt                     # Python deps for running ingestion/load locally
├── .env.example                         # template for local (non-Docker) runs
└── .env                                 # local env vars (gitignored; copy from .env.example)
```

---

## ✅ What’s correct / what to watch out for

- **Airflow + dbt integration is wired correctly**: the DAG runs dbt with `--profiles-dir /opt/airflow/dbt`, which matches the Docker mount of `../dbt` → `/opt/airflow/dbt`.
- **BigQuery load job is partitioned and clustered**: `load_to_bq.py` partitions on `started_at` and clusters on station IDs.
- **Important**: `ingestion/ingest_to_gcs.py` currently **deletes the bucket** (`remove_bucket_if_exists`) before recreating it.
  - If you provision the bucket with Terraform, this behavior can fight with IaC expectations.
  - Recommended: either **remove/disable bucket deletion** in code for “real” runs, or treat ingestion as a fully-managed ephemeral bucket step.

---

## 🧰 Prerequisites (local machine)

### Required

- **Docker + Docker Compose**
- **GCP Project with billing enabled**
- **Service account JSON key** (see next section)

### For running scripts locally (optional)

- **Python 3.10+**
- A virtual environment tool (`venv`, `uv`, `poetry`, etc.)

### For Terraform (optional, but recommended)

- **Terraform** installed locally

---

## 🔐 GCP Account & Permissions Preparation

### 1) Create / choose a GCP project

- Create a project (or reuse one) and ensure **billing is enabled**.
- The repo defaults assume:
  - **Project ID**: `citibike-zoomcamp`
  - **BQ dataset**: `citibike`
  - **GCS bucket**: `citibike-data-lake-zoomcamp`

You can change these via:

- `.env` for ingestion/load runtime
- `terraform/variables.tf` (or `-var ...`) for provisioning
- `dbt/profiles.yml` for dbt
- `airflow/docker-compose.yaml` for container runtime env vars

### 2) Enable required APIs

Enable at least:

- **BigQuery API**
- **Cloud Storage API**
- **IAM API** (for service accounts)

(If you use Terraform to provision, you may also need Service Usage permissions to enable APIs.)

### 3) Create a service account + key

Create a service account used by:

- Terraform (create bucket + dataset)
- Airflow ingestion/load operators
- dbt (BigQuery)

Recommended IAM roles (minimum practical set for this repo):

- **BigQuery Admin** (or narrower: BigQuery Data Editor + BigQuery Job User + dataset create)
- **Storage Admin** (bucket create/delete + object writes)

Then create and download a JSON key file.

### 4) Place credentials in the expected paths

- **Terraform**: `terraform/keys/my-creds.json` (from `terraform/keys/my-creds.example.json`).
- **Airflow + Docker**: `dbt/keys/my-creds.json` (from `dbt/keys/my-creds.example.json`) — see **Root concept** above; profile `keyfile` must stay as `/opt/airflow/keys/my-creds.json`.
- **Local Python only**: you can keep the key anywhere; set `GOOGLE_APPLICATION_CREDENTIALS` and point `dbt/profiles.yml` → `keyfile` to that same path.

Inside Airflow containers:

- `GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/keys/my-creds.json`
- Mount: `../dbt/keys` → `/opt/airflow/keys`

---

## 📦 Library / Environment Preparation

### Option A: Airflow + Docker (**my-creds + profiles mount**)

1. Copy `dbt/keys/my-creds.example.json` → `dbt/keys/my-creds.json` and paste your real service account JSON.
2. Keep `dbt/profiles.yml` under `dbt/` with `keyfile: /opt/airflow/keys/my-creds.json` (container path).
3. Start Compose from `airflow/` — the whole `dbt/` folder is mounted at `/opt/airflow/dbt`, so the profile is picked up with `--profiles-dir /opt/airflow/dbt`.

You do **not** need `.env` for the default container setup; pipeline settings come from `docker-compose.yaml` env vars.

### Option B: Local only — direct Python ingestion + dbt (**`.env`**)

1. Copy `.env.example` → `.env` and set `GCP_PROJECT_ID`, `GCS_BUCKET`, `BASE_URL`, `MONTHS` (and optionally `BQ_DATASET`).
2. Activate the repo venv and install pins:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

3. Point auth at your key file and load `.env`:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/your-service-account.json"
set -a && source .env && set +a
python ingestion/ingest_to_gcs.py
python ingestion/load_to_bq.py
```

4. For **dbt** on the host, edit `dbt/profiles.yml` so `keyfile:` is the **same** host path as `GOOGLE_APPLICATION_CREDENTIALS`, then:

```bash
cd dbt/citibike_dbt
dbt run --profiles-dir ../
dbt test --profiles-dir ../
```

---

## 1) 🏗️ Terraform Preparation (bucket + dataset)

### What Terraform provisions in this repo

`terraform/main.tf` creates:

- **GCS bucket**: `google_storage_bucket.citibike_bucket`
- **BigQuery dataset**: `google_bigquery_dataset.citibike_dataset`

Defaults are defined in `terraform/variables.tf`:

- `credentials` defaults to `./keys/my-creds.json`
- `project` defaults to `citibike-zoomcamp`
- `bq_dataset_name` defaults to `citibike`
- `gcs_bucket_name` defaults to `citibike-data-lake-zoomcamp`
- `location` defaults to `US`

### Run Terraform

```bash
cd terraform
terraform init
terraform apply
```

### Credentials file

Terraform expects:

```
terraform/keys/my-creds.json
```

---

## 2) 📥 Ingestion (GCS) — what it does

`ingestion/ingest_to_gcs.py`:

- downloads monthly ZIPs from `BASE_URL` (default: `https://s3.amazonaws.com/tripdata`)
- unzips to `/tmp/data`
- uploads CSVs to:

```
gs://<GCS_BUCKET>/raw/<month>/<month>*.csv
```

### Important behavior

It currently calls `remove_bucket_if_exists(...)`, meaning it will:

- delete the whole bucket, delete its objects, then recreate the bucket

If you want a safer behavior, update the script to **skip bucket deletion** and only create if missing.

---

## 3) 📤 Load to BigQuery (raw table)

`ingestion/load_to_bq.py` loads:

- **Source**: `gs://<bucket>/raw/<month>/*.csv`
- **Target table**: `<project>.<dataset>.trips_raw`

Defaults:

- `BQ_DATASET` defaults to `citibike` if not set
- table name is hardcoded as `trips_raw`

Table optimizations:

- **Partition**: by day on `started_at`
- **Cluster**: `start_station_id`, `end_station_id`

---

## 4) 🔄 dbt Transformation (staging + mart)

### dbt profile

Airflow runs dbt using:

- `--profiles-dir /opt/airflow/dbt`

The repo mounts `../dbt` to `/opt/airflow/dbt`, so the profile file used is:

- `dbt/profiles.yml`

The profile currently targets:

- `project`: `citibike-zoomcamp`
- `dataset`: `citibike` (raw dataset)
- `keyfile`: `/opt/airflow/keys/my-creds.json`
- `location`: `US`

### dbt datasets/schemas created

Models declare schemas directly:

- **Raw source**: dataset `citibike`, table `trips_raw` (`models/staging/schema.yml`)
- **Staging models**: schema `staging` (example: `stg_trips.sql`)
- **Mart models**: schema `mart` (fact + aggregates)

So you’ll end up with BigQuery datasets/schemas like:

- `citibike.trips_raw` (loaded by Python)
- `staging.stg_trips` (dbt)
- `mart.fct_trips`, `mart.agg_trips_by_month`, `mart.agg_trips_by_type` (dbt)

### Run dbt manually (outside Airflow)

If you have dbt installed locally, you can run:

```bash
cd dbt/citibike_dbt
dbt run --profiles-dir ../
dbt test --profiles-dir ../
```

If you do this locally, you’ll likely need to change `keyfile:` in `dbt/profiles.yml` to a local path (since `/opt/airflow/...` is a container path).

---

## 5) 🐳 Docker / Airflow (how it’s wired)

### Python libraries inside the Airflow container

The Airflow Docker image installs extra Python packages at container start via `_PIP_ADDITIONAL_REQUIREMENTS` in `airflow/docker-compose.yaml` (includes `dbt-bigquery`, `google-cloud-storage`, `google-cloud-bigquery`, `python-dotenv`, `requests`).

### Volumes mounted by `airflow/docker-compose.yaml`

These mounts are what make the DAG able to import Python scripts and run dbt:

- `airflow/dags` → `/opt/airflow/dags`
- `ingestion/` → `/opt/airflow/ingestion`
- `dbt/` → `/opt/airflow/dbt`
- `dbt/keys/` → `/opt/airflow/keys` (**service account JSON lives here**)
- `ingestion/data/` → `/opt/airflow/data` (present for local persistence if used)

### Credentials mount + env var

The compose file sets:

- `GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/keys/my-creds.json`

So you must have:

- `dbt/keys/my-creds.json` on your host machine

### Start Airflow

```bash
cd airflow
docker compose up airflow-init
docker compose up
```

Airflow UI:

- `http://localhost:8080`
- default login created by init step: `airflow / airflow`

### Run the pipeline

In the Airflow UI:

- enable `citibike_pipeline`
- trigger a run

The DAG task order is:

- `ingest_to_gcs` → `load_to_bq` → `dbt_run` → `dbt_test`

---

## 6) 📊 Dashboard (Looker Studio)

Connect Looker Studio to the BigQuery tables in the `mart` schema/dataset and build visuals such as:

- total trips
- trips by type
- monthly trends
- avg duration trend

Add your dashboard link here:

- **Looker Studio dashboard**: *https://datastudio.google.com/reporting/920196de-d967-4527-acba-ad8c73d8b24d*

---

## ⚠️ Operational Notes / Improvements

- **Credentials in repo**: this repo includes `my-creds.json` paths under `dbt/keys/` and `terraform/keys/`. In a real project, do **not commit** service account keys; use secret management or `.gitignore`.
- **Terraform state files**: `terraform/terraform.tfstate` is present. In a real project, keep state in a remote backend (e.g., GCS) and don’t commit local state.
- **Bucket deletion**: ingestion currently deletes the bucket on each run; consider removing that for safety/cost control.

