from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "test_data/source.csv"
MANDATORY_COLUMNS = ["fund_id", "business_date", "aum", "batch_id"]

def check_null_values(file_path=INPUT):
    df = pd.read_csv(file_path)
    missing_cols = [c for c in MANDATORY_COLUMNS if c not in df.columns]
    if missing_cols:
        print("FAIL: Missing mandatory columns:", missing_cols)
        return False
    df = df.replace(r"^\\s*$", pd.NA, regex=True)
    counts = df[MANDATORY_COLUMNS].isna().sum()
    print("NULL/blank counts:\n", counts)
    passed = counts.sum() == 0
    print("PASS: No NULLs" if passed else "FAIL: NULL/blank values found")
    return passed

if __name__ == "__main__":
    check_null_values()
