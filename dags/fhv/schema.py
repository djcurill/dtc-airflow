"""
test
"""
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

def transform_fhv_schema(path:str):
    fhv_schema = pa.schema([
    ("dispatching_base_num", pa.string()),
    ("pickup_datetime", pa.timestamp("us")),
    ("dropOff_datetime", pa.timestamp("us")),
    ("PUlocationID", pa.float64()),
    ("DOlocationID", pa.float64()),
    ("SR_Flag", pa.binary()),
    ("Affiliated_base_number", pa.string())
    ])
    table = pq.read_table(path)
    table.cast(fhv_schema)
    pq.write_table(table, path)

def transform_fhv_schema_v2(path:str):
    table = pq.read_table(path)
    df = table.to_pandas(timestamp_as_object=True)
    df['SR_Flag'] = df['SR_Flag'].fillna(0)
    df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], errors="coerce")
    df["dropOff_datetime"] = pd.to_datetime(df["dropOff_datetime"], errors="coerce")
    df = df.astype({
        'dispatching_base_num': str,
        "pickup_datetime": "datetime64[ns]",
        "dropOff_datetime": "datetime64[ns]",
        "PUlocationID": float,
        "DOlocationID": float,
        "SR_Flag": bool,
        "Affiliated_base_number": str
    })
    df.to_parquet(path)