"""Grounded planning assistant for common wedding questions."""

# I designed this as a grounded assistant instead of a generic chatbot. It only
# answers from the budget, vendor, and guest data in the app, so the advice is
# transparent and easy to check.

from .data import WeddingData
from .planner import attendance_forecast, budget_summary, guest_count_scenario, upcoming_payments


def answer(question: str, data: WeddingData) -> str:
    text = question.lower()
    summary = budget_summary(data)
    if any(word in text for word in ("payment", "due", "month")):
        payments = upcoming_payments(data)
        if payments.empty:
            return "There are no vendor payments due in the next 45 days in the current plan."
        items = ", ".join(f"{row.vendor} (${row.due:,.0f} due {row.next_payment:%b %d})" for _, row in payments.iterrows())
        return f"The next payments to plan for are {items}. Total upcoming payments: ${payments.due.sum():,.0f}."
    if any(word in text for word in ("add", "increase", "more guests")):
        scenario = guest_count_scenario(data, 15)
        return f"Adding 15 guests would add about ${scenario['total']:,.0f}, mostly from catering, bar, rentals, and stationery. Your expected count would become {scenario['new_expected_count']}."
    if any(word in text for word in ("guest", "attendance", "rsvp")):
        forecast = attendance_forecast(data.guests)
        return f"You currently have {forecast['confirmed']} confirmed guests. Based on pending RSVPs, I would plan for about {forecast['expected']} guests, with a likely range of {forecast['low']} to {forecast['high']}."
    if any(word in text for word in ("budget", "afford", "remaining")):
        return f"You have ${summary['remaining']:,.0f} left in the budget after current committed costs. The plan has ${summary['unallocated']:,.0f} not yet assigned to a category, so I would protect that before adding optional upgrades."
    if any(word in text for word in ("contract", "vendor")):
        pending = data.vendors[data.vendors.contract != "Signed"]
        names = ", ".join(pending.vendor)
        return f"The vendors that still need a decision or contract are {names}. I would confirm scope, cancellation terms, and the final payment schedule before committing."
    return "Try asking about your budget, upcoming payments, guest count, RSVPs, vendors, contracts, or adding guests. I will use the planning data in this dashboard to answer."

