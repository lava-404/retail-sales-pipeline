select
    age_group,
    count(*)                                                   as transactions,
    count(distinct customer_id)                                as customers,
    sum(quantity)                                              as units_sold,
    sum(total_amount)                                          as revenue,
    round(avg(total_amount), 2)                                as avg_transaction_value,
    round(sum(total_amount) / sum(sum(total_amount)) over () * 100, 2) as revenue_share_pct,
    rank() over (order by sum(total_amount) desc)              as revenue_rank
from {{ ref('fct_sales') }}
group by age_group
