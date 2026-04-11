import os
import requests
import zipfile
from google.cloud import storage
from dotenv import load_dotenv


# =========================
# FUNCTIONS
# =========================
def get_config():
    load_dotenv()

    bucket_name = os.getenv("GCS_BUCKET")
    base_url = os.getenv("BASE_URL")
    months = os.getenv("MONTHS")

    if not bucket_name:
        raise ValueError("GCS_BUCKET not set")

    if not base_url:
        raise ValueError("BASE_URL not set")

    if not months:
        raise ValueError("MONTHS not set")

    location = os.getenv("GCS_BUCKET_LOCATION")
    if location is not None:
        location = location.strip() or None

    return bucket_name, base_url, months.split(","), location


def get_gcs_client():
    return storage.Client()


def remove_bucket_if_exists(client, bucket_name):
    bucket = client.bucket(bucket_name)
    if not bucket.exists():
        print(f"Bucket gs://{bucket_name} does not exist; nothing to remove.\n")
        return

    print(f"Removing existing bucket: gs://{bucket_name}")
    blobs = list(client.list_blobs(bucket_name))
    if blobs:
        bucket.delete_blobs(blobs)
    bucket.delete()
    print(f"Removed bucket: gs://{bucket_name}\n")


def ensure_bucket(client, bucket_name, location=None):
    bucket = client.bucket(bucket_name)
    if bucket.exists():
        return

    print(f"Creating bucket: gs://{bucket_name}")
    if location:
        client.create_bucket(bucket_name, location=location)
    else:
        client.create_bucket(bucket_name)
    print(f"Created bucket: gs://{bucket_name}\n")


def download_zip(url, path):
    print(f"Downloading: {url}")
    r = requests.get(url)
    r.raise_for_status()

    with open(path, "wb") as f:
        f.write(r.content)


def unzip_file(zip_path, extract_to):
    print(f"Unzipping: {zip_path}")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)


def upload_to_gcs(client, bucket_name, local_file, gcs_path):
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_path)

    print(f"Uploading → gs://{bucket_name}/{gcs_path}")
    blob.upload_from_filename(local_file)


# =========================
# MAIN PIPELINE
# =========================
def process_month(client, bucket_name, base_url, month, download_dir):
    zip_name = f"{month}-citibike-tripdata.zip"
    zip_path = os.path.join(download_dir, zip_name)

    url = f"{base_url}/{zip_name}"

    # 1. download
    download_zip(url, zip_path)

    # 2. unzip
    unzip_file(zip_path, download_dir)

    # 3. find extracted CSVs
    extracted_files = [
        f for f in os.listdir(download_dir)
        if f.startswith(month) and f.endswith(".csv")
    ]

    # 4. upload each CSV
    for file in extracted_files:
        local_path = os.path.join(download_dir, file)
        gcs_path = f"raw/{month}/{file}"

        upload_to_gcs(client, bucket_name, local_path, gcs_path)

    print(f"Finished month: {month}\n")


def run_ingestion():
    # config
    bucket_name, base_url, months, bucket_location = get_config()

    # runtime resources (SAFE)
    client = get_gcs_client()

    remove_bucket_if_exists(client, bucket_name)
    ensure_bucket(client, bucket_name, location=bucket_location)

    download_dir = "/tmp/data"
    os.makedirs(download_dir, exist_ok=True)

    for month in months:
        process_month(client, bucket_name, base_url, month, download_dir)


if __name__ == "__main__":
    run_ingestion()