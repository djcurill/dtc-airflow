"""
Author: Dan Curilla
Description: Upload yellow taxi trips to GCP
"""
import os
from datetime import datetime


from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from google.cloud import storage
from utils.schema import df_snake_case

BASE_URL = f"https://d37ci6vzurychx.cloudfront.net/trip-data"
FILE_FORMAT = "parquet"
GCP_GCS_BUCKET = os.environ.get("GCP_GCS_BUCKET")
DATA_DIR = "/home/airflow/gcs/data"


def upload_to_gcs(bucket_name: str, prefix: str, local_path: str):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(prefix)
    blob.upload_from_filename(local_path)


default_args = {"depends_on_past": False, "retries": 1}

with DAG(
    dag_id="upload_taxi",
    description="Upload nyc taxi trips data to gcp",
    schedule_interval="@monthly",
    start_date=datetime(2019, 1, 1),
    catchup=False,
    max_active_runs=2,
    tags=["GCP", "BigQuery", "Upload"],
    default_args=default_args,
) as dag:

    year_month = '{{ macros.ds_format(ds, "%Y-%m-%d", "%Y-%m") }}'
    dataset_file = f"yellow_tripdata_{year_month}.{FILE_FORMAT}"
    url = f"{BASE_URL}/{dataset_file}"

    t1 = BashOperator(
        task_id="wget",
        bash_command=f"curl -sSL {url} > {DATA_DIR}/{dataset_file}",
    )

    t2 = PythonOperator(
        task_id="to_snake_case",
        python_callable=df_snake_case,
        op_args=(f"{DATA_DIR}/{dataset_file}",)
    )

    t3 = PythonOperator(
        task_id="gcs_upload",
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket_name": GCP_GCS_BUCKET,
            "prefix": f"raw/{dataset_file}",
            "local_path": f"{DATA_DIR}/{dataset_file}",
        },
    )

    t1 >> t2 >> t3
