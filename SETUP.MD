# Retail Sales Analytics Pipeline — Setup Guide (Windows)

This guide explains how to clone, configure and run the Retail Sales Analytics Pipeline on Windows.

## 1. Prerequisites

Install:

- Python 3.11
- Git
- Docker Desktop
- Visual Studio Code

Ensure Docker Desktop is running before starting Airflow.

## 2. Clone the Repository

Open PowerShell:

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd retail-sales-pipeline
code .
```

## 3. Create a Python Virtual Environment

```powershell
py -3.11 -m venv .venv

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\.venv\Scripts\Activate.ps1
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

## 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

## 5. Configure Google Cloud Credentials

Place an authorized Google Cloud service account JSON key inside:

```text
secrets/gcp-key.json
```

Set the credentials environment variable:

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:/Users/<USERNAME>/Downloads/retail-sales-pipeline/secrets/gcp-key.json"
```

Replace `<USERNAME>` with the Windows username.

## 6. Configure Environment Variables

Create a `.env` file in the project root:

```dotenv
# Google Cloud / BigQuery
GCP_PROJECT_ID=ambient-climate-514813-d4
BQ_LOCATION=US

BQ_RAW_DATASET=retail_raw
RAW_TABLE=retail_sales_csv_staging

BQ_ANALYTICS_DATASET=retail_analytics
BQ_MARTS_DATASET=retail_analytics_marts

GOOGLE_APPLICATION_CREDENTIALS=C:/Users/<USERNAME>/Downloads/retail-sales-pipeline/secrets/gcp-key.json

# Validation
EXPECTED_ROW_COUNT=1000

# Airflow
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=change-me
```

## 7. Configure dbt Profile

Create the dbt configuration directory:

```powershell
New-Item -ItemType Directory -Force "$HOME\.dbt"
```

Create the following file:

`C:\Users\<USERNAME>\.dbt\profiles.yml`

```yaml
retail_sales:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: ambient-climate-514813-d4
      dataset: retail_analytics
      location: US
      keyfile: "C:/Users/<USERNAME>/Downloads/retail-sales-pipeline/secrets/gcp-key.json"
      threads: 4
      timeout_seconds: 300
      priority: interactive
```

Replace `<USERNAME>` with the Windows username.

## 8. Verify BigQuery Connectivity

From the project root:

```powershell
python -c "from google.cloud import bigquery; c=bigquery.Client(project='ambient-climate-514813-d4'); print([(t.table_id) for t in c.list_tables('ambient-climate-514813-d4.retail_raw')])"
```

## 