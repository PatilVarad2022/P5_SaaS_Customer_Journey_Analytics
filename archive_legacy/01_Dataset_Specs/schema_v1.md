# Dataset Specification v1

## Overview
This document defines the schema, constraints, and business rules for the SaaS Customer Journey Analytics dataset.
**Time Window**: 2024-01-01 to 2024-12-31 (12 Months)

## 1. users.csv
**Description**: Master table of registered users.
**Estimated Rows**: ~10,000
**Primary Key**: `user_id`

| Column Name | Type | Key | Nullable | Description / Rules | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `user_id` | String | PK | No | Unique identifier (UUID or similar format). | `usr_8x92nm2` |
| `company_id` | String | | No | Company identifier. Repeated for B2B users. | `cmp_9921` |
| `signup_date` | Date | | No | ISO 8601 Date (YYYY-MM-DD). Must be within time window or slightly before (for older cohorts). | `2024-03-15` |
| `country` | String | | No | User's country. Limit to 6 major markets: US, UK, DE, FR, ES, IN. | `US` |
| `acquisition_channel` | String | | No | Source of signup. 6 values: `Organic`, `Paid_Search`, `Referral`, `Social`, `Direct`, `Email`. | `Organic` |
| `initial_plan` | String | | No | Plan selected at signup: `Free`, `Trial_Basic`, `Trial_Pro`. | `Trial_Pro` |
| `job_role` | String | | Yes | User's role: `Admin`, `Member`, `Viewer`. | `Admin` |

**Constraints & Logic**:
- `company_id`: Reuse roughly 1 `company_id` for every ~3 users to simulate B2B teams.
- `signup_date`: Distributed with seasonality (higher in Q1/Q4).

---

## 2. events.csv
**Description**: Log of user actions on the platform.
**Estimated Rows**: ~250,000 (Avg 25 events/user)
**Primary Key**: `event_id`
**Foreign Key**: `user_id`

| Column Name | Type | Key | Nullable | Description / Rules | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `event_id` | String | PK | No | Unique ID. | `evt_1120a` |
| `user_id` | String | FK | No | Links to users.csv. | `usr_8x92nm2` |
| `event_timestamp` | Datetime | | No | ISO 8601 Timestamp (UTC). Must be >= `signup_date`. | `2024-03-15T14:30:00Z` |
| `event_type` | String | | No | Taxonomy (12 types): `login`, `dashboard_view`, `report_create`, `report_export`, `feature_x_use`, `settings_change`, `invite_user`, `page_view`, `campaign_create`, `data_import`, `api_call`, `logout`. | `report_create` |
| `session_id` | String | | No | Unique session ID grouping events. | `ses_001` |
| `device` | String | | Yes | `Desktop`, `Mobile`, `Tablet`. | `Desktop` |

**Constraints & Logic**:
- Minimum 1 event (`signup_complete` or `login`) on `signup_date`.
- `event_timestamp` must strictly follow chronological order per user.

---

## 3. subscriptions.csv
**Description**: History of subscription states (SCD Type 2 or Event Log style).
**Estimated Rows**: ~8,000
**Primary Key**: `subscription_id`
**Foreign Key**: `user_id`

| Column Name | Type | Key | Nullable | Description / Rules | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `subscription_id` | String | PK | No | Unique ID per ledger entry. | `sub_5511` |
| `user_id` | String | FK | No | Links to users.csv. | `usr_8x92nm2` |
| `plan_id` | String | | No | `Free`, `Basic_Monthly`, `Pro_Monthly`, `Basic_Annual`, `Pro_Annual`. | `Pro_Monthly` |
| `start_date` | Date | | No | Start of this subscription period. | `2024-03-15` |
| `end_date` | Date | | Yes | End of this subscription period. NULL if active. | `2024-04-15` |
| `amount` | Float | | No | Monthly Recurring Revenue (MRR) equivalent. | `49.00` |
| `status` | String | | No | `Active`, `Cancelled`, `Past_Due`, `Trial`. | `Active` |
| `transaction_type` | String | | No | `New_Business`, `Renewal`, `Expansion`, `Contraction`, `Churn`. | `New_Business` |

**Constraints & Logic**:
- Trial length: 14 days (Fixed rule).
- `amount`: Free=$0, Basic=$29, Pro=$99 (Annual 10% discount).
- Time alignment: `start_date` must match a specific lifecycle event (signup or renewal).

---

## 4. support_nps.csv
**Description**: Customer support tickets and NPS survey responses.
**Estimated Rows**: ~12,000
**Primary Key**: `ticket_id`
**Foreign Key**: `user_id`

| Column Name | Type | Key | Nullable | Description / Rules | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ticket_id` | String | PK | No | Unique Ticket ID. | `tkt_990` |
| `user_id` | String | FK | No | Links to users.csv. | `usr_8x92nm2` |
| `created_at` | Datetime | | No | Timestamp of ticket creation. | `2024-05-10T09:00:00Z` |
| `resolved_at` | Datetime | | Yes | Timestamp of resolution. NULL if open. | `2024-05-11T14:00:00Z` |
| `ticket_category` | String | | No | `Billing`, `Technical`, `Feature_Req`, `Access`. | `Technical` |
| `nps_score` | Integer | | Yes | 0-10 Score. NULL if no survey sent/answered. | `9` |
| `nps_comment` | String | | Yes | Optional text feedback. | `Great service!` |

**Constraints & Logic**:
- NPS correlation: Lower scores should correlate slightly with Churn events in `subscriptions.csv`.
- SLA Breach: If `resolved_at` - `created_at` > 48 hours, consider SLA breached.

## Business Rules Summary
1. **Trial**: All users start on a Trial (or Free tier). Paid plans start after 14 days if converted.
2. **Activation**: Defined as `dashboard_view` + `report_create` within first 7 days.
3. **Churn**: A subscription ending with no subsequent renewal/upgrade record.
4. **Data Consistency**: No orphan `user_id`s in child tables. No events before signup date.
