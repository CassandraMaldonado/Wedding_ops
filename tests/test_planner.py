from datetime import date
from types import SimpleNamespace

from wedding_ops.assistant import answer
from wedding_ops.data import WeddingData, load_wedding, sample_wedding, save_wedding
from wedding_ops.planner import (
    attendance_forecast,
    budget_summary,
    guest_count_scenario,
    seating_plan,
    vendor_scores,
)

