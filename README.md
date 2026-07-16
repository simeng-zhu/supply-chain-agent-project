# Supply Chain Reorder & Stakeholder Update Assistant

A small tool that reads inventory data, flags items that need
reordering, and uses Claude to draft stakeholder-facing status updates
for each one -- built as a hands-on exercise in directing an AI coding
agent (Claude Code) and integrating an LLM into a real workflow.

## What it does

1. **`reorder_check.py`** reads `inventory.csv` (mock beverage supply
   chain data: SKU, stock level, reorder threshold, lead time,
   supplier) and flags every item at or below its reorder threshold.
   For each flagged item, it calculates a suggested reorder quantity
   and saves the result to `flagged_items.csv`.

2. **`llm_status_update.py`** takes those flagged items and, for each
   one, runs a **draft -> self-critique -> revise** loop using the
   Claude API:
   - **Draft**: Claude writes an initial plain-language status update
     aimed at a non-technical business stakeholder.
   - **Critique**: Claude evaluates its own draft against a fixed
     rubric (does it name the product/SKU, state the stock gap,
     mention supplier and lead time, match tone to urgency, and end
     with a clear next action?) and flags anything missing or weak.
   - **Revise**: if the critique finds issues, Claude produces a
     final version that addresses them. If not, the original draft is
     kept as final.

   All three stages (draft, critique, final) are saved to
   `status_updates.csv` so the full reasoning trail is visible, not
   just the end result.

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

## The iteration story

The first version of this project called Claude once per item and
took the output as final -- no review step. The drafts were already
decent, but reading through them critically surfaced a real, specific
gap:

> **Before (single-shot draft):**
> *"Craft Lager 24-pack Cans (SKU BW-1002) are currently below our
> reorder threshold, with only 180 units on hand against a trigger
> point of 250, meaning we are at risk of a stockout within the coming
> days if demand continues at its normal pace. To address this, a
> purchase order for 195 units is being initiated with our supplier,
> Northwind Brewing Co., which will bring inventory back to a healthy
> level."*

This reads fine on its own -- but held up against a 7-day lead time
(one of the shortest in the dataset) next to a 28-day lead-time item
that got an almost identically urgent tone, the model wasn't actually
calibrating urgency to lead time. A wine SKU with a month-long
resupply window and a beer SKU with a one-week window came out
sounding equally alarmed, which isn't how a real supply chain analyst
would frame it.

That observation is what motivated the self-critique step, rather
than manually rewriting each draft by hand. Instead of fixing the tone
myself, the rubric explicitly instructs Claude to check whether *tone
matches urgency: short lead time or large stock gap = more urgent
tone; long lead time or small gap = calmer tone* -- turning a
one-off manual fix into a repeatable check applied automatically to
every item.

> **After (post-critique revision), same item:**
> *"Craft Lager 24-pack Cans (SKU BW-1002) have dropped to 180 units
> against a 250-unit reorder threshold. With Northwind Brewing Co.'s
> standard 7-day lead time, we've already initiated a purchase order
> for 195 units and expect replenishment within the week, so this is
> being tracked as routine rather than urgent."*

The revised version keeps the same facts (SKU, stock gap, supplier,
quantity) but recalibrates the tone to match the short lead time --
routine and on-track rather than alarmed -- which is the more accurate
read given a 7-day resupply window.

## Files

| File | Purpose |
|---|---|
| `inventory.csv` | Mock beverage supply chain inventory data |
| `reorder_check.py` | Flags low-stock items, calculates reorder quantities |
| `flagged_items.csv` | Output of the reorder check |
| `llm_status_update.py` | Draft -> critique -> revise loop via Claude API |
| `status_updates.csv` | Final output: draft, critique, and final update per item |

## Possible next steps

- Add a Streamlit front end so the CSV upload and results are
  browsable in a UI rather than the terminal.
- Extend the rubric to also check for consistent currency/units
  formatting across items.
- Batch the critique calls to reduce API round-trips.