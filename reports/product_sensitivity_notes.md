# Product ranking sensitivity

The analysis reports four transparent inclusion scenarios because this dataset has service lines and one unusually large item order. The service description filter is a heuristic, so the main results retain all positive lines.

| Scenario | Positive line sales (GBP) | Top item | Top item sales (GBP) | Top 10 items' share |
|---|---:|---|---:|---:|
| All positive lines | 20,534,115 | Manual | 339,988 | 10.11% |
| Exclude service-like descriptions | 19,536,348 | REGENCY CAKESTAND 3 TIER | 331,084 | 7.85% |
| Exclude StockCode 23843 outlier item | 20,365,646 | Manual | 339,988 | 9.76% |
| Exclude service-like and StockCode 23843 | 19,367,878 | REGENCY CAKESTAND 3 TIER | 331,084 | 7.40% |

StockCode 23843 contributed GBP 168,470 in one unusually large invoice. Removing it changes the sales total by less than 1%, while excluding descriptions matching the service-line heuristic changes the top-ranked item. Review this filter before using the ranking as a merchandise-only result. The output table is [`product_sensitivity.csv`](product_sensitivity.csv).
