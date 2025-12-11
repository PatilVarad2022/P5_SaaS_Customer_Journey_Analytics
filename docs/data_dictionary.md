# Data Dictionary

## /data/users.csv
| Column | Type | Description |
|---|---|---|
| customer_id | String | Unique identifier for the user. Primary Key. |
| signup_date | Date | Date when the user created their account (YYYY-MM-DD). |
| country | String | User's geographical location. |
| pricing_plan | String | The initial plan selected during signup (e.g., Basic, Pro). |
| acquisition_channel | String | Marketing channel source (e.g., Organic, Paid Ads). |
| status | String | Current account status (Active, Cancelled). |

## /data/events.csv
| Column | Type | Description |
|---|---|---|
| event_id | String | Unique identifier for the event. |
| customer_id | String | Foreign key linking to users.csv. |
| event_name | String | The specific action taken (e.g., `login`, `campaign_create`). |
| event_timestamp | Datetime | The exact time the event occurred (ISO 8601). |

## /data/subscriptions.csv
| Column | Type | Description |
|---|---|---|
| subscription_id | String | Unique identifier for the subscription. |
| customer_id | String | Foreign key linking to users.csv. |
| plan | String | The name of the subscription plan. |
| start_date | Date | The date the subscription became active. |
| end_date | Date | The date the subscription ended (Null if active). |
| status | String | Subscription status (Active, Churned, Past Due). |
| price | Float | Monthly recurring cost of the subscription. |

## /data/revenue.csv
| Column | Type | Description |
|---|---|---|
| invoice_id | String | Unique identifier for a billing transaction. |
| customer_id | String | Foreign key linking to users.csv. |
| amount | Float | The billed amount in USD. |
| revenue_date | Date | The date the revenue was recognized. |
| revenue_type | String | Classification: `new`, `recurring`, `expansion`, `churn`. |

## /exports/tableau_ready/customer_master_extract.csv
| Column | Type | Description |
|---|---|---|
| customer_id | String | Unique user ID. |
| signup_date | Date | Account creation date. |
| current_plan | String | Most recent plan associated with the user. |
| last_payment_date | Date | Date of the last successful transaction. |
| total_lifetime_revenue | Float | Sum of all revenue from this user. |
