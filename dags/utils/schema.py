"""
test
"""
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
import re

def snake_case(s:str) -> str:
    """https://stackoverflow.com/questions/69079812/how-to-convert-string-to-snakecase-format-in-python"""
    return re.sub(r"(?<=[a-z])(?=[A-Z])|[^a-zA-Z]", "_", s).strip("_").lower()

def df_snake_case(path:str) -> None:
    df = pd.read_parquet(path)
    df.rename(columns = {col:snake_case(col) for col in df.columns}, inplace=True)
    df.to_parquet(path)

def transform_fhv_schema(path:str):
    table = pq.read_table(path)
    df = table.to_pandas(timestamp_as_object=True)
    # df['SR_Flag'] = df['SR_Flag'].fillna(0)
    # df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], errors="coerce")
    # df["dropOff_datetime"] = pd.to_datetime(df["dropOff_datetime"], errors="coerce")
    # df = df.astype({
    #     'dispatching_base_num': str,
    #     "pickup_datetime": "datetime64[ns]",
    #     "dropOff_datetime": "datetime64[ns]",
    #     "PUlocationID": float,
    #     "DOlocationID": float,
    #     "SR_Flag": bool,
    #     "Affiliated_base_number": str
    # })
    df.to_parquet(path)