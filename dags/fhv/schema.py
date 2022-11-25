"""
test
"""
import pyarrow as pa
import pyarrow.parquet as pq

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