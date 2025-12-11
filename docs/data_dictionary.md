# Data Dictionary

## /data/users.csv
| Column | Type | Description |
|---|---|---|
| customer_id | String | Unique identifier for the user. Primary Key. |
| signup_date | Date | Date when the user created their account (YYYY-MM-DD). |
| country | String | User's geographical location. |
| pricing_plan | String | The initial plan selected during signup (e.g., Basic, Pro). |
| acquisition_channel | String | Marketing channel source (e.g., Organic, Paid Ads). |
| status | String | Current account status (active, cancelled). |

## /data/events.csv
| Column | Type | Description |
|---|---|---|
| event_id | String | Unique identifier for the event. |
| customer_id | String | Foreign key linking to users.csv. |
| event_name | String | The specific action taken (e.g., `login`, `activate`, `campaign_create`). |
| event_timestamp | Datetime | The exact time the event occurred (ISO 8601). |

## /data/subscriptions.csv
| Column | Type | Description |
|---|---|---|
| subscription_id | String | Unique identifier for the subscription. Primary Key. |
| customer_id | String | Foreign key linking to users.csv. |
| plan | String | The name of the subscription plan (e.g., basic, pro, enterprise). |
| start_date | Date | The date the subscription became active (YYYY-MM-DD). |
| end_date | Date | The date the subscription ended (YYYY-MM-DD). Empty/null if active. |
| status | String | Subscription status (active, cancelled). |
| price | Float | The subscription price in USD. Billing frequency determined by billing_period. |
| billing_period | String | Billing frequency: `monthly` or `annual`. Used to normalize to MRR. |

**MRR Normalization Logic:**
- If `billing_period = "monthly"`: `monthly_price = price`
- If `billing_period = "annual"`: `monthly_price = price / 12`

## /data/revenue.csv
| Column | Type | Description |
|---|---|---|
| invoice_id | String | Unique identifier for a billing transaction. |
| customer_id | String | Foreign key linking to users.csv. |
| amount | Float | The billed amount in USD. |
| revenue_date | Date | The date the revenue was recognized (YYYY-MM-DD). |
| revenue_type | String | Classification of revenue type. See below. |

**Revenue Type Semantics:**
- `recurring`: Regular subscription payments (monthly/annual renewals)
- `expansion`: Revenue from upgrades, add-ons, or upsells
- `one_time`: Non-recurring charges (setup fees, one-time purchases)
- `churn`: Revenue lost from cancellations (negative or zero)

## /data/marketing_costs.csv (Optional)
| Column | Type | Description |
|---|---|---|
| month | Date | Month of marketing spend (YYYY-MM-DD, first day of month). |
| cost | Float | Total marketing costs for the month in USD. |

**Note:** This file is optional. If not present, CAC and payback period metrics will be null.

## /outputs/kpi_summary.csv
| Column | Type | Description |
|---|---|---|
| run_date | Datetime | Timestamp when the metrics were computed (ISO 8601). |
| active_users | Integer | Count of users with status = "active". |
| active_last_30_days | Integer | Count of users who signed up in the last 30 days. |
| signup_count | Integer | Total count of all signups. |
| activation_count | Integer | Count of users who activated within 14 days. |
| churn_count | Integer | Count of subscriptions that ended in the analysis period. |
| churn_rate | Float | MRR-based churn rate (0.0 to 1.0). |
| activation_rate | Float | Percentage of signups that activated (0.0 to 1.0). |
| avg_ltv | Float | Customer Lifetime Value (ARPU / churn_rate). Null if churn = 0. |
| total_mrr | Float | Total Monthly Recurring Revenue (sum of active subscription monthly_price). |
| total_arr | Float | Total Annual Recurring Revenue (MRR × 12). |
| net_revenue_retention | Float | NRR metric. Can be > 1.0 with expansion. Null if insufficient data. |
| gross_revenue_retention | Float | GRR metric (0.0 to 1.0). Null if insufficient data. |
| quick_ratio | Float | Growth efficiency (MRR expansion / MRR churn). Null if churn = 0. |
| customer_acquisition_cost | Float | CAC in USD. Null if marketing_costs.csv not available. |
| avg_revenue_per_user | Float | ARPU (MRR / active users). |
| customer_lifetime_months | Float | Average customer lifetime (1 / churn_rate). Null if churn = 0. |
| payback_period_months | Float | Months to recover CAC (CAC / ARPU). Null if CAC unavailable. |

## /outputs/tableau_ready/customer_master_extract.csv
| Column | Type | Description |
|---|---|---|
| customer_id | String | Unique user ID. |
| signup_date | Date | Account creation date. |
| current_plan | String | Most recent plan associated with the user. |
| last_payment_date | Date | Date of the last successful transaction. |
| total_lifetime_revenue | Float | Sum of all revenue from this user. |

