terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.16.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)
  project     = var.project
  region      = var.region
}

# =========================
# GCS BUCKET (Data Lake)
# =========================
resource "google_storage_bucket" "citibike_bucket" {
  name          = var.gcs_bucket_name
  location      = var.location
  storage_class = var.gcs_storage_class

  force_destroy = true

  labels = {
    project = "citibike"
    env     = "dev"
  }
}

# =========================
# BIGQUERY DATASET
# =========================
resource "google_bigquery_dataset" "citibike_dataset" {
  dataset_id  = var.bq_dataset_name
  location    = var.location
  description = "Dataset for Citi Bike ELT data pipeline (raw, staging, marts)"

  labels = {
    project = "citibike"
    env     = "dev"
  }
}