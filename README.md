# E-commerce Revenue & Customer Intelligence

Analyze online retail transactions to understand sales seasonality, returns, customer cohorts, and product/country performance.

## Questions

- How does line sales revenue change over time?
- Which customers and markets contribute most to sales?
- How often do customers return after a first purchase?
- How sensitive are product rankings to returns, service codes, and unusually large orders?

## Findings

The current analysis and business hypotheses are summarized in [`reports/executive_summary.md`](reports/executive_summary.md). Detailed cleaning decisions and caveats are in [`reports/validated_data_review.md`](reports/validated_data_review.md). Results are descriptive, and revenue figures are line-level estimates rather than profit or accounting revenue.

## Data

This project uses [Online Retail II from the UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/502/online_retail%2Bii), by Daqing Chen, licensed under CC BY 4.0. The original workbook covers Dec 2009–Dec 2011. Download `online_retail_II.xlsx` from the official UCI page and place it in `data/`. Raw data are excluded from Git.

## Run the analysis

On Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/analyze_retail.py
```

The script writes CSV tables and charts to `reports/`. The exploratory notebook is in `notebooks/01_initial_exploration.ipynb`.

## Repository structure

- `data/` — local source workbook (not committed) and download notes
- `notebooks/` — exploratory notebook
- `src/` — reproducible analysis script
- `reports/` — summary, metrics, CSV outputs, and charts

## License and attribution

Dataset: Chen, D. (2012). *Online Retail II*. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D. CC BY 4.0.
