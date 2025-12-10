# Data Generation

This folder contains the scripts and outputs for the synthetic SaaS dataset.

## Scripts
- `generate_synthetic_data.py`: Main Python script.

## Usage
Run the script to generate data. Outputs are saved to `outputs/`.

```bash
# Generate full dataset (10,000 users) -> Default
python generate_synthetic_data.py --size 10000

# Generate small dataset (1,000 users)
python generate_synthetic_data.py --size 1000
```

## Logic & Assumptions

### Users
- **Count**: 10,000 (default)
- **Seasonality**: Higher signups in Q1 and Q4.
- **Channels**: Mix of Organic, Paid Search, Social, etc.
- **B2B**: ~30% of users are associated with a company (shared `company_id`).

### Subscriptions
- **Trial**: All users start with a 14-day trial (or Free tier).
- **Conversion**: Logic based on channel (e.g., Paid Search converts better).
- **Plans**: Basic/Pro (Monthly/Annual).
- **Lifecycle**: Trial -> Active -> (Renewal/Churn).
- **Churn**: Randomly assigned (~15% churn rate after first period).

### Events
- **Volume**: ~250,000 events total (~6-50 per user).
- **Types**: 12 defined types including `login`, `dashboard_view`, `report_create`.
- **Timing**: Events only occur during valid subscription periods.

### Support
- **Ticket Volume**: ~10% of users submit tickets (higher for churned users).
- **NPS**: Correlated with Churn status (churned users give lower scores).

## Outputs
Files are saved in `outputs/` in both CSV and Parquet formats:
- `users.csv`
- `subscriptions.csv`
- `events.csv`
- `support_nps.csv`
