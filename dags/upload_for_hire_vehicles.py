"""
Author: Daniel Curilla
Description: Upload for hire vehicle trips to GCP
"""
import os
from datetime import datetime

from fhv.schema import transform_fhv_schema
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import \
    LocalFilesystemToGCSOperator

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
FILE_FORMAT = "parquet"
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow")
GCP_GCS_BUCKET = os.environ.get("GCP_GCS_BUCKET")

with DAG(
    dag_id="upload_fhv",
    description="Upload for hire vehicles to GCP",
    start_date=datetime(2019, 1, 1),
    end_date=datetime(2020, 1, 1),
    schedule_interval="@monthly",
    max_active_runs=2,
    catchup=True,
) as dag:

    year_month = "{{ macros.ds_format(ds, '%Y-%m-%d', '%Y-%m') }}"
    dataset_file = f"fhv_tripdata_{year_month}.{FILE_FORMAT}"
    url = f"{BASE_URL}/{dataset_file}"

    t1 = BashOperator(
        task_id="curl",
        bash_command=f"curl -sSL {url} > {AIRFLOW_HOME}/{dataset_file}",
    )

    t2 = PythonOperator(
        task_id="tranform_fhv_schema",
        python_callable=transform_fhv_schema,
        op_args=(f"{AIRFLOW_HOME}/{dataset_file}",))

    t3 = LocalFilesystemToGCSOperator(
        task_id="upload",
        src=f"{AIRFLOW_HOME}/{dataset_file}",
        dst=f"raw/fhv/{dataset_file}",
        bucket=GCP_GCS_BUCKET,
    )

    t4 = BashOperator(task_id="rm", bash_command=f"rm {AIRFLOW_HOME}/{dataset_file}")

    t1 >> t2 >> t3 >> t4
