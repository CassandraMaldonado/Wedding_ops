"""Interactive Streamlit dashboard for WeddingOps."""


import pandas as pd
import plotly.express as px
import streamlit as st

from wedding_ops.assistant import answer
from wedding_ops.data import sample_wedding
from wedding_ops.planner import (
    attendance_forecast,
    budget_summary,
    guest_count_scenario,
    seating_plan,
    upcoming_payments,
    vendor_scores,
)

st.set_page_config(page_title="WeddingOps", page_icon="✦", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Playfair+Display:wght@500;600&family=Manrope:wght@400;500;600;700&display=swap');.stApp{background:#fcfaf7;color:#332a29;font-family:Manrope,sans-serif}.block-container{max-width:1280px;padding-top:2rem}.stSidebar{background:#332a29!important}.stSidebar *{color:#f8f1e8!important}.stSidebar input{color:#332a29!important}h1,h2,h3{font-family:'Playfair Display',serif!important;letter-spacing:-.03em}.eyebrow{font:10px 'DM Mono';letter-spacing:.13em;color:#a05b53}.hero{background:#332a29;color:#f8f1e8;padding:3.5rem;min-height:300px;background-image:radial-gradient(circle at 88% 15%,#d88d7b 0,transparent 25%),radial-gradient(circle at 70% 110%,#c9a85c55 0,transparent 30%)}.hero h1{font-size:4.5rem;line-height:.95;margin:.5rem 0 1.2rem}.hero p{max-width:650px;color:#e1d5cc;line-height:1.65}.pill{display:inline-block;border:1px solid #e1d5cc55;padding:6px 9px;margin:14px 7px 0 0;font:9px 'DM Mono';color:#e9d9d0}.card{background:#fff;border:1px solid #eadfd7;padding:1.25rem;min-height:126px}.card span{font:9px 'DM Mono';letter-spacing:.09em;color:#9b7770}.card b{display:block;font-family:'Playfair Display';font-size:2rem;margin-top:.5rem}.section{border-top:1px solid #eadfd7;margin:2.5rem 0 1.5rem}.assistant{background:#f2e4df;border:1px solid #e8d0c8;padding:1.3rem}.assistant p{line-height:1.65}.stButton>button{background:#a05b53;color:#fff;border:0;border-radius:0;font-weight:700}.stButton>button:hover{background:#332a29;color:#fff}</style>""",unsafe_allow_html=True)

data = sample_wedding()
budget = budget_summary(data)
attendance = attendance_forecast(data.guests)

with st.sidebar:
    st.markdown("# ✦ WeddingOps")
    st.caption("YOUR PLANNING COMMAND CENTER")
    st.divider()
    page = st.radio("Go to", ["Overview", "Budget & payments", "Vendors", "Guests & seating", "Planning assistant"])
    st.divider()
    st.caption(f"Wedding date\n\n**{data.wedding_date:%B %d, %Y}**")

if page == "Overview":
    st.markdown('<div class="hero"><p class="eyebrow">WEDDING PLANNING COMMAND CENTER</p><h1>Plan the day.<br>Keep the calm.</h1><p>WeddingOps brings your budget, vendors, guests, contracts, payment dates, and planning decisions into one place.</p><span class="pill">{:%B %d, %Y}</span><span class="pill">{} EXPECTED GUESTS</span></div>'.format(data.wedding_date, attendance["expected"]), unsafe_allow_html=True)
    st.markdown('<div class="section"></div>',unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    c1.markdown(f'<div class="card"><span>TOTAL BUDGET</span><b>${budget["budget"]:,.0f}</b></div>',unsafe_allow_html=True)
    c2.markdown(f'<div class="card"><span>COMMITTED</span><b>${budget["committed"]:,.0f}</b></div>',unsafe_allow_html=True)
    c3.markdown(f'<div class="card"><span>STILL AVAILABLE</span><b>${budget["remaining"]:,.0f}</b></div>',unsafe_allow_html=True)
    c4.markdown(f'<div class="card"><span>EXPECTED GUESTS</span><b>{attendance["expected"]}</b></div>',unsafe_allow_html=True)
    st.markdown('<div class="section"></div>',unsafe_allow_html=True)
    left,right=st.columns([1.15,.85],gap="large")
    with left:
        st.subheader("Budget by category")
        categories=data.categories.melt(id_vars="category",value_vars=["planned","committed"],var_name="type",value_name="amount")
        chart=px.bar(categories,x="category",y="amount",color="type",barmode="group",color_discrete_map={"planned":"#c9a85c","committed":"#a05b53"})
        chart.update_layout(height=350,margin={"l":0,"r":0,"t":10,"b":0},paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",legend_title_text="")
        st.plotly_chart(chart,use_container_width=True,config={"displayModeBar":False})
    with right:
        st.subheader("What needs attention")
        payments=upcoming_payments(data)
        st.write(f"**{len(payments)} payments** are due in the next 45 days.")
        st.write(f"**{len(data.vendors[data.vendors.contract != 'Signed'])} vendors** still need a contract or final decision.")
        st.write(f"**{attendance['pending']} guests** are still pending an RSVP.")
        st.dataframe(payments[["vendor","next_payment","due"]],hide_index=True,use_container_width=True)

elif page == "Budget & payments":
    st.markdown('<p class="eyebrow">BUDGET & PAYMENTS</p>',unsafe_allow_html=True);st.title("See what is committed—and what is still flexible.")
    st.dataframe(data.categories.assign(remaining=lambda frame: frame.planned-frame.committed),hide_index=True,use_container_width=True,column_config={"planned":st.column_config.NumberColumn("Planned",format="$%d"),"committed":st.column_config.NumberColumn("Committed",format="$%d"),"remaining":st.column_config.NumberColumn("Still flexible",format="$%d")})
    st.subheader("Guest-count scenario")
    added=st.slider("Additional guests",0,50,15)
    scenario=guest_count_scenario(data,added)
    a,b,c=st.columns(3);a.metric("NEW EXPECTED COUNT",scenario["new_expected_count"]);b.metric("ADDED COST",f'${scenario["total"]:,.0f}');c.metric("BUDGET LEFT",f'${budget["remaining"]-scenario["total"]:,.0f}')
    st.dataframe(pd.DataFrame(list(scenario["impact"].items()),columns=["Cost area","Additional cost"]),hide_index=True,use_container_width=True,column_config={"Additional cost":st.column_config.NumberColumn(format="$%d")})
    st.subheader("Upcoming payments")
    st.dataframe(upcoming_payments(data),hide_index=True,use_container_width=True,column_config={"due":st.column_config.NumberColumn(format="$%d"),"committed":st.column_config.NumberColumn(format="$%d"),"paid":st.column_config.NumberColumn(format="$%d")})

elif page == "Vendors":
    st.markdown('<p class="eyebrow">VENDORS</p>',unsafe_allow_html=True);st.title("Compare the details before making a decision.")
    scores=vendor_scores(data)
    st.dataframe(scores[["vendor","category","quote","paid","committed","contract_status","next_payment","rating","fit","value_score"]],hide_index=True,use_container_width=True,column_config={"quote":st.column_config.NumberColumn(format="$%d"),"paid":st.column_config.NumberColumn(format="$%d"),"committed":st.column_config.NumberColumn(format="$%d"),"value_score":st.column_config.ProgressColumn("Value score",format="%.0f",min_value=0,max_value=100)})
    st.caption("The value score is a simple comparison tool based on price, rating, and fit. It is meant to support—not replace—your own judgment about the vendor.")

elif page == "Guests & seating":
    st.markdown('<p class="eyebrow">GUESTS & SEATING</p>',unsafe_allow_html=True);st.title("Keep track of RSVPs, meals, and who should sit together.")
    a,b,c,d=st.columns(4);a.metric("CONFIRMED",attendance["confirmed"]);b.metric("PENDING",attendance["pending"]);c.metric("EXPECTED",attendance["expected"]);d.metric("LIKELY RANGE",f'{attendance["low"]}–{attendance["high"]}')
    st.subheader("Guest list")
    st.dataframe(data.guests,hide_index=True,use_container_width=True)
    st.subheader("Suggested seating plan")
    st.dataframe(seating_plan(data.guests),hide_index=True,use_container_width=True)
    st.caption("This is a starting point that keeps requested pairings together when possible. You should still review any relationship or family dynamics yourself.")

else:
    st.markdown('<p class="eyebrow">GROUNDED PLANNING ASSISTANT</p>',unsafe_allow_html=True);st.title("Ask a question about the plan.")
    st.markdown('<div class="assistant"><p>This assistant uses the wedding data shown in WeddingOps. Try asking: <b>What is due this month?</b>, <b>Can we add more guests?</b>, <b>What vendors still need a contract?</b>, or <b>How much budget is left?</b></p></div>',unsafe_allow_html=True)
    question=st.text_input("Your question","What payments are due this month?")
    if st.button("Ask WeddingOps ✦"):
        st.markdown(f'<div class="assistant"><p>{answer(question,data)}</p></div>',unsafe_allow_html=True)

