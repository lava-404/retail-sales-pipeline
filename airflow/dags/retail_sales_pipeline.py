"""Retail sales pipeline.

start -> Airbyte sync -> dbt run -> dbt test -> data validation -> end

Airflow only coordinates. Airbyte moves the CSV into BigQuery, dbt transforms the
data inside BigQuery, and the validation task runs read-only SQL checks.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator

DBT_DIR = os.environ.get("DBT_PROJECT_DIR", "/opt/airflow/dbt_project")
DBT_CMD = f"cd {DBT_DIR} && dbt {{cmd}} --profiles-dir {DBT_DIR}"

default_args = {
    "owner": "data-engineering",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


def validate_warehouse(**_):
    """Post-dbt checks straight against BigQuery. Raises (task fails) on any problem."""
    from google.cloud import bigquery

    project = os.environ["GCP_PROJECT_ID"]
    raw = f"{project}.{os.environ.get('BQ_RAW_DATASET', 'retail_raw')}.{os.environ.get('RAW_TABLE', 'retail_sales')}"
    base = os.environ.get("BQ_ANALYTICS_DATASET", "retail_analytics")
    stg = f"{project}.{base}_staging"
    marts = f"{project}.{base}_marts"

    client = bigquery.Client(project=project, location=os.environ.get("BQ_LOCATION", "US"))

    def scalar(sql: str):
        return list(client.query(sql).result())[0][0]

    raw_rows = scalar(f"select count(*) from `{raw}`")
    stg_rows = scalar(f"select count(*) from `{stg}.stg_retail_sales`")
    fct_rows = scalar(f"select count(*) from `{marts}.fct_sales`")
    rejected = scalar(f"select count(*) from `{stg}.stg_dq_rejected_records`")
    fct_rev = scalar(f"select sum(total_amount) from `{marts}.fct_sales`")
    cat_rev = scalar(f"select sum(revenue) from `{marts}.mart_category_performance`")

    print(f"raw={raw_rows} staged={stg_rows} facts={fct_rows} rejected={rejected} "
          f"fct_revenue={fct_rev} category_revenue={cat_rev}")

    errors = []
    if raw_rows == 0:
        errors.append("raw table is empty")
    if raw_rows != stg_rows:
        errors.append(f"raw ({raw_rows}) != staging ({stg_rows})")
    if stg_rows != fct_rows + rejected:
        errors.append("rows lost between staging and facts")
    if fct_rev != cat_rev:
        errors.append("category mart revenue does not reconcile with fact table")
    expected = os.environ.get("EXPECTED_ROW_COUNT")
    if expected and int(expected) != raw_rows:
        errors.append(f"expected {expected} raw rows, found {raw_rows}")
    if errors:
        raise ValueError("Validation failed: " + "; ".join(errors))


with DAG(
    dag_id="retail_sales_pipeline",
    description="Airbyte -> BigQuery -> dbt -> validation for the retail sales dataset",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,          # manual trigger; use "@daily" for a scheduled run
    catchup=False,
    max_active_runs=1,
    tags=["retail", "airbyte", "dbt", "bigquery"],
) as dag:
    start = EmptyOperator(task_id="start")

    airbyte_ingestion = AirbyteTriggerSyncOperator(
        task_id="airbyte_ingestion",
        airbyte_conn_id="airbyte_default",
        connection_id=os.environ.get("AIRBYTE_CONNECTION_ID", ""),
        asynchronous=False,      # block until the sync finishes so dbt only runs after success
        timeout=1800,
        wait_seconds=10,
    )

    dbt_run = BashOperator(task_id="dbt_run", bash_command=DBT_CMD.format(cmd="run"))
    dbt_test = BashOperator(task_id="dbt_test", bash_command=DBT_CMD.format(cmd="test"))

    data_validation = PythonOperator(task_id="data_validation", python_callable=validate_warehouse)

    end = EmptyOperator(task_id="end")

    start >> airbyte_ingestion >> dbt_run >> dbt_test >> data_validation >> end
