"""
Author: Daniel Curilla
Description: Upload for hire vehicle trips to GCP
"""
import os
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import \
    LocalFilesystemToGCSOperator

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
FILE_FORMAT = "parquet"
GCP_GCS_BUCKET = os.environ.get("GCP_GCS_BUCKET")
AIRFLOW_STAGING_DIR = os.environ.get("AIRFLOW_STAGING_DIR")
GCS_LANDING_DIR = f"raw/fhv_trip_data"
default_args = {"depends_on_past": False, "retries": 1}

with DAG(
    dag_id="upload_fhv",
    description="Upload for hire vehicles to GCP",
    start_date=datetime(2019, 1, 1),
    end_date=datetime(2020, 1, 1),
    schedule_interval="@monthly",
    catchup=True,
) as dag:

    year_month = "{{ macros.ds_format(ds, '%Y-%m-%d', '%Y-%m') }}"
    dataset_file = f"fhv_tripdata_{year_month}.{FILE_FORMAT}"
    url = f"{BASE_URL}/{dataset_file}"

    t1 = BashOperator(
        task_id="curl",
        bash_command=f"mkdir -p {AIRFLOW_STAGING_DIR} && curl -sSL {url} > {AIRFLOW_STAGING_DIR}/{dataset_file}",
    )

    t2 = LocalFilesystemToGCSOperator(
        task_id="upload",
        src=f"{AIRFLOW_STAGING_DIR}/{dataset_file}",
        dst=f"{GCS_LANDING_DIR}/{dataset_file}",
        bucket=GCP_GCS_BUCKET,
    )

    t3 = BashOperator(task_id="rm", bash_command=f"rm {AIRFLOW_STAGING_DIR}/{dataset_file}")

    t1 >> t2 >> t3
