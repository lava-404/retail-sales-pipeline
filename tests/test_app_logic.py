import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "streamlit_app"))
from questions import QUESTIONS  # noqa: E402
from router import route  # noqa: E402
from sql_guard import is_safe_select  # noqa: E402

CSV = os.path.join(os.path.dirname(__file__), "..", "data", "retail_sales_dataset.csv")


@pytest.mark.parametrize("text,key", [
    ("Which product category generates the highest revenue?", "top_category_revenue"),
    ("How does revenue change month by month?", "monthly_revenue"),
    ("What is the average transaction value?", "avg_transaction_value"),
    ("Which age group spends the most?", "top_age_group"),
    ("What is the distribution of sales across genders?", "gender_distribution"),
    ("Which category has the highest quantity sold?", "top_category_quantity"),
])
def test_router_maps_the_six_required_questions(text, key):
    assert route(text).key == key


def test_router_rejects_nonsense():
    assert route("what's the weather in Pune") is None


@pytest.mark.parametrize("q", QUESTIONS, ids=lambda q: q.key)
def test_predefined_sql_passes_guard(q):
    ok, why = is_safe_select(q.sql.format(marts="proj.retail_analytics_marts"), "retail_analytics_marts")
    assert ok, why


@pytest.mark.parametrize("sql", [
    "drop table `p.retail_analytics_marts.x`",
    "select * from `p.retail_raw.retail_sales`",
    "select 1 from `p.retail_analytics_marts.t`; delete from `p.retail_analytics_marts.t`",
    "select * from `p.retail_analytics_marts.t` -- hi",
])
def test_guard_blocks_unsafe_sql(sql):
    assert not is_safe_select(sql, "retail_analytics_marts")[0]


def test_source_dataset_is_intact():
    df = pd.read_csv(CSV)
    assert df.shape == (1000, 9)
    assert df["Transaction ID"].is_unique
    assert (df["Quantity"] * df["Price per Unit"] == df["Total Amount"]).all()
