"""
Author: Dan Curilla
Description: Upload yellow taxi trips to GCP
"""
import os
from datetime import datetime

import pyarrow.parquet as pq
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import \
    BigQueryCreateExternalTableOperator
from google.cloud import storage
from pandas import DataFrame

BASE_URL = f"https://d37ci6vzurychx.cloudfront.net/trip-data"
FILE_FORMAT = "parquet"
GCP_GCS_BUCKET = os.environ.get("GCP_GCS_BUCKET")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", "trips_data_all")
GCP_PROJECT_ID = os.environ.get("GCS_PROJECT_ID")
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow")


def upload_to_gcs(bucket_name: str, prefix: str, local_path: str):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(prefix)
    blob.upload_from_filename(local_path)


default_args = {"depends_on_past": False, "retries": 1}

with DAG(
    dag_id="nyc_taxi_trips_upload",
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
        bash_command=f"curl -sSL {url} > {AIRFLOW_HOME}/{dataset_file}",
    )

    t2 = PythonOperator(
        task_id="gcs_upload",
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket_name": GCP_GCS_BUCKET,
            "prefix": f"raw/{dataset_file}",
            "local_path": f"{AIRFLOW_HOME}/{dataset_file}",
        },
    )

    t3 = BashOperator(task_id="rm", bash_command=f"rm {AIRFLOW_HOME}/{dataset_file}")

    t4 = BigQueryCreateExternalTableOperator(
        task_id="create_external_table",
        table_resource={
            "tableReference": {
                "projectId": GCP_PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "external_table",
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{GCP_GCS_BUCKET}/raw/{dataset_file}"],
            },
        },
    )

    t1 >> t2 >> t3 >> t4
