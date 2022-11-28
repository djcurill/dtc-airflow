"""
Author: Daniel Curilla
Description: Upload for hire vehicle trips to GCP
"""
import os
from datetime import datetime, timedelta

from utils.schema import transform_fhv_schema, df_snake_case
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import \
    LocalFilesystemToGCSOperator

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
FILE_FORMAT = "parquet"
GCP_GCS_BUCKET = os.environ.get("GCP_GCS_BUCKET")
DATA_DIR = "/home/airflow/gcs/data"

with DAG(
    dag_id="upload_fhv",
    description="Upload for hire vehicles to GCP",
    start_date=datetime(2019, 1, 1),
    end_date=datetime(2020, 1, 1),
    schedule_interval="@monthly",
    max_active_runs=1,
    catchup=True,
    default_args={
        "retries": 3,
        "retry_delay": timedelta(seconds=15)
    }
) as dag:

    year_month = "{{ macros.ds_format(ds, '%Y-%m-%d', '%Y-%m') }}"
    dataset_file = f"fhv_tripdata_{year_month}.{FILE_FORMAT}"
    url = f"{BASE_URL}/{dataset_file}"

    t1 = BashOperator(
        task_id="curl",
        bash_command=f"curl -sSL {url} > {DATA_DIR}/{dataset_file}",
    )

    t2 = PythonOperator(
        task_id="tranform_fhv_schema",
        python_callable=transform_fhv_schema,
        op_args=(f"{DATA_DIR}/{dataset_file}",))

    t3 = PythonOperator(
        task_id="to_snake_case",
        python_callable=df_snake_case,
        op_args=(f"{DATA_DIR}/{dataset_file}",)
    )

    t4 = LocalFilesystemToGCSOperator(
        task_id="upload",
        src=f"{DATA_DIR}/{dataset_file}",
        dst=f"raw/fhv/{dataset_file}",
        bucket=GCP_GCS_BUCKET,
    )

    t5 = BashOperator(task_id="rm", bash_command=f"rm {DATA_DIR}/{dataset_file}")

    t1 >> t2 >> t3 >> t4 >> t5
