"""Step 0: programmatically inspect the CSV before anything is built.
Usage: python scripts/inspect_data.py [path-to-csv]
Exits non-zero if the schema or integrity assumptions are broken.
"""
import sys
import pandas as pd

PATH = sys.argv[1] if len(sys.argv) > 1 else "data/retail_sales_dataset.csv"
EXPECTED = ["Transaction ID", "Date", "Customer ID", "Gender", "Age",
            "Product Category", "Quantity", "Price per Unit", "Total Amount"]

df = pd.read_csv(PATH)
problems = []

print(f"shape            : {df.shape}")
print(f"columns          : {list(df.columns)}")
print(f"missing values   : {int(df.isna().sum().sum())}")
print(f"exact duplicates : {int(df.duplicated().sum())}")
print(f"transaction ids unique: {df['Transaction ID'].is_unique}")
print(f"date range       : {df['Date'].min()} -> {df['Date'].max()}")
print(f"categories       : {df['Product Category'].value_counts().to_dict()}")
print(f"genders          : {df['Gender'].value_counts().to_dict()}")
print(f"age range        : {df['Age'].min()} - {df['Age'].max()}")
print(f"distinct customers: {df['Customer ID'].nunique()}")
mismatch = int((df["Quantity"] * df["Price per Unit"] != df["Total Amount"]).sum())
print(f"total_amount != quantity * price_per_unit : {mismatch} rows")

if list(df.columns) != EXPECTED:
    problems.append("column list differs from expected schema")
if df.isna().any().any():
    problems.append("missing values present")
if not df["Transaction ID"].is_unique:
    problems.append("duplicate transaction ids")
if mismatch:
    problems.append(f"{mismatch} amount mismatches")
if pd.to_datetime(df["Date"], errors="coerce").isna().any():
    problems.append("unparseable dates")

if problems:
    print("\nDATA ISSUES:", *problems, sep="\n - ")
    sys.exit(1)
print("\nOK: schema and integrity checks passed")
