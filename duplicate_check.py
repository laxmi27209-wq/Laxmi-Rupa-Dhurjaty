from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "test_data/source.csv"
BUSINESS_KEY = ["fund_id", "business_date"]

def check_duplicates(file_path=INPUT):
    df = pd.read_csv(file_path)
    missing = [c for c in BUSINESS_KEY if c not in df.columns]
    if missing:
        print("FAIL: Missing business-key columns:", missing)
        return False

    exact = df.duplicated(keep=False)
    repeated_key = df.duplicated(subset=BUSINESS_KEY, keep=False)
    print("Rows involved in exact duplicates:", int(exact.sum()))
    print("Rows involved in repeated fund/date keys:", int(repeated_key.sum()))

    if exact.any():
        print("\nExact duplicate rows:\n", df[exact])
    if repeated_key.any():
        print("\nRepeated business keys need review:\n",
              df[repeated_key].sort_values(BUSINESS_KEY))
        print("Do not automatically delete these: they may be valid corrections.")
    else:
        print("PASS: No repeated business keys")
    return not repeated_key.any()

if __name__ == "__main__":
    check_duplicates()
