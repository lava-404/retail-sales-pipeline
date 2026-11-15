"""Independent reference calculation straight from the CSV (pandas).
Use it to cross-check what BigQuery/dbt/Streamlit report. Nothing here feeds the app.
"""
import pandas as pd

df = pd.read_csv("data/retail_sales_dataset.csv", parse_dates=["Date"])
print("Revenue by category\n", df.groupby("Product Category")["Total Amount"].sum().sort_values(ascending=False), "\n")
print("Units by category\n", df.groupby("Product Category")["Quantity"].sum().sort_values(ascending=False), "\n")
print("Average transaction value:", round(df["Total Amount"].mean(), 2), "\n")
print("Monthly revenue\n", df.groupby(df["Date"].dt.to_period("M"))["Total Amount"].sum(), "\n")
bins = [0, 24, 34, 44, 54, 64, 200]
labels = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
df["age_group"] = pd.cut(df["Age"], bins=bins, labels=labels)
print("Revenue by age group\n", df.groupby("age_group", observed=True)["Total Amount"].sum(), "\n")
print("Revenue by gender\n", df.groupby("Gender")["Total Amount"].sum())
