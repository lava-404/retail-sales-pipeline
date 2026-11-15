with c as (
    select
        product_category,
        count(*)                         as transactions,
        sum(quantity)                    as units_sold,
        sum(total_amount)                as revenue,
        round(avg(total_amount), 2)      as avg_transaction_value,
        round(safe_divide(sum(total_amount), sum(quantity)), 2) as avg_realised_unit_price
    from {{ ref('fct_sales') }}
    group by product_category
)
select
    *,
    round(revenue / sum(revenue) over () * 100, 2)   as revenue_share_pct,
    rank() over (order by revenue desc)              as revenue_rank,
    rank() over (order by units_sold desc)           as units_rank
from c
