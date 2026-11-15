{#- Staging: snake_case, proper types, and data-quality FLAGS.
    Rows are never dropped here; invalid rows stay visible via is_valid_record
    and are routed to stg_dq_rejected_records instead of being silently discarded. -#}
{% set c = var('raw_columns') %}

with source as (

    select * from {{ source('airbyte_raw', 'retail_sales') }}

),

typed as (

    select
        safe_cast(cast(`{{ c.transaction_id }}` as string) as int64)      as transaction_id,
        safe_cast(cast(`{{ c.date }}` as string) as date)                 as transaction_date,
        nullif(trim(cast(`{{ c.customer_id }}` as string)), '')           as customer_id,
        initcap(trim(cast(`{{ c.gender }}` as string)))                   as gender,
        safe_cast(cast(`{{ c.age }}` as string) as int64)                 as age,
        initcap(trim(cast(`{{ c.product_category }}` as string)))         as product_category,
        safe_cast(cast(`{{ c.quantity }}` as string) as int64)            as quantity,
        safe_cast(cast(`{{ c.price_per_unit }}` as string) as numeric)    as price_per_unit,
        safe_cast(cast(`{{ c.total_amount }}` as string) as numeric)      as total_amount,
        _airbyte_extracted_at                                             as loaded_at
    from source

),

checked as (

    select
        *,
        quantity * price_per_unit                                         as calculated_amount,
        count(*) over (partition by transaction_id)                       as transaction_id_count
    from typed

),

flagged as (

    select
        *,
        coalesce(transaction_id > 0 and transaction_id_count = 1, false)  as is_valid_transaction_id,
        (transaction_date is not null)                                    as is_valid_date,
        (customer_id is not null)                                         as is_valid_customer_id,
        coalesce(product_category in ('Beauty', 'Clothing', 'Electronics'), false) as is_valid_category,
        coalesce(gender in ('Male', 'Female'), false)                     as is_valid_gender,
        coalesce(age between 0 and 120, false)                            as is_valid_age,
        coalesce(quantity > 0 and price_per_unit > 0 and total_amount >= 0, false) as is_valid_numeric,
        coalesce(total_amount = calculated_amount, false)                 as is_amount_consistent
    from checked

)

select
    transaction_id,
    transaction_date,
    customer_id,
    gender,
    age,
    product_category,
    quantity,
    price_per_unit,
    total_amount,
    calculated_amount,
    is_valid_transaction_id,
    is_valid_date,
    is_valid_customer_id,
    is_valid_category,
    is_valid_gender,
    is_valid_age,
    is_valid_numeric,
    is_amount_consistent,
    (is_valid_transaction_id and is_valid_date and is_valid_customer_id
        and is_valid_category and is_valid_gender and is_valid_age
        and is_valid_numeric and is_amount_consistent)                    as is_valid_record,
    array_to_string([
        if(not is_valid_transaction_id, 'invalid_or_duplicate_transaction_id', null),
        if(not is_valid_date,           'invalid_date', null),
        if(not is_valid_customer_id,    'missing_customer_id', null),
        if(not is_valid_category,       'unexpected_product_category', null),
        if(not is_valid_gender,         'unexpected_gender', null),
        if(not is_valid_age,            'invalid_age', null),
        if(not is_valid_numeric,        'invalid_numeric_value', null),
        if(not is_amount_consistent,    'total_amount_mismatch', null)
    ], '; ')                                                              as dq_issues,
    loaded_at
from flagged
