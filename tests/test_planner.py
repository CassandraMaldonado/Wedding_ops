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


def test_wedding_profile_round_trip(tmp_path):
    data = sample_wedding()
    data = WeddingData(
        65000,
        date(2027, 6, 12),
        data.vendors,
        data.guests,
        data.categories,
        couple_name="Jamie & Morgan",
        venue="The Glass Garden",
    )

    profile_id = save_wedding(data, "Jamie Morgan", tmp_path)
    restored = load_wedding(profile_id, tmp_path)

    assert restored.budget == 65000
    assert restored.venue == "The Glass Garden"
    assert restored.couple_name == "Jamie & Morgan"
    assert restored.wedding_date.isoformat() == "2027-06-12"


def test_committed_and_expected_guest_overrides(tmp_path):
    data = sample_wedding()
    data = WeddingData(
        70000,
        date(2027, 8, 14),
        data.vendors,
        data.guests,
        data.categories,
        committed=52000,
        expected_guests=145,
    )

    profile_id = save_wedding(data, "Editable Wedding", tmp_path)
    restored = load_wedding(profile_id, tmp_path)

    assert budget_summary(restored)["committed"] == 52000
    assert (
        attendance_forecast(restored.guests, restored.expected_guests)["expected"]
        == 145
    )


def test_old_wedding_data_shape_is_supported():
    data = sample_wedding()
    legacy_data = SimpleNamespace(
        budget=data.budget,
        wedding_date=data.wedding_date,
        vendors=data.vendors,
        guests=data.guests,
        categories=data.categories,
    )

    assert budget_summary(legacy_data)["committed"] == data.categories.committed.sum()
