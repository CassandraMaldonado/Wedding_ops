# WeddingOps

**A wedding planning command center for my budget, vendors, guests and decisions.**

I started building WeddingOps while planning my own wedding. I kept thinking about how many moving pieces there are at once: tracking what we have spent, comparing vendors, remembering payment deadlines and figuring out how a guest list change affects the rest of the budget. I wanted one place that makes those decisions a little easier to see.

It also includes a planning helper that uses the information already in the app. It can point out upcoming payments, budget pressure, missing vendor contracts and the cost impact of guest-list changes without pretending to know more than the data shows


## What it helps with

 Compare the planned budget with actual spending and committed vendor costs.
- Keep vendor quotes, deposits, contracts, contact details and payment dates in one place.
- Flag upcoming payments and vendors with missing contracts.
- Estimate attendance from RSVP patterns and show the expected range.

## Run it locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Repository map

| Location | What I use it for |
|---|---|
| `src/data.py` | Creates a realistic sample wedding with vendors, expenses, guests and seating constraints. |
| `src/planner.py` | Calculates budget health, attendance scenarios, vendor scores and seating suggestions. |
| `src/assistant.py` | Provides grounded answers using the wedding data in the app. |
| `streamlit_app.py` | The planning dashboard. |
| `tests/test_planner.py` | Checks the budgeting, guest list, seating and assistant logic. |
