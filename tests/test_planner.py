from wedding_ops.assistant import answer
from wedding_ops.data import sample_wedding
from wedding_ops.planner import (
    attendance_forecast,
    budget_summary,
    guest_count_scenario,
    seating_plan,
    vendor_scores,
)


def test_budget_summary_is_consistent():
    summary = budget_summary(sample_wedding())
    assert summary["remaining"] == summary["budget"] - summary["committed"]
    assert summary["paid"] < summary["committed"]


def test_attendance_and_guest_scenario_are_reasonable():
    data = sample_wedding()
    forecast = attendance_forecast(data.guests)
    scenario = guest_count_scenario(data, 15)
    assert forecast["low"] <= forecast["expected"] <= forecast["high"]
    assert scenario["total"] > 0
    assert scenario["new_expected_count"] == forecast["expected"] + 15


def test_vendor_scoring_and_seating_plan():
    data = sample_wedding()
    scored = vendor_scores(data)
    tables = seating_plan(data.guests)
    assert scored.value_score.between(0, 100).all()
    assert tables.seats_used.max() <= 8


def test_grounded_assistant_answers_common_questions():
    data = sample_wedding()
    assert "upcoming payments" in answer("What is due this month?", data).lower()
    assert "budget" in answer("How much budget is left?", data).lower()

