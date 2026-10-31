from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "test_data/source.csv"
TARGET = ROOT / "test_data/target.csv"
BUSINESS_KEY = ["fund_id", "business_date"]
AUM_TOLERANCE = 0.01
REMOVE_ID_PREFIX = ""  # Example: "FND-" only if required by mapping rules.

def normalize_fund_id(value):
    if pd.isna(value):
        return pd.NA
    value = str(value).strip()
    return value[len(REMOVE_ID_PREFIX):] if REMOVE_ID_PREFIX and value.startswith(REMOVE_ID_PREFIX) else value

def validate_source_to_target(source_file=SOURCE, target_file=TARGET):
    source = pd.read_csv(source_file, dtype={"fund_id": "string"})
    target = pd.read_csv(target_file, dtype={"fund_id": "string"})
    required = BUSINESS_KEY + ["aum"]

    for label, df in [("source", source), ("target", target)]:
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"{label} missing columns: {missing}")

    for df in (source, target):
        df["fund_id"] = df["fund_id"].map(normalize_fund_id)
        df["business_date"] = pd.to_datetime(df["business_date"], errors="coerce")
        df["aum"] = pd.to_numeric(df["aum"], errors="coerce")

    for label, df in [("source", source), ("target", target)]:
        if df.duplicated(BUSINESS_KEY).any():
            raise ValueError(f"{label} contains repeated business keys; apply correction/version rules first.")

    result = source[required].merge(
        target[required], on=BUSINESS_KEY, how="outer",
        suffixes=("_source", "_target"), indicator=True
    )
    missing_target = result[result["_merge"] == "left_only"]
    extra_target = result[result["_merge"] == "right_only"]
    matched = result[result["_merge"] == "both"].copy()
    matched["aum_difference"] = (matched["aum_source"] - matched["aum_target"]).abs()
    mismatches = matched[
        matched["aum_difference"].isna() |
        (matched["aum_difference"] > AUM_TOLERANCE)
    ]

    print("Source records:", len(source))
    print("Target records:", len(target))
    print("Missing from target:", len(missing_target))
    print("Unexpected in target:", len(extra_target))
    print("AUM mismatches:", len(mismatches))
    if not missing_target.empty:
        print("\nMissing records:\n", missing_target[BUSINESS_KEY])
    if not extra_target.empty:
        print("\nUnexpected records:\n", extra_target[BUSINESS_KEY])
    if not mismatches.empty:
        print("\nAUM differences:\n",
              mismatches[BUSINESS_KEY + ["aum_source", "aum_target", "aum_difference"]])

    passed = missing_target.empty and extra_target.empty and mismatches.empty
    print("PASS: Source-to-target reconciliation" if passed else "FAIL: Discrepancies detected")
    return passed

if __name__ == "__main__":
    validate_source_to_target()
