
from google.cloud import bigquery
from pathlib import Path

PROJECT_ID = "ambient-climate-514813-d4"
DATASET_ID = "retail_raw"
TABLE_ID = "retail_sales_dataset"

client = bigquery.Client(project=PROJECT_ID)

csv_path = Path("data/retail_sales_dataset.csv")

target = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
staging = f"{PROJECT_ID}.{DATASET_ID}.retail_sales_csv_staging"

# Load original CSV into a temporary, unpartitioned table.
config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    autodetect=True,
    write_disposition="WRITE_TRUNCATE",
)

with csv_path.open("rb") as file:
    job = client.load_table_from_file(file, staging, job_config=config)

job.result()
print("CSV loaded into temporary table.")

# Insert records while supplying the metadata required
# by the existing partitioned Airbyte-compatible table.
query = f"""
INSERT INTO `{target}` (
    _airbyte_raw_id,
    _airbyte_extracted_at,
    _airbyte_meta,
    _airbyte_generation_id,
    Age,
    Date,
    Gender,
    Quantity,
    Customer_ID,
    Total_Amount,
    Price_per_Unit,
    Transaction_ID,
    Product_Category
)
SELECT
    GENERATE_UUID(),
    CURRENT_TIMESTAMP(),
    JSON '{{}}',
    0,
    SAFE_CAST(Age AS NUMERIC),
    CAST(Date AS STRING),
    CAST(Gender AS STRING),
    SAFE_CAST(Quantity AS NUMERIC),
    CAST(Customer_ID AS STRING),
    SAFE_CAST(Total_Amount AS NUMERIC),
    SAFE_CAST(Price_per_Unit AS NUMERIC),
    SAFE_CAST(Transaction_ID AS NUMERIC),
    CAST(Product_Category AS STRING)
FROM `{staging}`
"""

client.query(query).result()

count = client.get_table(target).num_rows
print(f"Successfully loaded {count} records into {target}")

client.delete_table(staging, not_found_ok=True)
print("Temporary table removed.")
