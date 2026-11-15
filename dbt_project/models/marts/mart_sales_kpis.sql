with f as (select * from {{ ref('fct_sales') }}),
top_cat as (
    select product_category from f
    group by product_category order by sum(total_amount) desc limit 1
)
select
    sum(total_amount)                         as total_revenue,
    count(*)                                  as total_transactions,
    sum(quantity)                             as total_units_sold,
    round(avg(total_amount), 2)               as avg_transaction_value,
    count(distinct customer_id)               as distinct_customers,
    min(transaction_date)                     as first_transaction_date,
    max(transaction_date)                     as last_transaction_date,
    (select product_category from top_cat)    as top_category_by_revenue
from f
