# ETL Test Automation – Interview Portfolio Upgrade

This folder contains supplementary, independently written examples for a fund-data ETL validation portfolio.

## What is included

- `aum_validation.py` – compares expected and actual AUM snapshots for daily, monthly, yearly and year-to-date (YTD) periods.
- `sample_expected_aum.csv` and `sample_actual_aum.csv` – synthetic demonstration data only.
- `requirements.txt` – Python dependency.
- `.gitignore` – excludes local environments, caches and generated reports.

## Pipeline context

`Source / Landing → Data Mart → Final Reporting`

The existing repository contains separate examples for record counts, nulls, duplicates, schema checks and source-to-target reconciliation. This add-on demonstrates period-based AUM reconciliation.

## AUM period logic used in this example

AUM is treated as a point-in-time balance, not a flow to be summed across dates. For each fund and period, the script selects the latest available business date in that period and compares its AUM between the expected and actual datasets.

- Daily: latest available record for each fund and business date.
- Monthly: latest available record for each fund within each calendar month.
- Yearly: latest available record for each fund within each calendar year.
- YTD: latest available record for each fund from the start of the year through the maximum date in the input data.

**Confirm these definitions with the business requirements / BRD before using this logic in a real project.** Some reporting specifications define period-end dates, prior-business-day handling, restatements, currencies, or YTD metrics differently.

## Input format

Both CSV files must contain:

- `fund_id`
- `business_date` (YYYY-MM-DD or another pandas-readable date)
- `aum` (numeric)

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python aum_validation.py \
  --expected sample_expected_aum.csv \
  --actual sample_actual_aum.csv \
  --tolerance 0.01
```

The script prints PASS/FAIL checks and writes `aum_validation_results.csv` in the current directory.

## Interpreting results

- `PASS`: expected and actual AUM are within the configured absolute tolerance.
- `FAIL`: a key is missing on one side, or the AUM difference exceeds tolerance.
- The script does not silently delete duplicates. Investigate duplicate fund/date keys according to the business rule.

## Important

All included CSV data is synthetic. Do not upload employer-owned code, confidential data, production extracts, credentials, connection strings, or internal documentation to a public repository. Only publish code and sample data you are authorized to share.
