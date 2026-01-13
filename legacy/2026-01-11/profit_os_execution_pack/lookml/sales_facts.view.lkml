view: sales_facts {
  sql_table_name: propulse-autonomax.profit_os_data.sales_fact ;;

  dimension: deal_id {
    primary_key: yes
    type: string
    sql: ${TABLE}.deal_id ;;
  }

  dimension: sales_rep {
    type: string
    sql: ${TABLE}.sales_rep ;;
  }

  measure: total_pipeline {
    type: sum
    sql: ${TABLE}.deal_value ;;
  }

  measure: avg_deal_size {
    type: average
    sql: ${TABLE}.deal_value ;;
  }

  measure: win_rate {
    type: number
    sql: CASE WHEN ${TABLE}.deal_stage = 'Closed Won' THEN 1 ELSE 0 END ;;
    value_format_name: percent_0
  }

  measure: quota_attainment {
    type: number
    sql: ${total_pipeline} / ${TABLE}.rep_quota ;;
    value_format_name: percent_1
  }
}
