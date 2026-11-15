-- Every staged row must land either in fct_sales or in the quarantine view.
with counts as (
    select
        (select count(*) from {{ ref('stg_retail_sales') }})        as staged,
        (select count(*) from {{ ref('fct_sales') }})               as facts,
        (select count(*) from {{ ref('stg_dq_rejected_records') }}) as rejected
)
select * from counts where staged != facts + rejected
