# Dashboard for WeddingOps.

import pandas as pd
import plotly.express as px
import streamlit as st

from wedding_ops.assistant import answer
from wedding_ops.data import (
    WeddingData,
    list_profiles,
    load_wedding,
    sample_wedding,
    save_wedding,
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
    """<style>@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Playfair+Display:wght@500;600&family=Manrope:wght@400;500;600;700&display=swap');.stApp{background:#fcfaf7;color:#332a29;font-family:Manrope,sans-serif}.block-container{max-width:1280px;padding-top:2rem}.stSidebar{background:#332a29!important}.stSidebar *{color:#f8f1e8!important}.stSidebar input{color:#332a29!important}h1,h2,h3{font-family:'Playfair Display',serif!important;letter-spacing:-.03em}.eyebrow{font:10px 'DM Mono';letter-spacing:.13em;color:#a05b53}.hero{background:#332a29;color:#f8f1e8;padding:3.5rem;min-height:300px;background-image:radial-gradient(circle at 88% 15%,#d88d7b 0,transparent 25%),radial-gradient(circle at 70% 110%,#c9a85c55 0,transparent 30%)}.hero h1{font-size:4.5rem;line-height:.95;margin:.5rem 0 1.2rem}.hero p{max-width:650px;color:#e1d5cc;line-height:1.65}.pill{display:inline-block;border:1px solid #e1d5cc55;padding:6px 9px;margin:14px 7px 0 0;font:9px 'DM Mono';color:#e9d9d0}.card{background:#fff;border:1px solid #eadfd7;padding:1.25rem;min-height:126px}.card span{font:9px 'DM Mono';letter-spacing:.09em;color:#9b7770}.card b{display:block;font-family:'Playfair Display';font-size:2rem;margin-top:.5rem}.section{border-top:1px solid #eadfd7;margin:2.5rem 0 1.5rem}.assistant{background:#f2e4df;border:1px solid #e8d0c8;padding:1.3rem}.assistant p{line-height:1.65}.stButton>button{background:#a05b53;color:#fff;border:0;border-radius:0;font-weight:700}.stButton>button:hover{background:#332a29;color:#fff}</style>""",
    unsafe_allow_html=True,
)

profiles = list_profiles()
if "active_profile" not in st.session_state:
    st.session_state.active_profile = profiles[0] if profiles else "demo"

if st.session_state.active_profile == "demo":
    data = sample_wedding()
else:
    data = load_wedding(st.session_state.active_profile)
budget = budget_summary(data)
attendance = attendance_forecast(data.guests, getattr(data, "expected_guests", None))
