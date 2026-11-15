# Airbyte setup (CSV → BigQuery)

> Airbyte's UI and connector options change between versions. Check each item against the
> Airbyte version you install; anything that differs is noted in your report as a deviation.

## 1. Install Airbyte locally
```bash
curl -LsfS https://get.airbyte.com | bash -     # installs abctl
abctl local install                              # UI at http://localhost:8000
abctl local credentials                          # prints the login + client id/secret
```
Put the client id / secret in `.env` (`AIRBYTE_CLIENT_ID`, `AIRBYTE_CLIENT_SECRET`).

## 2. Make the CSV reachable by the File source
Pick ONE:

**A. Local file** (simplest if your abctl version supports mounting a folder):
`abctl local install --volume <repo>/data:/local` then use storage provider *Local Filesystem*
with URL `/local/retail_sales_dataset.csv`.

**B. Google Cloud Storage** (works everywhere): upload the CSV to a bucket
(`gsutil cp data/retail_sales_dataset.csv gs://<bucket>/`) and use provider *GCS* with
`gs://<bucket>/retail_sales_dataset.csv` + the service-account JSON.

**C. Fallback required by the course guideline**: if neither works, load the CSV into
PostgreSQL and use the Postgres source instead. Document it as a simplified step.

## 3. Source: File (CSV)
| Field | Value |
|---|---|
| Dataset Name | `retail_sales`  (becomes the BigQuery table name = `RAW_TABLE`) |
| Format | csv |
| Storage Provider | per step 2 |
| URL | per step 2 |

## 4. Destination: BigQuery
| Field | Value |
|---|---|
| Project ID | your `GCP_PROJECT_ID` |
| Dataset Location | same as `BQ_LOCATION` |
| Default Dataset ID | `retail_raw` (= `BQ_RAW_DATASET`) |
| Loading method | Standard inserts (fine for 1,000 rows) |
| Service Account Key | contents of `secrets/gcp-key.json` (entered in the UI only) |

## 5. Connection
Stream `retail_sales`, sync mode **Full refresh | Overwrite** (the dataset is static, so reruns stay idempotent).
Run one manual sync, then verify:
```bash
bq show --schema --format=prettyjson $GCP_PROJECT_ID:retail_raw.retail_sales
bq query --use_legacy_sql=false "select count(*) from \`$GCP_PROJECT_ID.retail_raw.retail_sales\`"
```
Expected: 1,000 rows. **Compare the column names with `raw_columns` in `dbt_project/dbt_project.yml`** and edit that mapping if they differ.

Copy the connection UUID from the URL (`/connections/<uuid>/...`) into `AIRBYTE_CONNECTION_ID`.
