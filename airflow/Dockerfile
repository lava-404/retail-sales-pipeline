FROM apache/airflow:2.10.5-python3.11
USER airflow
# Providers + dbt live in the Airflow image so BashOperator can call dbt directly.
RUN pip install --no-cache-dir \
    apache-airflow-providers-airbyte \
    apache-airflow-providers-google \
    "dbt-bigquery>=1.8,<2.0"
