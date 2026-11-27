# Dashboard for WeddingOps.

from dataclasses import replace

import pandas as pd
import plotly.express as px
import streamlit as st

from wedding_ops.assistant import answer
from wedding_ops.data import (
    WeddingData,
    blank_wedding,
    load_account_wedding,
    save_account_wedding,
)
from wedding_ops.planner import (
    attendance_forecast,
    budget_summary,
    guest_count_scenario,
    seating_plan,
    upcoming_payments,
    vendor_scores,
)

st.set_page_config(
    page_title="WeddingOps",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(
    """<style>@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Playfair+Display:wght@500;600&family=Manrope:wght@400;500;600;700&display=swap');.stApp{background:#ffffff;color:#111111;font-family:Manrope,sans-serif}.block-container{max-width:1280px;padding-top:2rem}.stSidebar{background:#111111!important}.stSidebar *{color:#ffffff!important}.stSidebar input{color:#111111!important}h1,h2,h3{font-family:'Playfair Display',serif!important;letter-spacing:-.03em}.eyebrow{font:10px 'DM Mono';letter-spacing:.13em;color:#a7832d}.hero{background:#111111;color:#ffffff;padding:3.5rem;min-height:300px;background-image:radial-gradient(circle at 88% 15%,#c9a54b 0,transparent 25%),radial-gradient(circle at 70% 110%,#c9a54b55 0,transparent 30%)}.hero h1{font-size:4.5rem;line-height:.95;margin:.5rem 0 1.2rem}.hero p{max-width:650px;color:#e5d6a9;line-height:1.65}.pill{display:inline-block;border:1px solid #e5d6a955;padding:6px 9px;margin:14px 7px 0 0;font:9px 'DM Mono';color:#f4e8c5}.card{background:#fff;border:1px solid #e8ddc0;padding:1.25rem;min-height:126px}.card span{font:9px 'DM Mono';letter-spacing:.09em;color:#806b32}.card b{display:block;font-family:'Playfair Display';font-size:2rem;margin-top:.5rem}.section{border-top:1px solid #e8ddc0;margin:2.5rem 0 1.5rem}.assistant{background:#f8f4e8;border:1px solid #e8ddc0;padding:1.3rem}.assistant p{line-height:1.65}.stButton>button{background:#a7832d;color:#fff;border:0;border-radius:0;font-weight:700}.stButton>button:hover{background:#111111;color:#fff}</style>""",
    unsafe_allow_html=True,
)

if not st.user.is_logged_in:
    st.title("Welcome to WeddingOps")
    st.write("Sign in to open your wedding plan.")
    st.button("Sign in with Google", on_click=st.login)
    st.stop()

subject = st.user.get("sub")
if not subject:
    st.error("Google did not provide an account identifier. Please sign in again.")
    st.stop()
try:
    database_url = st.secrets["database"]["url"]
    data = load_account_wedding(database_url, subject) or blank_wedding()
except Exception:
    st.error("The wedding database is unavailable. Check the database setup and connection in Streamlit secrets.")
    st.stop()
st.session_state.active_profile = subject
budget = budget_summary(data)
attendance = attendance_forecast(data.guests, getattr(data, "expected_guests", None))

def save_current_wedding(updated_data: WeddingData) -> None:
    save_account_wedding(database_url, subject, updated_data)
    st.success("Changes saved.")


with st.sidebar:
    st.markdown("# ✦ WeddingOps")
    st.caption("YOUR PLANNING COMMAND CENTER")
    st.divider()
    st.caption(f"Signed in as {st.user.get('email', 'Google account')}")
    st.button("Sign out", on_click=st.logout)

    with st.expander("Wedding details", expanded=False):
        couple_name = st.text_input(
            "Bride & partner",
            value=data.couple_name,
            key=f"couple_{st.session_state.active_profile}",
        )
        venue = st.text_input(
            "Venue", value=data.venue, key=f"venue_{st.session_state.active_profile}"
        )
        wedding_date = st.date_input(
            "Wedding date",
            value=data.wedding_date,
            key=f"date_{st.session_state.active_profile}",
        )
        wedding_budget = st.number_input(
            "Total budget",
            min_value=0.0,
            step=500.0,
            value=float(data.budget),
            key=f"budget_{st.session_state.active_profile}",
        )
        overridden_committed = getattr(data, "committed", None)
        committed_default = (
            float(overridden_committed)
            if overridden_committed is not None
            else float(budget["committed"])
        )
        committed = st.number_input(
            "Committed spend",
            min_value=0.0,
            step=500.0,
            value=committed_default,
            key=f"committed_{st.session_state.active_profile}",
        )
        paid_default = (
            float(getattr(data, "paid", None))
            if getattr(data, "paid", None) is not None
            else float(budget["paid"])
        )
        paid = st.number_input(
            "Money spent / paid",
            min_value=0.0,
            step=500.0,
            value=paid_default,
            key=f"paid_{st.session_state.active_profile}",
        )
        expected_guests = st.number_input(
            "Expected guests",
            min_value=0,
            step=1,
            value=int(
                getattr(data, "expected_guests", None)
                if getattr(data, "expected_guests", None) is not None
                else attendance["expected"]
            ),
            key=f"expected_guests_{st.session_state.active_profile}",
        )
        if st.button("Save wedding", use_container_width=True):
            save_current_wedding(replace(
                data, budget=float(wedding_budget), wedding_date=wedding_date,
                couple_name=couple_name.strip() or "Your wedding",
                venue=venue.strip() or "Venue to be confirmed",
                committed=float(committed), expected_guests=int(expected_guests), paid=float(paid),
            ))
            st.rerun()
    st.divider()
    page = st.radio(
        "Go to",
        [
            "Overview",
            "Budget & payments",
            "Vendors",
            "Guests & seating",
            "Planning assistant",
        ],
    )
    st.divider()
    st.caption(f"{data.couple_name}")
    st.caption(f"Wedding date\n\n**{data.wedding_date:%B %d, %Y}**")
    st.caption(f"Venue\n\n**{data.venue}**")

if page == "Overview":
    st.markdown(
        '<div class="hero"><p class="eyebrow">{}</p><h1>Plan the day.<br>Keep the calm.</h1><p>WeddingOps brings {} — your budget, vendors, guests, contracts, payment dates, and planning decisions — into one place.</p><span class="pill">{}</span><span class="pill">{:%B %d, %Y}</span><span class="pill">{} EXPECTED GUESTS</span></div>'.format(
            data.couple_name.upper(),
            data.venue,
            data.venue,
            data.wedding_date,
            attendance["expected"],
        ),
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section"></div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(
        f'<div class="card"><span>TOTAL BUDGET</span><b>${budget["budget"]:,.0f}</b></div>',
        unsafe_allow_html=True,
    )
    c2.markdown(
        f'<div class="card"><span>COMMITTED</span><b>${budget["committed"]:,.0f}</b></div>',
        unsafe_allow_html=True,
    )
    c3.markdown(
        f'<div class="card"><span>STILL AVAILABLE</span><b>${budget["remaining"]:,.0f}</b></div>',
        unsafe_allow_html=True,
    )
    c4.markdown(
        f'<div class="card"><span>EXPECTED GUESTS</span><b>{attendance["expected"]}</b></div>',
        unsafe_allow_html=True,
    )
    c5.markdown(
        f'<div class="card"><span>MONEY SPENT</span><b>${budget["paid"]:,.0f}</b></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section"></div>', unsafe_allow_html=True)
    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        st.subheader("Budget by category")
        categories = data.categories.melt(
            id_vars="category",
            value_vars=["planned", "committed"],
            var_name="type",
            value_name="amount",
        )
        chart = px.bar(
            categories,
            x="category",
            y="amount",
            color="type",
            barmode="group",
            color_discrete_map={"planned": "#c9a54b", "committed": "#a7832d"},
        )
        chart.update_layout(
            height=350,
            margin={"l": 0, "r": 0, "t": 10, "b": 0},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend_title_text="",
        )
        st.plotly_chart(
            chart, use_container_width=True, config={"displayModeBar": False}
        )
    with right:
        st.subheader("What needs attention")
        payments = upcoming_payments(data)
        st.write(f"**{len(payments)} payments** are due in the next 45 days.")
        st.write(
            f"**{len(data.vendors[data.vendors.contract != 'Signed'])} vendors** still need a contract or final decision."
        )
        st.write(f"**{attendance['pending']} guests** are still pending an RSVP.")
        st.dataframe(
            payments[["vendor", "next_payment", "due"]],
            hide_index=True,
            use_container_width=True,
        )

elif page == "Budget & payments":
    st.markdown('<p class="eyebrow">BUDGET & PAYMENTS</p>', unsafe_allow_html=True)
    st.title("See what is committed—and what is still flexible.")
    st.caption("Edit the total budget and category amounts, then save. Committed amounts here are tracked by category.")
    total_budget = st.number_input("Total wedding budget", min_value=0.0, value=float(data.budget), step=100.0, key=f"total_budget_{st.session_state.active_profile}")
    categories = st.data_editor(
        data.categories[["category", "planned", "committed"]],
        hide_index=True, use_container_width=True, num_rows="dynamic",
        column_config={
            "category": st.column_config.TextColumn("Category", required=True),
            "planned": st.column_config.NumberColumn("Planned ($)", min_value=0, required=True, format="$%.2f"),
            "committed": st.column_config.NumberColumn("Committed ($)", min_value=0, required=True, format="$%.2f"),
        }, key=f"categories_{st.session_state.active_profile}",
    )
    if st.button("Save budget changes", type="primary"):
        if categories.empty or categories[["category", "planned", "committed"]].isna().any().any() or categories.category.astype(str).str.strip().eq("").any():
            st.error("Add at least one category and fill in its name, planned amount, and committed amount.")
        else:
            save_current_wedding(replace(data, budget=float(total_budget), categories=categories, committed=None))
            st.rerun()
    st.caption("Still flexible by category = planned amount minus committed amount.")
    st.dataframe(data.categories.assign(**{"Still flexible": data.categories.planned - data.categories.committed})[["category", "Still flexible"]], hide_index=True, use_container_width=True, column_config={"Still flexible": st.column_config.NumberColumn(format="$%.2f")})
    st.subheader("Payments")
    st.caption("Update amounts paid and the next payment date here. Remaining balance is the total committed minus paid; it is not necessarily the amount due on that date.")
    payments_edit = st.data_editor(
        data.vendors[["vendor", "committed", "paid", "next_payment"]],
        hide_index=True, use_container_width=True,
        column_config={
            "vendor": st.column_config.TextColumn("Vendor", disabled=True),
            "committed": st.column_config.NumberColumn("Committed ($)", min_value=0, required=True, format="$%.2f"),
            "paid": st.column_config.NumberColumn("Paid ($)", min_value=0, required=True, format="$%.2f"),
            "next_payment": st.column_config.TextColumn("Next payment date (YYYY-MM-DD)", help="Leave blank if no date is set."),
        }, key=f"payments_{st.session_state.active_profile}",
    )
    if st.button("Save payment changes"):
        dates = payments_edit.next_payment.fillna("").astype(str).str.strip()
        invalid = dates.ne("") & pd.to_datetime(dates, format="%Y-%m-%d", errors="coerce").isna()
        if invalid.any() or payments_edit[["committed", "paid"]].isna().any().any():
            st.error("Enter valid dates as YYYY-MM-DD and fill in all amounts.")
        else:
            vendors = data.vendors.copy()
            for col in ["committed", "paid", "next_payment"]:
                vendors[col] = payments_edit[col].to_numpy()
            vendors["next_payment"] = dates.to_numpy()
            save_current_wedding(replace(data, vendors=vendors, paid=None))
            st.rerun()
    st.subheader("Guest-count scenario")
    added = st.slider("Additional guests", 0, 50, 15)
    scenario = guest_count_scenario(data, added)
    a, b, c = st.columns(3)
    a.metric("NEW EXPECTED COUNT", scenario["new_expected_count"])
    b.metric("ADDED COST", f"${scenario['total']:,.0f}")
    c.metric("BUDGET LEFT", f"${budget['remaining'] - scenario['total']:,.0f}")
    st.dataframe(
        pd.DataFrame(
            list(scenario["impact"].items()), columns=["Cost area", "Additional cost"]
        ),
        hide_index=True,
        use_container_width=True,
        column_config={"Additional cost": st.column_config.NumberColumn(format="$%d")},
    )
    st.subheader("Upcoming payment dates")
    st.dataframe(
        upcoming_payments(data),
        hide_index=True,
        use_container_width=True,
        column_config={
            "due": st.column_config.NumberColumn("Remaining balance", format="$%d"),
            "committed": st.column_config.NumberColumn(format="$%d"),
            "paid": st.column_config.NumberColumn(format="$%d"),
        },
    )

elif page == "Vendors":
    st.markdown('<p class="eyebrow">VENDORS</p>', unsafe_allow_html=True)
    st.title("Compare the details before making a decision.")
    scores = vendor_scores(data)
    st.caption("Add or edit vendors below. Scroll across for contact and comparison details; payment amounts can also be edited on Budget & payments.")
    vendors = st.data_editor(
        data.vendors, hide_index=True, use_container_width=True, num_rows="dynamic",
        column_config={
            "vendor": st.column_config.TextColumn("Vendor", required=True),
            "category": st.column_config.TextColumn("Category", required=True),
            "quote": st.column_config.NumberColumn("Quote ($)", min_value=0, required=True, format="$%.2f"),
            "paid": st.column_config.NumberColumn("Paid ($)", min_value=0, required=True, format="$%.2f"),
            "committed": st.column_config.NumberColumn("Committed ($)", min_value=0, required=True, format="$%.2f"),
            "contract": st.column_config.SelectboxColumn("Contract", options=["Quote", "Signed", "Pending", "Not needed"], required=True),
            "next_payment": st.column_config.TextColumn("Next payment (YYYY-MM-DD)"),
            "rating": st.column_config.NumberColumn("Rating / 5", min_value=0.0, max_value=5.0, required=True),
            "fit": st.column_config.NumberColumn("Fit / 5", min_value=0, max_value=5, required=True),
            "contact": st.column_config.TextColumn("Contact"),
        }, key=f"vendors_{st.session_state.active_profile}",
    )
    if st.button("Save vendor changes", type="primary"):
        required = ["vendor", "category", "quote", "paid", "committed", "contract", "rating", "fit"]
        dates = vendors.next_payment.fillna("").astype(str).str.strip()
        invalid_dates = dates.ne("") & pd.to_datetime(dates, format="%Y-%m-%d", errors="coerce").isna()
        if vendors[required].isna().any().any() or vendors.vendor.fillna("").astype(str).str.strip().eq("").any() or vendors.category.fillna("").astype(str).str.strip().eq("").any() or invalid_dates.any():
            st.error("Fill in the required fields and use YYYY-MM-DD for payment dates.")
        else:
            vendors = vendors.copy()
            vendors["next_payment"] = dates
            vendors["contact"] = vendors.contact.fillna("")
            save_current_wedding(replace(data, vendors=vendors, paid=None))
            st.rerun()
    st.subheader("Vendor comparison")
    st.dataframe(
        scores[
            [
                "vendor",
                "category",
                "quote",
                "paid",
                "committed",
                "contract_status",
                "next_payment",
                "rating",
                "fit",
                "value_score",
            ]
        ],
        hide_index=True,
        use_container_width=True,
        column_config={
            "quote": st.column_config.NumberColumn(format="$%d"),
            "paid": st.column_config.NumberColumn(format="$%d"),
            "committed": st.column_config.NumberColumn(format="$%d"),
            "value_score": st.column_config.ProgressColumn(
                "Value score", format="%.0f", min_value=0, max_value=100
            ),
        },
    )
    st.caption(
        "The value score is a simple comparison tool based on price, rating, and fit. It is meant to support—not replace—your own judgment about the vendor."
    )

elif page == "Guests & seating":
    st.markdown('<p class="eyebrow">GUESTS & SEATING</p>', unsafe_allow_html=True)
    st.title("Keep track of RSVPs, meals, and who should sit together.")
    a, b, c, d = st.columns(4)
    a.metric("CONFIRMED", attendance["confirmed"])
    b.metric("PENDING", attendance["pending"])
    c.metric("EXPECTED", attendance["expected"])
    d.metric("LIKELY RANGE", f"{attendance['low']}–{attendance['high']}")
    st.subheader("Guest list")
    guests = st.data_editor(
        data.guests,
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic",
        key=f"guests_{st.session_state.active_profile}",
    )
    if st.button("Save guest changes"):
        updated = WeddingData(
            data.budget,
            data.wedding_date,
            data.vendors,
            guests,
            data.categories,
            data.couple_name,
            data.venue,
            getattr(data, "committed", None),
            getattr(data, "expected_guests", None),
            getattr(data, "paid", None),
        )
        save_current_wedding(updated)
        st.rerun()
    st.subheader("Suggested seating plan")
    st.dataframe(seating_plan(data.guests), hide_index=True, use_container_width=True)
    st.caption(
        "This is a starting point that keeps requested pairings together when possible. You should still review any relationship or family dynamics yourself."
    )

else:
    st.markdown(
        '<p class="eyebrow">GROUNDED PLANNING ASSISTANT</p>', unsafe_allow_html=True
    )
    st.title("Ask a question about the plan.")
    st.markdown(
        '<div class="assistant"><p>This assistant uses the wedding data shown in WeddingOps. Try asking: <b>What is due this month?</b>, <b>Can we add more guests?</b>, <b>What vendors still need a contract?</b>, or <b>How much budget is left?</b></p></div>',
        unsafe_allow_html=True,
    )
    question = st.text_input("Your question", "What payments are due this month?")
    if st.button("Ask WeddingOps ✦"):
        st.markdown(
            f'<div class="assistant"><p>{answer(question, data)}</p></div>',
            unsafe_allow_html=True,
        )

