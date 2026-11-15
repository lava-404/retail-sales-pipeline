select
    order_value_tier,
    product_category,
    count(*)                       as transactions,
    sum(quantity)                  as units_sold,
    sum(total_amount)              as revenue,
    round(avg(quantity), 2)        as avg_quantity_per_transaction
from {{ ref('fct_sales') }}
group by order_value_tier, product_category
