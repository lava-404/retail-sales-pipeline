{#- Clean fact table: validated transactions plus reusable analytical attributes. -#}
select
    transaction_id,
    transaction_date,
    date_trunc(transaction_date, month)                  as transaction_month,
    format_date('%Y-%m', transaction_date)               as year_month,
    customer_id,
    gender,
    age,
    case
        when age between 18 and 24 then '18-24'
        when age between 25 and 34 then '25-34'
        when age between 35 and 44 then '35-44'
        when age between 45 and 54 then '45-54'
        when age between 55 and 64 then '55-64'
        else '65+ / under 18'
    end                                                  as age_group,
    product_category,
    quantity,
    price_per_unit,
    total_amount,
    case
        when total_amount < 100  then '1 - Low (<100)'
        when total_amount < 500  then '2 - Medium (100-499)'
        when total_amount < 1000 then '3 - High (500-999)'
        else                          '4 - Premium (1000+)'
    end                                                  as order_value_tier
from {{ ref('stg_retail_sales') }}
where is_valid_record
