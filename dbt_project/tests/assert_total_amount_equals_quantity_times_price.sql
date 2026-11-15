-- Singular test: returns offending rows. Passes when zero rows come back.
select transaction_id, quantity, price_per_unit, total_amount, calculated_amount
from {{ ref('stg_retail_sales') }}
where not is_amount_consistent
