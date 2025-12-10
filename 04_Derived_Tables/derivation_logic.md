# Derivation Logic

## 1. User Master (`user_master.csv`)
- **Source**: `users_cleaned` + Aggregates from subs/events.
- **Columns**: `user_id`, `signup_date`, `current_plan` (latest sub status), `lifetime_days` (signup to today/churn).
- **Logic**: Join users with latest subscription status. Determine `first_activation` as date of first key event.

## 2. Monthly Revenue (`monthly_revenue.csv`)
- **Granularity**: Monthly (Calendar Month).
- **MRR Calculation**: Sum of `amount` for all subscriptions active on the last day of the month.
- **Components**:
  - `New MRR`: MRR from new subs starting in month.
  - `Expansion`: Increase in MRR from finding upgrade events.
  - `Churned MRR`: MRR lost from subs ending in month.

## 3. Funnel (`monthly_funnel.csv`)
- **Stages**:
  - Signups (count distinct users by signup month)
  - Activations (users having >3 events in first week)
  - Trials (users taking trial plan)
  - Paid (users with >0 payment record)

## 4. Cohort Retention (`cohort_retention.csv`)
- **Cohort**: Month of `signup_date`.
- **Retention**: Count of users from cohort active (valid subscription) in Month N.
- **Metric**: `retention_rate = active_users_N / cohort_size`.

## 5. Churn Flags (`churn_flags.csv`)
- **Flag**: 1 if user has no active subscription and last end_date < Current Date - 30 days.
- **Reason**: `Explicit Cancellation` or `Non-Renewal`.
