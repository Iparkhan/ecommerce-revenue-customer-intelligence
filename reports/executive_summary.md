# E-commerce Revenue & Customer Intelligence

## Executive summary

This project analyzes two years of transactions from a UK online retailer to understand sales seasonality, returns, customer concentration, and repeat purchasing. It uses Python and a public UCI dataset. The analysis is descriptive; it does not estimate profit, causal effects, or future customer value.

## Key findings

- Gross positive line sales are **GBP 20.53m**; negative-quantity line value is **GBP 1.47m**; mechanical net line sales are **GBP 19.07m**. These are line-level estimates, not accounting revenue.
- November was the highest gross-sales month in both full years observed: **GBP 1.47m in Nov 2010** and **GBP 1.51m in Nov 2011**. December 2011 is partial, ending on Dec 9.
- The United Kingdom accounts for **85.1%** of gross positive line sales.
- Among identified customers, the top 10% account for **63.8%** of positive line sales. An exploratory RFM rule places 29.4% in its highest segment, associated with 80.5% of identified-customer sales.
- Median next-month cohort retention is **20.4%** across 25 cohorts with a following month available.
- Cancellation invoice codes and negative quantities disagree in 3,394 rows. Most discordant negative-quantity lines have zero value; one C-coded positive-quantity line is worth GBP 373.57.
- A single invoice contains 80,995 units of one item, so product demand should be reviewed with and without unusually large orders.

## Recommended business actions to test

1. **Plan seasonal inventory and fulfillment:** review October–November capacity and stock planning, then compare more years or weeks before changing policy.
2. **Protect high-value customer relationships:** identify service needs among high-volume buyers and track concentration risk; the current segments are descriptive heuristics.
3. **Encourage a second purchase:** test a post-purchase follow-up for one-invoice customers, measuring repeat rate against a comparable group.
4. **Improve transaction data quality:** standardize cancellation/return codes and customer IDs so net sales and retention can be measured consistently.
5. **Separate merchandise from service codes and wholesale outliers:** report product performance with transparent inclusion rules.

## Method

- Combined the two workbook sheets while removing only excess exact copies across sheets; repeated identical rows within a sheet are retained.
- Separated positive sales from negative-quantity lines and cross-checked the invoice cancellation prefix.
- Aggregated monthly sales, country/product mix, customer cohorts, and recency-frequency-monetary (RFM) metrics.
- RFM cutoffs are dataset-relative quartiles and labels are not validated predictions.

## Limitations

- Data cover Dec 2009–Dec 2011 and may not represent current retail behavior.
- Missing customer IDs prevent customer-level analysis for some transactions.
- No cost, margin, marketing channel, inventory, or operational data are available.
- Returns, duplicate lines, special stock codes, and exceptional wholesale orders need business validation.

See [validated data review](validated_data_review.md) for detailed figures and [project README](../README.md) for setup and reproducibility.
