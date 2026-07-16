"""
LLM Status Update Generator (Agentic: Draft -> Self-Critique -> Revise)
------------------------------------------------------------------------
Takes the flagged low-stock items and drafts a short, professional
status update for each one -- the kind of message a supply chain rep
could send directly to a business stakeholder.

Instead of a single one-shot call, this runs a lightweight two-step
agentic loop for each item:
    1. DRAFT    - generate an initial status update
    2. CRITIQUE - ask the model to evaluate its own draft against a
                  fixed rubric and flag anything missing or weak
    3. REVISE   - produce a final version that addresses the critique

This mirrors how the tool is actually meant to be used in practice:
not "accept whatever the model says first," but direct it, review its
own output, and push it to improve before treating anything as final.

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

RUBRIC = (
    "Rubric:\n"
    "1. Names the product and SKU.\n"
    "2. States current stock vs. reorder threshold clearly.\n"
    "3. Mentions the supplier and lead time explicitly.\n"
    "4. Tone matches urgency: short lead time or large stock gap = more "
    "urgent tone; long lead time or small gap = calmer tone.\n"
    "5. Ends with a clear next action (the purchase order / quantity).\n"
    "6. Written in plain prose for a non-technical business audience -- "
    "no bullet points, no jargon.\n"
)

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def call_claude(prompt: str, max_tokens: int = 300) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def build_draft_prompt(row: pd.Series) -> str:
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


def build_critique_prompt(draft: str) -> str:
    return (
        "Evaluate the following status update against this rubric. "
        "List only what is missing or weak, in 1-3 short bullet points. "
        "If it fully satisfies the rubric, respond with exactly: "
        "'No issues found.'\n\n"
        f"{RUBRIC}\n"
        f"Status update to evaluate:\n\"{draft}\""
    )


def build_revise_prompt(draft: str, critique: str) -> str:
    return (
        "Revise the status update below to address the feedback. "
        "Keep it to 2-3 sentences, plain prose, no bullet points. "
        "Return only the revised update, nothing else.\n\n"
        f"Original update:\n\"{draft}\"\n\n"
        f"Feedback to address:\n{critique}"
    )


def generate_update(row: pd.Series) -> dict:
    draft = call_claude(build_draft_prompt(row))
    critique = call_claude(build_critique_prompt(draft), max_tokens=150)

    if critique.strip().lower().startswith("no issues"):
        final = draft
    else:
        final = call_claude(build_revise_prompt(draft, critique))

    return {"draft": draft, "critique": critique, "final": final}


def main():
    flagged = pd.read_csv(INPUT_FILE)

    drafts, critiques, finals = [], [], []
    for _, row in flagged.iterrows():
        print(f"Processing {row['product_name']}...")
        result = generate_update(row)
        drafts.append(result["draft"])
        critiques.append(result["critique"])
        finals.append(result["final"])

    flagged["draft_v1"] = drafts
    flagged["self_critique"] = critiques
    flagged["stakeholder_update_final"] = finals
    flagged.to_csv(OUTPUT_FILE, index=False)

    print(f"\nDone. Saved {len(flagged)} status updates to {OUTPUT_FILE}\n")
    for _, row in flagged.iterrows():
        print(f"--- {row['product_name']} ---")
        print(row["stakeholder_update_final"])
        print()


if __name__ == "__main__":
    main()