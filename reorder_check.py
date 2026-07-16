"""
Reorder Flagging Logic
-----------------------
Reads inventory data and flags items that are at or below their
reorder threshold, calculating a suggested reorder quantity for each.

Suggested reorder quantity formula:
    reorder_qty = (reorder_threshold * 1.5) - current_stock

This targets restocking to 150% of the threshold, rounded up to the
nearest whole unit, and never suggests reordering a negative amount.
"""

import pandas as pd
import math

INPUT_FILE = "inventory.csv"
OUTPUT_FILE = "flagged_items.csv"


def load_inventory(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def flag_low_stock(df: pd.DataFrame) -> pd.DataFrame:
    flagged = df[df["current_stock"] <= df["reorder_threshold"]].copy()

    flagged["suggested_reorder_qty"] = (
        (flagged["reorder_threshold"] * 1.5) - flagged["current_stock"]
    ).apply(lambda qty: max(math.ceil(qty), 0))

    flagged["stock_gap"] = flagged["reorder_threshold"] - flagged["current_stock"]

    flagged = flagged.sort_values("stock_gap", ascending=False).drop(columns="stock_gap")

    return flagged


def print_summary(flagged: pd.DataFrame) -> None:
    if flagged.empty:
        print("No items are at or below their reorder threshold.")
        return

    print(f"{len(flagged)} item(s) flagged for reorder:\n")
    for _, row in flagged.iterrows():
        print(
            f"- {row['product_name']} ({row['sku']}): "
            f"{row['current_stock']} in stock, threshold {row['reorder_threshold']}, "
            f"lead time {row['lead_time_days']} days, supplier {row['supplier']} "
            f"-> suggested reorder qty: {row['suggested_reorder_qty']}"
        )


def main():
    df = load_inventory(INPUT_FILE)
    flagged = flag_low_stock(df)
    print_summary(flagged)
    flagged.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved flagged items to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
