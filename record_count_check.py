from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "test_data/source.csv"
TARGET = ROOT / "test_data/target.csv"

def compare_record_counts(source_file=SOURCE, target_file=TARGET):
    source = pd.read_csv(source_file)
    target = pd.read_csv(target_file)
    print(f"Source count: {len(source)}")
    print(f"Target count: {len(target)}")
    passed = len(source) == len(target)
    print("PASS: Counts match" if passed else "FAIL: Count mismatch")

    if "batch_id" in source and "batch_id" in target:
        counts = pd.concat([
            source.groupby("batch_id").size().rename("source_count"),
            target.groupby("batch_id").size().rename("target_count")
        ], axis=1).fillna(0).astype(int)
        counts["status"] = counts.apply(
            lambda r: "PASS" if r.source_count == r.target_count else "FAIL", axis=1
        )
        print("\nBatch-wise counts:\n", counts)
    return passed

if __name__ == "__main__":
    compare_record_counts()
