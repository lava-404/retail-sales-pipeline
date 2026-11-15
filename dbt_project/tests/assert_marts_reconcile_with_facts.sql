-- Revenue must be identical across the fact table and every revenue mart.
with totals as (
    select
        (select sum(total_amount) from {{ ref('fct_sales') }})              as fct,
        (select sum(revenue) from {{ ref('mart_category_performance') }})   as by_category,
        (select sum(revenue) from {{ ref('mart_monthly_sales') }})          as by_month,
        (select sum(revenue) from {{ ref('mart_age_group_sales') }})        as by_age,
        (select sum(revenue) from {{ ref('mart_gender_sales') }})           as by_gender,
        (select sum(revenue) from {{ ref('mart_spend_tiers') }})            as by_tier,
        (select total_revenue from {{ ref('mart_sales_kpis') }})            as kpi
)
select * from totals
where fct != by_category or fct != by_month or fct != by_age
   or fct != by_gender or fct != by_tier or fct != kpi
