with m as (
    select
        transaction_month,
        year_month,
        count(*)                       as transactions,
        sum(quantity)                  as units_sold,
        sum(total_amount)              as revenue,
        round(avg(total_amount), 2)    as avg_transaction_value
    from {{ ref('fct_sales') }}
    group by transaction_month, year_month
)
select
    *,
    round(safe_divide(revenue - lag(revenue) over (order by transaction_month),
                      lag(revenue) over (order by transaction_month)) * 100, 2) as revenue_mom_change_pct
from m
