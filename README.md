# WeddingOps

**A wedding planning command center for my budget, vendors, guests and decisions.**

I built WeddingOps around the parts of wedding planning that can get messy quickly, like keeping track of what has been spent, comparing vendors, remembering payment deadlines and understanding how a guest count change affects the whole budget.

It includes a grounded planning assistant that only uses the structured wedding data in the app. Instead of giving generic advice, it can explain upcoming payments, budget pressure, missing vendor contracts and the cost impact of guest-list changes.

This hits personal to home since i'm planning my wedding.

## What it helps with

- Compare the planned budget with actual spending and committed vendor costs.
- Keep vendor quotes, deposits, contracts, contact details, and payment dates in one place.
- Flag upcoming payments and vendors with missing contracts.
- Estimate attendance from RSVP patterns and show the expected range.
- Model the cost effect of changing the guest count.
- Suggest a seating layout while respecting table size, preferences, and conflict constraints.
- Ask practical questions through the planning assistant, such as “What is due this month?” or “Can we add 15 guests?”

## Run it locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository and push this folder to it.
2. Go to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Select the repository, branch, and `streamlit_app.py` as the entry point.
4. Click **Deploy** to create a shareable URL.

## Repository map

| Location | What I use it for |
|---|---|
| `src/wedding_ops/data.py` | Creates a realistic sample wedding with vendors, expenses, guests, and seating constraints. |
| `src/wedding_ops/planner.py` | Calculates budget health, attendance scenarios, vendor scores, and seating suggestions. |
| `src/wedding_ops/assistant.py` | Provides grounded answers using the wedding data in the app. |
| `streamlit_app.py` | Contains the interactive planning dashboard. |
| `tests/` | Checks the budgeting, guest-list, seating, and assistant logic. |

The data is synthetic so the project can be shared safely. It is meant to demonstrate a practical planning workflow, not to replace contracts, financial advice, or the couple’s final decisions.

