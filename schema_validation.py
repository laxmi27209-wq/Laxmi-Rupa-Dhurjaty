from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "test_data/source.csv"
EXPECTED_SCHEMA = {
    "fund_id": "string",
    "business_date": "datetime",
    "aum": "numeric",
    "batch_id": "string"
}

def validate_schema(file_path=INPUT):
    df = pd.read_csv(file_path, dtype={"fund_id": "string", "batch_id": "string"})
    errors = []
    missing = [c for c in EXPECTED_SCHEMA if c not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")

    for col, expected in EXPECTED_SCHEMA.items():
        if col not in df.columns:
            continue
        if expected == "string":
            invalid = df[col].isna()
        elif expected == "datetime":
            invalid = pd.to_datetime(df[col], errors="coerce").isna()
        else:
            invalid = pd.to_numeric(df[col], errors="coerce").isna()
        if invalid.any():
            errors.append(f"{col}: {int(invalid.sum())} invalid {expected} value(s)")

    if errors:
        print("FAIL: Schema validation")
        for error in errors:
            print("-", error)
        return False
    print("PASS: Required columns and data types are valid")
    return True

if __name__ == "__main__":
    validate_schema()
