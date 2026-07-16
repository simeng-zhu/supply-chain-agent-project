"""
LLM Status Update Generator
----------------------------
Takes the flagged low-stock items and calls the Claude API to draft a
short, professional status update for each one -- the kind of message
a supply chain rep could send directly to a business stakeholder.

Setup:
    pip install anthropic pandas
    export ANTHROPIC_API_KEY="your-key-here"

Run:
    python llm_status_update.py
"""

import os
import pandas as pd
from anthropic import Anthropic

INPUT_FILE = "flagged_items.csv"
OUTPUT_FILE = "status_updates.csv"
MODEL = "claude-sonnet-4-6"

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def build_prompt(row: pd.Series) -> str:
    return (
        "You are a supply chain analyst drafting a short internal status "
        "update for a business stakeholder (not a technical audience). "
        "Write 2-3 professional sentences covering: what the item is, "
        "why it needs attention, and what's being done about it. "
        "Do not use bullet points or headers, just plain prose.\n\n"
        f"Product: {row['product_name']} (SKU {row['sku']})\n"
        f"Current stock: {row['current_stock']}\n"
        f"Reorder threshold: {row['reorder_threshold']}\n"
        f"Suggested reorder quantity: {row['suggested_reorder_qty']}\n"
        f"Supplier: {row['supplier']}\n"
        f"Supplier lead time: {row['lead_time_days']} days\n"
    )


def generate_update(row: pd.Series) -> str:
    prompt = build_prompt(row)
    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def main():
    flagged = pd.read_csv(INPUT_FILE)

    updates = []
    for _, row in flagged.iterrows():
        print(f"Drafting update for {row['product_name']}...")
        updates.append(generate_update(row))

    flagged["stakeholder_update"] = updates
    flagged.to_csv(OUTPUT_FILE, index=False)

    print(f"\nDone. Saved {len(flagged)} status updates to {OUTPUT_FILE}\n")
    for _, row in flagged.iterrows():
        print(f"--- {row['product_name']} ---")
        print(row["stakeholder_update"])
        print()


if __name__ == "__main__":
    main()