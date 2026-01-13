-- models/gold/customer_kpis.sql
with base as (
  select
    customer_id,
    region,
    signup_date,
    max(last_active_date) as last_seen,
    count(distinct session_id) as session_count,
    count(case when status = 'churned' then 1 end) as churn_flag
  from {{ ref('silver_customer_activity') }}
  group by 1, 2, 3
)

select *,
  case
    when date_diff(current_date, last_seen, day) > 90 then 1
    else 0
  end as predicted_churn
from base
