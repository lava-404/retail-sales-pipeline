select
    gender,
    product_category,
    count(*)                                                   as transactions,
    sum(quantity)                                              as units_sold,
    sum(total_amount)                                          as revenue,
    round(avg(total_amount), 2)                                as avg_transaction_value
from {{ ref('fct_sales') }}
group by gender, product_category
