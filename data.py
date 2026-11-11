"""Sample wedding data used by the Streamlit dashboard."""

# I use realistic sample data so every part of the dashboard can be explored
# right away. It includes a budget, vendors, payment dates, guest details, and
# a few seating preferences and conflicts.

from dataclasses import dataclass
from datetime import date

import pandas as pd


@dataclass(frozen=True)
class WeddingData:
    budget: float
    wedding_date: date
    vendors: pd.DataFrame
    guests: pd.DataFrame
    categories: pd.DataFrame


def sample_wedding() -> WeddingData:
    vendors = pd.DataFrame(
        [
            ["Golden Hour Venue", "Venue", 14500, 5000, 14500, "Signed", "2026-05-18", 4.9, 5, "venue@goldenhour.com"],
            ["Mira Catering", "Catering", 10800, 2700, 12400, "Signed", "2026-06-10", 4.7, 4, "hello@miracatering.com"],
            ["Northline Photo", "Photography", 5200, 2600, 5200, "Signed", "2026-07-02", 4.9, 5, "studio@northline.com"],
            ["Paper Moon Floral", "Flowers", 3900, 1000, 4600, "Quote", "2026-06-03", 4.6, 4, "hi@papermoon.com"],
            ["Side B Music", "Music", 2200, 500, 2600, "Quote", "2026-06-24", 4.5, 3, "book@sidebmusic.com"],
            ["Oak & Ink", "Stationery", 1150, 575, 1150, "Signed", "2026-05-30", 4.8, 5, "studio@oakandink.com"],
        ],
        columns=["vendor", "category", "quote", "paid", "committed", "contract", "next_payment", "rating", "fit", "contact"],
    )
    guests = pd.DataFrame(
        [
            ["Avery Kim", "Bride family", "Yes", 1, "Vegetarian", "Table 1", "Jordan Lee", ""],
            ["Jordan Lee", "Bride family", "Yes", 1, "None", "Table 1", "Avery Kim", ""],
            ["Maya Patel", "Groom family", "Yes", 0, "Vegan", "Table 2", "Nina Shah", ""],
            ["Nina Shah", "Groom family", "Pending", 1, "None", "", "Maya Patel", ""],
            ["Sam Rivera", "Friends", "Yes", 1, "None", "Table 3", "Theo Grant", "Chris Park"],
            ["Theo Grant", "Friends", "Yes", 0, "Gluten-free", "Table 3", "Sam Rivera", ""],
            ["Chris Park", "Friends", "Pending", 1, "None", "", "", "Sam Rivera"],
            ["Elena Rossi", "Work", "No", 0, "None", "", "", ""],
            ["Kai Morgan", "Work", "Pending", 0, "None", "", "Elena Rossi", ""],
            ["Riley Chen", "Friends", "Yes", 0, "None", "Table 3", "Sam Rivera", ""],
            ["Drew Wilson", "Groom family", "Yes", 1, "None", "Table 2", "Maya Patel", ""],
            ["Casey Brooks", "Bride family", "Pending", 0, "Vegetarian", "", "Avery Kim", ""],
        ],
        columns=["guest", "group", "rsvp", "plus_ones", "meal", "table", "sit_with", "avoid"],
    )
    categories = pd.DataFrame(
        [
            ["Venue", 14500, 14500], ["Catering", 12000, 10800], ["Photography", 5500, 5200],
            ["Flowers", 4500, 3900], ["Music", 2500, 2200], ["Stationery", 1400, 1150],
            ["Attire", 3600, 2700], ["Other", 2500, 900],
        ],
        columns=["category", "planned", "committed"],
    )
    return WeddingData(48_000, date(2026, 8, 22), vendors, guests, categories)

