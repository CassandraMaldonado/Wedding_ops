# WeddingOps

**A wedding planning command center for my budget, vendors, guests and decisions.**

I started building WeddingOps while planning my own wedding. I kept thinking about how many moving pieces there are at once: tracking what we have spent, comparing vendors, remembering payment deadlines and figuring out how a guest list change affects the rest of the budget. I wanted one place that makes those decisions a little easier to see.

It also includes a planning helper that uses the information already in the app. It can point out upcoming payments, budget pressure, missing vendor contracts and the cost impact of guest-list changes without pretending to know more than the data shows


## What it helps with

 Compare the planned budget with actual spending and committed vendor costs.
- Keep vendor quotes, deposits, contracts, contact details and payment dates in one place.
- Flag upcoming payments and vendors with missing contracts.
- Estimate attendance from RSVP patterns and show the expected range.
- - Model the cost effect of changing the guest count.
- Suggest a seating layout while respecting table size, preferences and conflict constraints.
- Ask practical questions through the planning assistant like: “What is due this month?” or “Can we add 15 guests?”

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
| `wedding_ops/data.py` | Creates a realistic sample wedding with vendors, expenses, guests and seating constraints. |
| `wedding_ops/planner.py` | Calculates budget health, attendance scenarios, vendor scores and seating suggestions. |
| `wedding_ops/assistant.py` | Provides grounded answers using the wedding data in the app. |
| `streamlit_app.py` | The planning dashboard. |
| `tests/test_planner.py` | Checks the budgeting, guest list, seating and assistant logic. |


## Google sign-in and PostgreSQL setup

Each Google account receives one private wedding plan, initially empty. Existing JSON profiles are not automatically imported; retain a backup before switching.

Create the following table in your PostgreSQL database (the application database user needs SELECT, INSERT and UPDATE access):

```sql
CREATE TABLE wedding_accounts (
    google_subject TEXT PRIMARY KEY,
    payload JSONB NOT NULL
);
```

Configure a Google OAuth web application as described in [Streamlit's Google sign-in guide](https://docs.streamlit.io/develop/tutorials/authentication/google). Add the deployed app URL followed by `/oauth2callback` as an authorized redirect URI. In Streamlit Community Cloud app settings, add the following secrets, replacing the placeholders. Never commit real credentials to GitHub.

```toml
[auth]
redirect_uri = "https://YOUR-APP.streamlit.app/oauth2callback"
cookie_secret = "a-long-random-secret"
client_id = "your-google-client-id"
client_secret = "your-google-client-secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

[database]
url = "postgresql://USER:PASSWORD@HOST:5432/DATABASE?sslmode=require"
```

For local use, put these settings in `.streamlit/secrets.toml` and use the matching localhost redirect URI. Google OAuth must be published or have the intended users listed as test users. Database backups and security remain the responsibility of the database administrator.
