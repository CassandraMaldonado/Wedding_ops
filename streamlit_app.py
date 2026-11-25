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

