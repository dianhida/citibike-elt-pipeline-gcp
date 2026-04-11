# Terraform (Infrastructure)

## What Terraform provisions

This module provisions the minimal GCP infrastructure for the pipeline:

- **GCS bucket** (data lake)
- **BigQuery dataset** (raw dataset used by ingestion/dbt sources)

Files:

- `main.tf`: resources + provider config
- `variables.tf`: default names and credentials path
- `keys/my-creds.json`: service account key (expected by default var)

## Versions

- Terraform: `v1.14.3` (observed in this environment)
- Provider: `hashicorp/google v7.16.0` (pinned in `.terraform.lock.hcl` and `main.tf`)

## Inputs (defaults)

See `variables.tf`:

- `project`: `citibike-zoomcamp`
- `location`: `US`
- `gcs_bucket_name`: `citibike-data-lake-zoomcamp`
- `bq_dataset_name`: `citibike`
- `credentials`: `./keys/my-creds.json`

## Setup

1. Put your service account key here:

```
terraform/keys/my-creds.json
```

2. Run:

```bash
terraform init
terraform apply
```

## Notes

- The bucket resource uses `force_destroy = true` (Terraform will delete objects on destroy).
- This repo currently contains local state files (`terraform.tfstate*`). For real usage, prefer a remote backend (e.g., GCS).

