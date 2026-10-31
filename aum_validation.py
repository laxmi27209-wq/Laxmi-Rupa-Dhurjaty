"""Compare expected and actual fund AUM snapshots across reporting periods.

AUM is treated as a point-in-time balance. The latest available record in each
fund/period is selected; values are not summed across dates.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = {"fund_id", "business_date", "aum"}


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"{path}: missing required columns: {sorted(missing)}")

    df = df.copy()
    df["business_date"] = pd.to_datetime(df["business_date"], errors="coerce")
    df["aum"] = pd.to_numeric(df["aum"], errors="coerce")

    if df["business_date"].isna().any():
        raise ValueError(f"{path}: business_date contains invalid or blank values")
    if df["aum"].isna().any():
        raise ValueError(f"{path}: aum contains non-numeric or blank values")
    if df["fund_id"].isna().any():
        raise ValueError(f"{path}: fund_id contains blank values")

    duplicate_keys = df.duplicated(["fund_id", "business_date"], keep=False)
    if duplicate_keys.any():
        duplicates = df.loc[duplicate_keys, ["fund_id", "business_date"]]
        raise ValueError(
            f"{path}: duplicate fund_id/business_date keys found:\n"
            f"{duplicates.to_string(index=False)}"
        )
    return df


def build_period_snapshots(df: pd.DataFrame) -> pd.DataFrame:
    """Create daily, monthly, yearly and YTD latest-date snapshots."""
    frames = []

    # Daily: one row per fund and business date.
    daily = df[["fund_id", "business_date", "aum"]].copy()
    daily["period_type"] = "daily"
    daily["period"] = daily["business_date"].dt.strftime("%Y-%m-%d")
    frames.append(daily)

    # Monthly: latest available date within each fund/calendar month.
    monthly = df.copy()
    monthly["period"] = monthly["business_date"].dt.to_period("M").astype(str)
    monthly = (
        monthly.sort_values("business_date")
        .groupby(["fund_id", "period"], as_index=False)
        .tail(1)[["fund_id", "business_date", "aum", "period"]]
    )
    monthly["period_type"] = "monthly"
    frames.append(monthly)

    # Yearly: latest available date within each fund/calendar year.
    yearly = df.copy()
    yearly["period"] = yearly["business_date"].dt.year.astype(str)
    yearly = (
        yearly.sort_values("business_date")
        .groupby(["fund_id", "period"], as_index=False)
        .tail(1)[["fund_id", "business_date", "aum", "period"]]
    )
    yearly["period_type"] = "yearly"
    frames.append(yearly)

    # YTD: latest available date from the start of each year to data's max date.
    ytd = df.copy()
    ytd["year"] = ytd["business_date"].dt.year
    ytd = (
        ytd.sort_values("business_date")
        .groupby(["fund_id", "year"], as_index=False)
        .tail(1)[["fund_id", "business_date", "aum", "year"]]
    )
    ytd["period"] = ytd["year"].astype(str) + "-YTD"
    ytd["period_type"] = "YTD"
    ytd = ytd.drop(columns=["year"])
    frames.append(ytd)

    return pd.concat(frames, ignore_index=True)


def reconcile(expected: pd.DataFrame, actual: pd.DataFrame, tolerance: float) -> pd.DataFrame:
    exp = build_period_snapshots(expected).rename(
        columns={"business_date": "expected_date", "aum": "expected_aum"}
    )
    act = build_period_snapshots(actual).rename(
        columns={"business_date": "actual_date", "aum": "actual_aum"}
    )

    keys = ["fund_id", "period_type", "period"]
    result = exp.merge(act, on=keys, how="outer", indicator=True)
    result["difference"] = result["actual_aum"] - result["expected_aum"]

    def status(row):
        if row["_merge"] == "left_only":
            return "FAIL - missing in actual"
        if row["_merge"] == "right_only":
            return "FAIL - unexpected in actual"
        if abs(row["difference"]) <= tolerance:
            return "PASS"
        return "FAIL - AUM mismatch"

    result["status"] = result.apply(status, axis=1)
    return result[
        keys + [
            "expected_date", "actual_date", "expected_aum", "actual_aum",
            "difference", "status"
        ]
    ].sort_values(keys)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected", required=True, help="Expected/source AUM CSV")
    parser.add_argument("--actual", required=True, help="Actual/final AUM CSV")
    parser.add_argument("--tolerance", type=float, default=0.01,
                        help="Allowed absolute AUM difference (default: 0.01)")
    parser.add_argument("--output", default="aum_validation_results.csv",
                        help="Output CSV path")
    args = parser.parse_args()

    if args.tolerance < 0:
        parser.error("--tolerance must be zero or greater")

    expected = load_data(args.expected)
    actual = load_data(args.actual)
    results = reconcile(expected, actual, args.tolerance)
    results.to_csv(args.output, index=False)

    print("\nAUM validation results")
    print(results.to_string(index=False))
    passed = results["status"].eq("PASS").sum()
    failed = len(results) - passed
    print(f"\nTotal checks: {len(results)} | PASS: {passed} | FAIL: {failed}")
    print(f"Detailed results saved to: {Path(args.output).resolve()}")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
