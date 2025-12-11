# Changelog

## [1.0.0] - 2024-03-15
- Initial release of SaaS Customer Journey Analytics pipeline.
- Added data generation, cleaning, and metric computation scripts.
- Included Excel LTV Simulator v1.1.
- Tableau extracts generation enabled.

### Limitations
- Cohort retention matrix is currently a sample placeholder in `generate_sample_outputs.py`. Full logic requires `compute_metrics.py` expansion.
- "Activation" is defined as `campaign_create`.

### Next Steps
- Integrate SQL database export.
- Add specific churn prediction model.
