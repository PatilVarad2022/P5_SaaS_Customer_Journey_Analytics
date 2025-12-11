# Data Dictionary

## users.csv
| Column | Type | Description |
|---|---|---|
| customer_id | String | Canonical unique identifier for a user. |
| email | String | User email address. |
| signup_date | Date | Date of account creation (YYYY-MM-DD). |
| country | String | User's country. |
| pricing_plan | String | Initial pricing plan selected. |
| acquisition_channel | String | Channel where the user was acquired (e.g., Organic, Ads). |
| status | String | Current account status (Active, Cancelled). |

## events.csv
| Column | Type | Description |
|---|---|---|
| event_id | String | Unique event identifier. |
| customer_id | String | Foreign key to users.csv. |
| event_name | String | Name of the action (e.g., login, campaign_create). |
| event_timestamp | Datetime | Exact time of event (YYYY-MM-DDTHH:MM:SS). |

## subscriptions.csv
| Column | Type | Description |
|---|---|---|
| subscription_id | String | Unique subscription identifier. |
| customer_id | String | Foreign key to users.csv. |
| plan | String | Subscription plan name. |
| start_date | Date | Start date of the subscription. |
| end_date | Date | End date of the subscription (nullable if active). |
| status | String | Status of subscription (Active, Churned). |
| price | Float | Monthly cost of the plan. |
| billing_period | String | Billing frequency (Monthly/Annual). |

## revenue.csv
| Column | Type | Description |
|---|---|---|
| invoice_id | String | Unique invoice identifier. |
| customer_id | String | Foreign key to users.csv. |
| amount | Float | Billed amount. |
| revenue_date | Date | Date of revenue recognition. |
| revenue_type | String | Category (new, recurring, expansion, churn, refund). |

## support_tickets.csv
| Column | Type | Description |
|---|---|---|
| ticket_id | String | Unique ticket identifier. |
| customer_id | String | Foreign key to users.csv. |
| created_at | Datetime | Ticket creation time. |
| resolved_at | Datetime | Ticket resolution time. |
| issue_category | String | Category of the issue (Technical, Billing, etc.). |
| priority | String | Priority level (High, Medium, Low). |
