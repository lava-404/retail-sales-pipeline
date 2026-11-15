{#- Quarantine view: every record that failed a validation, with the reasons. -#}
select * from {{ ref('stg_retail_sales') }}
where not is_valid_record
