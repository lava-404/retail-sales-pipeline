"""Conversational BI for the retail sales marts in BigQuery."""
import os

import altair as alt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google.cloud import bigquery

from questions import QUESTIONS, BY_KEY
from router import route
from sql_guard import is_safe_select

load_dotenv()
PROJECT = os.environ["GCP_PROJECT_ID"]
MARTS_DATASET = os.environ.get("BQ_MARTS_DATASET", "retail_analytics_marts")
MARTS = f"{PROJECT}.{MARTS_DATASET}"

st.set_page_config(page_title="Retail Sales Insights", page_icon="🛍️", layout="wide")


@st.cache_resource
def client() -> bigquery.Client:
    return bigquery.Client(project=PROJECT, location=os.environ.get("BQ_LOCATION", "US"))


@st.cache_data(ttl=300, show_spinner="Querying BigQuery…")
def run(sql: str) -> pd.DataFrame:
    ok, reason = is_safe_select(sql, MARTS_DATASET)
    if not ok:
        raise ValueError(f"Blocked by SQL guard: {reason}")
    job_cfg = bigquery.QueryJobConfig(maximum_bytes_billed=100 * 1024 * 1024)  # 100 MB safety cap
    return client().query(sql, job_config=job_cfg).to_dataframe()


def draw_chart(df: pd.DataFrame, q) -> None:
    if q.chart == "none" or df.empty:
        return
    if q.chart == "line":
        c = alt.Chart(df).mark_line(point=True).encode(x=alt.X(q.x, sort=None), y=q.y, tooltip=list(df.columns))
    elif q.chart == "pie":
        c = alt.Chart(df).mark_arc(innerRadius=50).encode(theta=q.y, color=q.x, tooltip=list(df.columns))
    else:
        c = alt.Chart(df).mark_bar().encode(x=alt.X(q.x, sort="-y"), y=q.y, tooltip=list(df.columns))
    st.altair_chart(c, use_container_width=True)


def answer(q) -> None:
    sql = q.sql.format(marts=f"{MARTS}")
    df = run(sql)
    st.subheader(q.title)
    if q.headline and not df.empty:
        st.success(q.headline.format(**df.iloc[0].to_dict()))
    cols = st.columns(2)
    with cols[0]:
        st.dataframe(df, use_container_width=True, hide_index=True)
    with cols[1]:
        draw_chart(df, q)
    with st.expander("SQL executed"):
        st.code(sql.strip(), language="sql")


# ---------- layout ----------
st.title("🛍️ Retail Sales Insights")
st.caption(f"Answers come live from `{MARTS}` (dbt marts). Nothing on this page is hardcoded.")

try:
    kpi = run(f"select * from `{MARTS}.mart_sales_kpis`").iloc[0]
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total revenue", f"{kpi.total_revenue:,.0f}")
    k2.metric("Transactions", f"{int(kpi.total_transactions):,}")
    k3.metric("Avg transaction value", f"{kpi.avg_transaction_value:,.2f}")
    k4.metric("Top category", kpi.top_category_by_revenue)
except Exception as exc:  # noqa: BLE001
    st.error(f"Could not read the marts. Has the pipeline run? ({exc})")
    st.stop()

st.divider()
with st.sidebar:
    st.header("Ask a question")
    pick = st.radio("Suggested questions", [q.title for q in QUESTIONS], index=None)
    st.caption("Only predefined, read-only queries on the marts are executed.")

typed = st.chat_input("Ask about sales, categories, months, age groups, genders…")

if typed:
    with st.chat_message("user"):
        st.write(typed)
    matched = route(typed)
    with st.chat_message("assistant"):
        if matched is None:
            st.warning("I couldn't match that to a known question. Try one of these:")
            for q in QUESTIONS:
                st.markdown(f"- {q.title}")
        else:
            answer(matched)
elif pick:
    answer(next(q for q in QUESTIONS if q.title == pick))
else:
    st.info("Pick a suggested question in the sidebar or type your own below.")
