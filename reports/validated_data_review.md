# Refreshed analysis: sales, customers, and data checks

## Cleaning rule

The workbook contains 1,067,371 combined rows. The sheets overlap. Instead of deleting every identical row, we retained the maximum multiplicity of each exact row found in either sheet, preserving repeat lines within a sheet. This removes 22,523 excess cross-sheet copies and leaves 1,044,848 rows. Row matching uses a 64-bit row hash; a collision is very unlikely but remains a technical limitation.

## Returns and cancellation flags

- `C`-prefixed invoice lines: 19,165.
- Negative-quantity lines: 22,557.
- Mismatched rows: 3,394.
- Positive line sales: GBP 20,534,115.49; negative-quantity line value: GBP 1,465,677.23; mechanical net: GBP 19,068,438.26.
- Mismatch table: 3,393 negative-quantity lines without `C` have zero line value, and 1 `C`-prefixed line with positive quantity has GBP 373.57 line value. Inspect the exceptional invoice before a final return rule.

## Customer and market findings

- Customers with IDs and positive purchases: 5,878.
- Median month-one cohort retention: 20.4% across 25 cohorts with an observed next month.
- Current RFM heuristic: Champions are 29.4% of identified customers and contribute 80.5% of identified-customer sales. Labels are descriptive heuristics, not validated customer value predictions.
- United Kingdom sales share: 85.1%.
- Top 1% / 5% / 10% of identified customers contribute 31.9% / 51.9% / 63.8% of identified-customer positive sales.

## Outlier review

Stock code 23843 (`PAPER CRAFT , LITTLE BIRDIE`) has 80,995 positive units across 1 invoices. The largest line-invoice group is 80,995 units / GBP 168,469.60. This may be wholesale demand; do not remove it without a documented reason. Product ranking also includes non-merchandise descriptions such as Manual and Postage.

## Outputs

- Sales and returns: `monthly_sales_returns.csv`, `monthly_sales_returns.png`
- Cohorts: `customer_cohort_retention.csv`, `customer_cohort_retention.png`
- RFM: `customer_rfm_segments.csv`, `rfm_segment_summary.csv`
- Country and products: `country_performance.csv`, `top_products.csv`
- Cancellation checks: `cancellation_flag_crosscheck.csv`, `cancellation_mismatch_summary.csv`

All findings are exploratory. Final recommendations should use explicit cancellation rules, a reviewed list of non-merchandise codes, and sensitivity results with and without unusually large orders.
