# Fund Data Validation Scripts

Standalone Python/Pandas checks for a fund AUM ETL pipeline.

## Scripts
- `record_count_check.py`: overall and batch-wise counts.
- `null_check.py`: NULL and blank values in mandatory fields.
- `duplicate_check.py`: exact duplicates and repeated `(fund_id, business_date)` keys.
- `schema_validation.py`: required columns and value types.
- `source_to_target_validation.py`: missing/extra business keys and AUM reconciliation.

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run separately
```bash
python record_count_check.py
python null_check.py
python duplicate_check.py
python schema_validation.py
python source_to_target_validation.py
```

## Assumptions to confirm
- Business key is `(fund_id, business_date)`.
- AUM tolerance is `0.01`.
- ID prefix stripping is disabled unless the mapping specification requires it.
- Repeated business keys are flagged for investigation, not automatically deleted; they may represent valid corrections.
- Replace sample files with approved test extracts. Never commit confidential production data or credentials to GitHub.
