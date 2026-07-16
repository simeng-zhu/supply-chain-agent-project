# Supply Chain Reorder & Stakeholder Update Assistant

A tool that reads inventory data, flags items that need reordering,
and uses Claude to draft stakeholder-facing status updates for each
one -- built as a hands-on exercise in directing an AI coding agent
(Claude Code) and integrating an LLM into a real workflow.

## What it does

1. **`reorder_check.py`** reads `inventory.csv` (mock beverage supply
   chain data: SKU, stock level, reorder threshold, lead time,
   supplier) and flags every item at or below its reorder threshold.
   For each flagged item, it calculates a suggested reorder quantity
   and saves the result to `flagged_items.csv`.

2. **`llm_status_update.py`** takes those flagged items and calls the
   Claude API to draft a short, professional status update for each
   one -- the kind of message a supply chain rep could send directly
   to a business stakeholder.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install anthropic pandas
export ANTHROPIC_API_KEY="your-key-here"
```

## Run

```bash
python reorder_check.py
python llm_status_update.py
```

## Files

| File | Purpose |
|---|---|
| `inventory.csv` | Mock beverage supply chain inventory data |
| `reorder_check.py` | Flags low-stock items, calculates reorder quantities |
| `flagged_items.csv` | Output of the reorder check |
| `llm_status_update.py` | Drafts stakeholder status updates via Claude API |
| `status_updates.csv` | Output: stakeholder update per flagged item |