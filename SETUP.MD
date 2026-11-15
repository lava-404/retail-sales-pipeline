
## Setup & Installation (Windows)

### 1. Clone the Repository

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd retail-sales-pipeline
```

### 2. Create and Activate Virtual Environment

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Google Cloud Credentials

Place the Google Cloud service account JSON key inside:

```text
secrets/gcp-key.json
```

Set the credentials environment variable:

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:/Users/lavanyareddy/Downloads/retail-sales-pipeline/secrets/gcp-key.json"
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```dotenv
GCP_PROJECT_ID=ambient-climate-514813-d4
BQ_LOCATION=US

BQ_RAW_DATASET=retail_raw
RAW_TABLE=retail_sales_csv_staging

BQ_ANALYTICS_DATASET=retail_analytics
BQ_MARTS_DATASET=retail_analytics_marts

GOOGLE_APPLICATION_CREDENTIALS=C:/Users/lavanyareddy/Downloads/retail-sales-pipeline/secrets/gcp-key.json

EXPECTED_ROW_COUNT=1000
```

### 6. Configure dbt Profile

Create the dbt configuration directory:

```powershell
New-Item -ItemType Directory -Force "$HOME\.dbt"
```

Create `profiles.yml` inside `$HOME\.dbt` with the following configuration:

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
      keyfile: "C:/Users/lavanyareddy/Downloads/retail-sales-pipeline/secrets/gcp-key.json"
      threads: 4
      timeout_seconds: 300
      priority: interactive
```

### 7. Verify BigQuery Connection

```powershell
python -c "from google.cloud import bigquery; c=bigquery.Client(project='ambient-climate-514813-d4'); print([(t.table_id) for t in c.list_tables('ambient-climate-514813-d4.retail_raw')])"
```

### 8. Run dbt Transformations

```powershell
cd dbt_project

dbt debug --profiles-dir "$HOME/.dbt"

dbt run --profiles-dir "$HOME/.dbt"

dbt test --profiles-dir "$HOME/.dbt"

cd ..
```

### 9. Launch Streamlit Dashboard

```powershell
streamlit run streamlit_app/app.py
```

Open the dashboard:

```text
http://localhost:8501
```

### 10. Stop the Application

Press:

```text
Ctrl + C
```
