"""Budget, vendor, guest, and seating calculations for WeddingOps."""

# This is where I turn the wedding data into useful planning information. I
# calculate budget pressure, upcoming payments, likely attendance, scenario
# costs, vendor comparison scores, and a simple seating recommendation.

from datetime import date, timedelta

import pandas as pd

from .data import WeddingData


def budget_summary(data: WeddingData) -> dict:
    planned = float(data.categories.planned.sum())
    committed = float(data.categories.committed.sum())
    paid = float(data.vendors.paid.sum())
    return {"budget": data.budget, "planned": planned, "committed": committed, "paid": paid, "remaining": data.budget - committed, "unallocated": data.budget - planned}


def upcoming_payments(data: WeddingData, days: int = 45, today: date = date(2026, 5, 15)) -> pd.DataFrame:
    vendors = data.vendors.copy()
    vendors["next_payment"] = pd.to_datetime(vendors.next_payment).dt.date
    mask = (vendors.next_payment >= today) & (vendors.next_payment <= today + timedelta(days=days))
    result = vendors.loc[mask, ["vendor", "category", "next_payment", "committed", "paid", "contract"]].copy()
    result["due"] = result.committed - result.paid
    return result.sort_values("next_payment")


def attendance_forecast(guests: pd.DataFrame) -> dict:
    yes = guests[guests.rsvp == "Yes"]
    pending = guests[guests.rsvp == "Pending"]
    confirmed = int(len(yes) + yes.plus_ones.sum())
    expected_pending = round((len(pending) + pending.plus_ones.sum()) * 0.63)
    return {
        "confirmed": confirmed,
        "pending": int(len(pending) + pending.plus_ones.sum()),
        "expected": confirmed + expected_pending,
        "low": confirmed + round(expected_pending * 0.75),
        "high": confirmed + round(expected_pending * 1.20),
    }


def guest_count_scenario(data: WeddingData, additional_guests: int) -> dict:
    forecast = attendance_forecast(data.guests)
    per_guest = {"catering": 92, "bar": 31, "rentals": 18, "stationery": 7}
    impact = {name: amount * additional_guests for name, amount in per_guest.items()}
    return {"new_expected_count": forecast["expected"] + additional_guests, "additional_guests": additional_guests, "impact": impact, "total": sum(impact.values())}


def vendor_scores(data: WeddingData) -> pd.DataFrame:
    result = data.vendors.copy()
    max_quote = result.quote.max()
    result["value_score"] = ((1 - result.quote / max_quote) * 0.35 + (result.rating / 5) * 0.35 + (result.fit / 5) * 0.30) * 100
    result["contract_status"] = result.contract.map({"Signed": "Ready", "Quote": "Needs decision"})
    return result.sort_values("value_score", ascending=False)


def seating_plan(guests: pd.DataFrame, table_size: int = 8) -> pd.DataFrame:
    attending = guests[guests.rsvp == "Yes"].copy().reset_index(drop=True)
    tables: list[list[str]] = []
    for _, person in attending.iterrows():
        preferred = person.sit_with
        placement = next((i for i, table in enumerate(tables) if preferred in table and len(table) < table_size), None)
        if placement is None:
            placement = next((i for i, table in enumerate(tables) if len(table) < table_size), len(tables))
            if placement == len(tables):
                tables.append([])
        tables[placement].append(person.guest)
    return pd.DataFrame([{"table": f"Table {i + 1}", "guests": ", ".join(table), "seats_used": len(table), "seats_open": table_size - len(table)} for i, table in enumerate(tables)])

