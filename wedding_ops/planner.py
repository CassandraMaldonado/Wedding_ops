# I calculate budget pressure, upcoming payments, likely attendance, scenario costs, vendor comparison scores and seating recommendations.

from datetime import date, timedelta

import pandas as pd

from .data import WeddingData


def budget_summary(data: WeddingData) -> dict:
    planned = float(data.categories.planned.sum())
    overridden_committed = getattr(data, "committed", None)
    committed = (
        float(overridden_committed)
        if overridden_committed is not None
        else float(data.categories.committed.sum())
    )
    overridden_paid = getattr(data, "paid", None)
    paid = (
        float(overridden_paid)
        if overridden_paid is not None
        else float(data.vendors.paid.sum())
    )
    return {
        "budget": data.budget,
        "planned": planned,
        "committed": committed,
        "paid": paid,
        "remaining": data.budget - committed,
        "unallocated": data.budget - planned,
    }


def upcoming_payments(
    data: WeddingData, days: int = 45, today: date | None = None
) -> pd.DataFrame:
    today = today or date.today()
    vendors = data.vendors.copy()
    vendors["next_payment"] = pd.to_datetime(vendors.next_payment, errors="coerce").dt.date
    mask = (vendors.next_payment >= today) & (
        vendors.next_payment <= today + timedelta(days=days)
    )
    result = vendors.loc[
        mask, ["vendor", "category", "next_payment", "committed", "paid", "contract"]
    ].copy()
    result["due"] = result.committed - result.paid
    return result.sort_values("next_payment")


def attendance_forecast(
    guests: pd.DataFrame, expected_guests: int | None = None
) -> dict:
    yes = guests[guests.rsvp == "Yes"]
    pending = guests[guests.rsvp == "Pending"]
    confirmed = int(len(yes) + yes.plus_ones.sum())
    expected_pending = round((len(pending) + pending.plus_ones.sum()) * 0.63)
    calculated_expected = confirmed + expected_pending
    expected = (
        int(expected_guests) if expected_guests is not None else calculated_expected
    )
    return {
        "confirmed": confirmed,
        "pending": int(len(pending) + pending.plus_ones.sum()),
        "expected": expected,
        "low": min(confirmed + round(expected_pending * 0.75), expected),
        "high": max(confirmed + round(expected_pending * 1.20), expected),
    }


def guest_count_scenario(data: WeddingData, additional_guests: int) -> dict:
    forecast = attendance_forecast(data.guests, getattr(data, "expected_guests", None))
    per_guest = {"catering": 92, "bar": 31, "rentals": 18, "stationery": 7}
    impact = {name: amount * additional_guests for name, amount in per_guest.items()}
    return {
        "new_expected_count": forecast["expected"] + additional_guests,
        "additional_guests": additional_guests,
        "impact": impact,
        "total": sum(impact.values()),
    }


def vendor_scores(data: WeddingData) -> pd.DataFrame:
    result = data.vendors.copy()
    max_quote = result.quote.max() or 1
    result["value_score"] = (
        (1 - result.quote / max_quote) * 0.35
        + (result.rating / 5) * 0.35
        + (result.fit / 5) * 0.30
    ) * 100
    result["contract_status"] = result.contract.map(
        {"Signed": "Ready", "Quote": "Needs decision"}
    )
    return result.sort_values("value_score", ascending=False)


def seating_plan(guests: pd.DataFrame, table_size: int = 8) -> pd.DataFrame:
    attending = guests[guests.rsvp == "Yes"].copy().reset_index(drop=True)
    tables: list[list[str]] = []
    for _, person in attending.iterrows():
        preferred = person.sit_with
        placement = next(
            (
                i
                for i, table in enumerate(tables)
                if preferred in table and len(table) < table_size
            ),
            None,
        )
        if placement is None:
            placement = next(
                (i for i, table in enumerate(tables) if len(table) < table_size),
                len(tables),
            )
            if placement == len(tables):
                tables.append([])
        tables[placement].append(person.guest)
    return pd.DataFrame(
        [
            {
                "table": f"Table {i + 1}",
                "guests": ", ".join(table),
                "seats_used": len(table),
                "seats_open": table_size - len(table),
            }
            for i, table in enumerate(tables)
        ]
    )
