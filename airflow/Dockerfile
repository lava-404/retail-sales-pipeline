
FROM apache/airflow:2.10.5-python3.11

USER airflow

# Install Airbyte provider with Airflow-compatible constraints
RUN pip install --no-cache-dir \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.11.txt" \
    "apache-airflow==2.10.5" \
    apache-airflow-providers-airbyte

# Install only the libraries this project actually needs
RUN pip install --no-cache-dir \
    "dbt-bigquery>=1.8,<2.0" \
    "google-cloud-bigquery>=3.0"
