{#- One row per customer. In the supplied file every Customer ID appears once,
    so each customer has a single purchase; the model still works if repeat customers arrive. -#}
with per_customer as (
    select
        customer_id,
        any_value(gender)                                      as gender,
        any_value(age_group)                                   as age_group,
        count(*)                                               as transactions,
        sum(quantity)                                          as units_purchased,
        sum(total_amount)                                      as lifetime_revenue,
        round(avg(total_amount), 2)                            as avg_transaction_value,
        min(transaction_date)                                  as first_purchase_date,
        max(transaction_date)                                  as last_purchase_date,
        array_agg(product_category order by total_amount desc limit 1)[offset(0)] as top_category
    from {{ ref('fct_sales') }}
    group by customer_id
)
select
    *,
    transactions > 1                                           as is_repeat_customer,
    case
        when lifetime_revenue < 100  then '1 - Low (<100)'
        when lifetime_revenue < 500  then '2 - Medium (100-499)'
        when lifetime_revenue < 1000 then '3 - High (500-999)'
        else                              '4 - Premium (1000+)'
    end                                                        as spend_tier
from per_customer
