import os
from google.cloud import bigquery, storage
from dotenv import load_dotenv


def get_gcs_client():
    return storage.Client()

def get_bq_client(project_id):
    return bigquery.Client(project=project_id)

def get_config():
    load_dotenv()

    project_id = os.getenv("GCP_PROJECT_ID")
    dataset = os.getenv("BQ_DATASET", "citibike")
    table = "trips_raw"
    bucket = os.getenv("GCS_BUCKET")
    months = os.getenv("MONTHS").split(",")

    return project_id, dataset, table, bucket, months

def get_schema():
    schema = [
        bigquery.SchemaField("ride_id", "STRING"),
        bigquery.SchemaField("rideable_type", "STRING"),
        bigquery.SchemaField("started_at", "TIMESTAMP"),
        bigquery.SchemaField("ended_at", "TIMESTAMP"),
        bigquery.SchemaField("start_station_name", "STRING"),
        bigquery.SchemaField("start_station_id", "STRING"),  # 🔥 FIX
        bigquery.SchemaField("end_station_name", "STRING"),
        bigquery.SchemaField("end_station_id", "STRING"),    # 🔥 FIX
        bigquery.SchemaField("start_lat", "FLOAT"),
        bigquery.SchemaField("start_lng", "FLOAT"),
        bigquery.SchemaField("end_lat", "FLOAT"),
        bigquery.SchemaField("end_lng", "FLOAT"),
        bigquery.SchemaField("member_casual", "STRING"),
    ]

    return schema

# =========================
# LOAD FUNCTION
# =========================
def load_month(
    client, project_id, dataset, table, bucket, month, write_disposition
):
    uri = f"gs://{bucket}/raw/{month}/*.csv"
    table_id = f"{project_id}.{dataset}.{table}"

    print(f"\nLoading data for {month}")
    print(f"Source: {uri}")
    print(f"Destination: {table_id}")
    print(f"Write disposition: {write_disposition}")

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        schema=get_schema(),
        write_disposition=write_disposition,

        # 🔥 PARTITION
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="started_at",  # harus timestamp/datetime
        ),

        # 🔥 CLUSTER
        clustering_fields=[
            "start_station_id",
            "end_station_id"
        ],
    )

    load_job = client.load_table_from_uri(
        uri,
        table_id,
        job_config=job_config
    )

    load_job.result()  # wait until finished

    print(f"Finished loading {month}")


# =========================
# MAIN
# =========================
def run_load():
    project_id, dataset, table, bucket, months = get_config()
    client = get_bq_client(project_id)
    for i, month in enumerate(months):
        disposition = (
            bigquery.WriteDisposition.WRITE_TRUNCATE
            if i == 0
            else bigquery.WriteDisposition.WRITE_APPEND
        )
        load_month(
            client, project_id, dataset, table, bucket, month.strip(), disposition
        )

if __name__ == "__main__":
    run_load()