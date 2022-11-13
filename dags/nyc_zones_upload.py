"""
Author: Daniel Curilla
Description: Upload zones as a single batch job
"""
import os
import re
from datetime import datetime

import pyarrow.csv as csv
import pyarrow.parquet as pq
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import \
    LocalFilesystemToGCSOperator

URL = "'https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv'"
FILE_NAME = "gcs/data/zones/taxi_zone_lookup"
FILE_FORMAT = "csv"
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME")
GCP_GCS_BUCKET = os.environ.get("GCP_GCS_BUCKET")
default_args = {"depends_on_past": False, "retries": 1}


def to_parquet(path: str, ti):
    if os.path.isfile(path):
        tbl = csv.read_csv(path)
        parquet_path = re.sub(".csv$", ".parquet", path)
        pq.write_table(tbl, parquet_path)
        return parquet_path
    else:
        raise FileNotFoundError(f"File with path: {path} not found")


with DAG(
    dag_id="upload_zones",
    description="Upload for taxi zones to GCP",
    start_date=datetime(2019, 1, 1),
    schedule_interval="@once",
    catchup=False,
) as dag:

    t1 = BashOperator(
        task_id="curl",
        bash_command=f"curl -sSL {URL} > {AIRFLOW_HOME}/{FILE_NAME}.csv",
    )

    t2 = PythonOperator(
        task_id="parquetize",
        python_callable=to_parquet,
        op_kwargs={"path": f"{AIRFLOW_HOME}/{FILE_NAME}.csv"},
    )

    t3 = LocalFilesystemToGCSOperator(
        task_id="upload",
        src='{{ task_instance.xcom_pull(task_ids="parquetize") }}',
        dst=f"raw/fhv/{FILE_NAME}.parquet",
        bucket=GCP_GCS_BUCKET,
    )

    t1 >> t2 >> t3
