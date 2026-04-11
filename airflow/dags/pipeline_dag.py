from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
import sys

# 🔥 path ke ingestion
sys.path.append('/opt/airflow/ingestion')

from ingest_to_gcs import run_ingestion
from load_to_bq import run_load


default_args = {
    "owner": "dian",
    "start_date": datetime(2025, 1, 1),
    "retries": 1,
}


with DAG(
    dag_id="citibike_pipeline",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    ingest = PythonOperator(
        task_id="ingest_to_gcs",
        python_callable=run_ingestion
    )

    load = PythonOperator(
        task_id="load_to_bq",
        python_callable=run_load
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="""
        cd /opt/airflow/dbt/citibike_dbt &&
        dbt run \
        --profiles-dir /opt/airflow/dbt \
        --log-path /tmp/dbt_logs \
        --target-path /tmp/dbt_target
        """
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="""
        cd /opt/airflow/dbt/citibike_dbt &&
        dbt test \
        --profiles-dir /opt/airflow/dbt \
        --log-path /tmp/dbt_logs \
        --target-path /tmp/dbt_target
        """
    )

    ingest >> load >> dbt_run >> dbt_test