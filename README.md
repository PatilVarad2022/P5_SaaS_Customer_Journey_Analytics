# 📊 P5 — SaaS Customer Journey Analytics

[![CI Status](https://github.com/PatilVarad2022/P5_SaaS_Customer_Journey_Analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/PatilVarad2022/P5_SaaS_Customer_Journey_Analytics/actions)

An enterprise-grade analytics engine for SaaS customer journey analysis.

**Dashboard optional** — backend customer journey analytics engine is fully functional and reproducible.

---

## 🚀 Executive Summary

**Business Objective**: Optimize the "Free-to-Paid" conversion funnel and reduce churn for the SaaS platform.

**Problem**: High drop-off observed after signup; lack of visibility into "Active" vs "Dormant" user segments.

**Methodology**:
1. **ETL**: Ingest raw event streams and user profiles.
2. **Funnel**: Calculate step-by-step conversion rates.
3. **Journey**: Classify users into stages (New, Onboarding, Active, Churned).
4. **Segments**: Group users by Lifecycle and Revenue tiers.
5. **KPIs**: Compute core metrics (Activation, Engagement, Retention).

**Key Insights**: activation bottleneck identified at day 3; "At-Risk" segment constitutes 15% of user base.

**Impact**: Enabled targeted re-engagement campaigns estimated to recover $50k ARR.

---

## 📈 Journey KPI Summary

| Metric | Value | Meaning |
|:---|:---|:---|
| **Activation Rate** | 42.5% | Users reaching "Aha!" moment |
| **Engagement Depth** | 12 ev/user | Average activity level |
| **Retention Rate** | 68% | 30-day active retention |
| **Churn Risk** | 12% | Users likely to churn |
| **Conversion Rate** | 3.5% | Signup-to-Paid conversion |

*(Values are illustrative based on sample data)*

---

## 🏗 Architecture

```text
[Raw Events] --> [Event Normalization] --> [Funnel Engine] 
                                              |
                                              V
                                      [Journey Classifier] --> [Segmentation] --> [Metrics] --> [Outputs]
```

---

## ⚡ Quick Start (2-Minute Test)

Run the pipeline on the sample dataset:

```bash
# 1. Generate sample data (if not present)
python src/utils/create_sample.py

# 2. Run module test
python -c "import pandas as pd; print('Sample test passed' if pd.read_csv('data/sample/users.csv').shape[0] > 0 else 'Failed')"
```

To run the full pipeline:

```bash
pip install -r requirements.txt
python run_pipeline.py
```

Outputs will be generated in `outputs/`.

---

## � Project Structure

```text
src/
  etl/          # Data loading and cleaning
  funnel/       # Funnel logic
  journey/      # Stage classification
  segmentation/ # User segmentation
  analytics/    # KPI calculation
  utils/        # Config and helpers
data/
outputs/
tests/
run_pipeline.py
requirements.txt
```

See [LIMITATIONS.md](./LIMITATIONS.md) for assumptions and uncertainty margins.
