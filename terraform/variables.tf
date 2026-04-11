variable "project" {
  description = "GCP Project ID"
  default     = "citibike-zoomcamp"
}

variable "credentials" {
  description = "Path to service account JSON"
  default     = "./keys/my-creds.json"
}

variable "region" {
  description = "GCP Region"
  default     = "us-central1"
}

variable "location" {
  description = "GCP Location for BigQuery and GCS"
  default     = "US"
}

# =========================
# BIGQUERY
# =========================
variable "bq_dataset_name" {
  description = "BigQuery dataset for Citi Bike project"
  default     = "citibike"
}

# =========================
# GCS
# =========================
variable "gcs_bucket_name" {
  description = "GCS bucket for Citi Bike data lake"
  default     = "citibike-data-lake-zoomcamp"
}

variable "gcs_storage_class" {
  description = "Storage class for GCS bucket"
  default     = "STANDARD"
}