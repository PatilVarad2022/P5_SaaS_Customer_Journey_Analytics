#!/bin/bash
echo "1. Validating Data..."
python scripts/run_inspect.py

echo "2. Computing Metrics..."
python scripts/compute_metrics.py

echo "3. Exporting Tableau Extracts..."
python scripts/export_tableau_extracts.py

echo "Pipeline Complete. Check /outputs/ for results."
