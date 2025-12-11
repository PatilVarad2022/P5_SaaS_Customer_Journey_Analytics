# P5 — SaaS Customer Journey Analytics (Backend)

**Purpose.** Production-quality backend for a SaaS product-analytics project designed for Analyst CVs: funnel → cohorts → revenue (MRR/ARPU/LTV) → segmentation → scenario simulation (Excel).  
**Scope.** Backend only: data pipelines, KPI computation, Tableau-ready extracts, and an Excel LTV & scenario simulator. No frontend / no ML.

---

## Quick status
- Backend: ✅ Implemented  
- Excel simulator: ✅ `P5_LTV_Simulator.xlsx` (open to view inputs & results)  
- Tableau dashboard: 🔜 Planned (exports available in `/outputs/tableau_ready/`)  
- How a recruiter can verify (without running code): open `/outputs/` and `/docs/screenshots/`.

---

## Repo layout

```text
/
├─ data/
│  ├─ users.csv
│  ├─ events.csv
│  ├─ subscriptions.csv
│  ├─ revenue.csv
├─ scripts/
│  ├─ run_inspect.py
│  ├─ compute_metrics.py
│  ├─ export_tableau_extracts.py
├─ notebooks/
│  └─ pipeline_demo.py
├─ outputs/
│  ├─ kpi_summary.csv
│  ├─ cohort_retention_matrix.csv
│  └─ tableau_ready/
├─ docs/
│  ├─ screenshots/
│  ├─ data_dictionary.md
│  └─ metrics_definitions.md
├─ P5_LTV_Simulator.xlsx
├─ tests/
├─ requirements.txt
└─ README.md
```

---

## How to reproduce (one-liners)
```bash
# 1. prepare environment
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. run validation and produce outputs
python scripts/run_inspect.py     # validates schemas & dates -> writes /outputs/inspections/
python scripts/compute_metrics.py # writes /outputs/kpi_summary.csv, cohort_retention_matrix.csv, mrr_breakdown.csv
python scripts/export_tableau_extracts.py # writes /outputs/tableau_ready/*
```

---

## What to look at (recruiter checklist)

* `/outputs/kpi_summary.csv` — activation rate, funnel conversions, ARPU, LTV summary.
* `/outputs/cohort_retention_matrix.csv` — monthly cohort survival table.
* `/outputs/mrr_breakdown.csv` — new / expansion / churn MRR.
* `/P5_LTV_Simulator.xlsx` — open `Inputs` tab to see scenario variables; `Results` tab shows LTV / ARPU / MRR impact.
* `/docs/screenshots/` — screenshots of outputs and repository structure for quick review.

---

## Data & metrics (short)

See `docs/data_dictionary.md` for column-level definitions. See `docs/metrics_definitions.md` for explicit formulas (activation rate, funnel steps, monthly churn, MRR breakdown, ARPU, cohort LTV). Example formula (documented in `metrics_definitions.md`):

* **Activation rate** = (# customers with `event_name = "campaign_create"` within 14 days of `signup_date`) / (total signups)
* **Monthly churn rate** = (MRR lost from cancellations in month) / (MRR at start of month)
* **MRR** = sum of active monthly-recurring prices for active subscriptions (normalize annual to monthly)

---

## Tests & CI

Run the tests:

```bash
python tests/test_schema.py
python tests/test_keys_unique.py
```

(If CI is enabled, a GitHub Actions workflow will run `scripts/run_inspect.py` on PRs.)

---

## Notes for recruiters / reviewers

This repo intentionally ships a complete, runnable backend and an Excel simulator so recruiters can verify analytics outputs immediately. The Tableau dashboard is not included in this commit; Tableau-ready extracts are provided for rapid dashboard construction.

---

## Contact / Author

Varad Patil — Backend & Analytics lead
Github: `https://github.com/PatilVarad2022/P5_SaaS_Customer_Journey_Analytics`

---

## License

MIT
