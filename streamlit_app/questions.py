"""Predefined question -> SQL mappings. Every query reads the dbt marts, never raw data,
and no user text is ever interpolated into SQL (only the dataset name from the environment).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    key: str
    title: str
    sql: str                 # uses {marts} placeholder = `project.dataset`
    keywords: tuple          # used by the router
    chart: str               # "bar" | "line" | "pie" | "none"
    x: str | None = None
    y: str | None = None
    headline: str | None = None   # template filled from the first row, e.g. "{product_category}"


QUESTIONS: tuple[Question, ...] = (
    Question(
        key="top_category_revenue",
        title="Which product category generates the highest revenue?",
        sql="""
            select product_category, revenue, revenue_share_pct, transactions
            from `{marts}.mart_category_performance`
            order by revenue desc""",
        keywords=("category", "revenue", "highest", "top", "best", "product", "generates", "earns"),
        chart="bar", x="product_category", y="revenue",
        headline="{product_category} leads with {revenue:,.0f} in revenue ({revenue_share_pct}% of total)",
    ),
    Question(
        key="monthly_revenue",
        title="How does revenue change month by month?",
        sql="""
            select year_month, revenue, transactions, revenue_mom_change_pct
            from `{marts}.mart_monthly_sales`
            order by year_month""",
        keywords=("month", "monthly", "trend", "change", "over", "time", "month-by-month", "mom", "growth"),
        chart="line", x="year_month", y="revenue",
    ),
    Question(
        key="avg_transaction_value",
        title="What is the average transaction value?",
        sql="""
            select avg_transaction_value, total_transactions, total_revenue
            from `{marts}.mart_sales_kpis`""",
        keywords=("average", "avg", "mean", "transaction", "value", "order", "basket"),
        chart="none",
        headline="Average transaction value: {avg_transaction_value:,.2f} across {total_transactions:,} transactions",
    ),
    Question(
        key="top_age_group",
        title="Which age group spends the most?",
        sql="""
            select age_group, revenue, revenue_share_pct, avg_transaction_value, transactions
            from `{marts}.mart_age_group_sales`
            order by revenue desc""",
        keywords=("age", "group", "spends", "spend", "spending", "older", "younger", "demographic"),
        chart="bar", x="age_group", y="revenue",
        headline="{age_group} spends the most: {revenue:,.0f} ({revenue_share_pct}% of revenue)",
    ),
    Question(
        key="gender_distribution",
        title="What is the distribution of sales across genders?",
        sql="""
            select gender, sum(revenue) as revenue, sum(transactions) as transactions,
                   round(sum(revenue) / sum(sum(revenue)) over () * 100, 2) as revenue_share_pct
            from `{marts}.mart_gender_sales`
            group by gender
            order by revenue desc""",
        keywords=("gender", "male", "female", "men", "women", "distribution", "split"),
        chart="pie", x="gender", y="revenue",
    ),
    Question(
        key="top_category_quantity",
        title="Which category has the highest quantity sold?",
        sql="""
            select product_category, units_sold, revenue, units_rank
            from `{marts}.mart_category_performance`
            order by units_sold desc""",
        keywords=("quantity", "units", "sold", "volume", "most", "category", "pieces", "items"),
        chart="bar", x="product_category", y="units_sold",
        headline="{product_category} sold the most units: {units_sold:,.0f}",
    ),
    Question(
        key="customer_spend_tiers",
        title="How are customers spread across spend tiers?",
        sql="""
            select spend_tier, count(*) as customers, sum(lifetime_revenue) as revenue,
                   countif(is_repeat_customer) as repeat_customers
            from `{marts}.mart_customer_patterns`
            group by spend_tier
            order by spend_tier""",
        keywords=("customer", "customers", "tier", "tiers", "pattern", "patterns", "repeat", "segment", "purchasing"),
        chart="bar", x="spend_tier", y="customers",
    ),
)

BY_KEY = {q.key: q for q in QUESTIONS}
