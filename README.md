# Supply Chain Reorder & Stakeholder Update Assistant

A tool that reads inventory data, flags items that need reordering,
and (eventually) drafts stakeholder-facing status updates using
Claude. Built as a hands-on exercise in directing an AI coding agent
(Claude Code) and integrating an LLM into a real workflow.

## What it does so far

**`reorder_check.py`** reads `inventory.csv` (mock beverage supply
chain data: SKU, stock level, reorder threshold, lead time, supplier)
and flags every item at or below its reorder threshold. For each
flagged item, it calculates a suggested reorder quantity and saves
the result to `flagged_items.csv`.

Next step: use the flagged items to draft stakeholder-facing status
updates via the Claude API.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install anthropic pandas openpyxl
export ANTHROPIC_API_KEY="your-key-here"
```

## Run

```bash
python reorder_check.py
```

## Files

| File | Purpose |
|---|---|
| `inventory.csv` | Mock beverage supply chain inventory data |
| `reorder_check.py` | Flags low-stock items, calculates reorder quantities |
| `flagged_items.csv` | Output of the reorder check |