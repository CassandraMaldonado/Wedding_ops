# I use sample data so every part of the dashboard can be explored right away.
# It includes budget, vendors, payment dates, guest details and seating preferences.

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class WeddingData:
    budget: float
    wedding_date: date
    vendors: pd.DataFrame
    guests: pd.DataFrame
    categories: pd.DataFrame
    couple_name: str = "Avery & Jordan"
    venue: str = "Golden Hour Venue"
    committed: float | None = None
    expected_guests: int | None = None
    paid: float | None = None


def sample_wedding() -> WeddingData:
    vendors = pd.DataFrame(
        [
            [
                "Golden Hour Venue",
                "Venue",
                14500,
                5000,
                14500,
                "Signed",
                "2026-05-18",
                4.9,
                5,
                "venue@goldenhour.com",
            ],
            [
                "Mira Catering",
                "Catering",
                10800,
                2700,
                12400,
                "Signed",
                "2026-06-10",
                4.7,
                4,
                "hello@miracatering.com",
            ],
            [
                "Northline Photo",
                "Photography",
                5200,
                2600,
                5200,
                "Signed",
                "2026-07-02",
                4.9,
                5,
                "studio@northline.com",
            ],
            [
                "Paper Moon Floral",
                "Flowers",
                3900,
                1000,
                4600,
                "Quote",
                "2026-06-03",
                4.6,
                4,
                "hi@papermoon.com",
            ],
            [
                "Side B Music",
                "Music",
                2200,
                500,
                2600,
                "Quote",
                "2026-06-24",
                4.5,
                3,
                "book@sidebmusic.com",
            ],
            [
                "Oak & Ink",
                "Stationery",
                1150,
                575,
                1150,
                "Signed",
                "2026-05-30",
                4.8,
                5,
                "studio@oakandink.com",
            ],
        ],
        columns=[
            "vendor",
            "category",
            "quote",
            "paid",
            "committed",
            "contract",
            "next_payment",
            "rating",
            "fit",
            "contact",
        ],
    )
    guests = pd.DataFrame(
        [
            [
                "Avery Kim",
                "Bride family",
                "Yes",
                1,
                "Vegetarian",
                "Table 1",
                "Jordan Lee",
                "",
            ],
            [
                "Jordan Lee",
                "Bride family",
                "Yes",
                1,
                "None",
                "Table 1",
                "Avery Kim",
                "",
            ],
            [
                "Maya Patel",
                "Groom family",
                "Yes",
                0,
                "Vegan",
                "Table 2",
                "Nina Shah",
                "",
            ],
            ["Nina Shah", "Groom family", "Pending", 1, "None", "", "Maya Patel", ""],
            [
                "Sam Rivera",
                "Friends",
                "Yes",
                1,
                "None",
                "Table 3",
                "Theo Grant",
                "Chris Park",
            ],
            [
                "Theo Grant",
                "Friends",
                "Yes",
                0,
                "Gluten-free",
                "Table 3",
                "Sam Rivera",
                "",
            ],
            ["Chris Park", "Friends", "Pending", 1, "None", "", "", "Sam Rivera"],
            ["Elena Rossi", "Work", "No", 0, "None", "", "", ""],
            ["Kai Morgan", "Work", "Pending", 0, "None", "", "Elena Rossi", ""],
            ["Riley Chen", "Friends", "Yes", 0, "None", "Table 3", "Sam Rivera", ""],
            [
                "Drew Wilson",
                "Groom family",
                "Yes",
                1,
                "None",
                "Table 2",
                "Maya Patel",
                "",
            ],
            [
                "Casey Brooks",
                "Bride family",
                "Pending",
                0,
                "Vegetarian",
                "",
                "Avery Kim",
                "",
            ],
        ],
        columns=[
            "guest",
            "group",
            "rsvp",
            "plus_ones",
            "meal",
            "table",
            "sit_with",
            "avoid",
        ],
    )
    categories = pd.DataFrame(
        [
            ["Venue", 14500, 14500],
            ["Catering", 12000, 10800],
            ["Photography", 5500, 5200],
            ["Flowers", 4500, 3900],
            ["Music", 2500, 2200],
            ["Stationery", 1400, 1150],
            ["Attire", 3600, 2700],
            ["Other", 2500, 900],
        ],
        columns=["category", "planned", "committed"],
    )
    return WeddingData(
        48_000,
        date(2026, 8, 22),
        vendors,
        guests,
        categories,
        couple_name="Avery & Jordan",
        venue="Golden Hour Venue",
    )


def _profiles_dir(directory: Path | None = None) -> Path:
    if directory is not None:
        return Path(directory)
    return Path(__file__).resolve().parent.parent / "wedding_profiles"


def _profile_id(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "wedding"


def list_profiles(directory: Path | None = None) -> list[str]:
    folder = _profiles_dir(directory)
    if not folder.exists():
        return []
    return sorted(path.stem for path in folder.glob("*.json"))


def save_wedding(data: WeddingData, name: str, directory: Path | None = None) -> str:
    folder = _profiles_dir(directory)
    folder.mkdir(parents=True, exist_ok=True)
    profile_id = _profile_id(name)
    payload = {
        "profile_name": name,
        "couple_name": data.couple_name,
        "venue": data.venue,
        "budget": data.budget,
        "committed": getattr(data, "committed", None),
        "expected_guests": getattr(data, "expected_guests", None),
        "paid": getattr(data, "paid", None),
        "wedding_date": data.wedding_date.isoformat(),
        "vendors": data.vendors.to_dict(orient="records"),
        "guests": data.guests.to_dict(orient="records"),
        "categories": data.categories.to_dict(orient="records"),
    }
    (folder / f"{profile_id}.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    return profile_id


def load_wedding(profile_name: str, directory: Path | None = None) -> WeddingData:
    path = _profiles_dir(directory) / f"{_profile_id(profile_name)}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return WeddingData(
        budget=float(payload["budget"]),
        wedding_date=date.fromisoformat(payload["wedding_date"]),
        vendors=pd.DataFrame(payload["vendors"], columns=["vendor", "category", "quote", "paid", "committed", "contract", "next_payment", "rating", "fit", "contact"]),
        guests=pd.DataFrame(payload["guests"]),
        categories=pd.DataFrame(payload["categories"]),
        couple_name=payload.get("couple_name", payload["profile_name"]),
        venue=payload.get("venue", "Venue to be confirmed"),
        committed=payload.get("committed"),
        expected_guests=payload.get("expected_guests"),
        paid=payload.get("paid"),
    )


def blank_wedding() -> WeddingData:
    """Create an empty plan with the same editable columns as the sample."""
    sample = sample_wedding()
    return WeddingData(
        0.0, date.today(), sample.vendors.iloc[:0].copy(),
        sample.guests.iloc[:0].copy(), sample.categories.iloc[:0].copy(),
        couple_name="Your wedding", venue="Venue to be confirmed",
    )


def load_account_wedding(database_url: str, subject: str) -> WeddingData | None:
    import psycopg

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT payload FROM wedding_accounts WHERE google_subject = %s", (subject,))
            row = cur.fetchone()
    if row is None:
        return None
    payload = row[0]
    sample = sample_wedding()
    return WeddingData(
        budget=float(payload["budget"]), wedding_date=date.fromisoformat(payload["wedding_date"]),
        vendors=pd.DataFrame(payload["vendors"], columns=sample.vendors.columns),
        guests=pd.DataFrame(payload["guests"], columns=sample.guests.columns),
        categories=pd.DataFrame(payload["categories"], columns=sample.categories.columns),
        couple_name=payload.get("couple_name", "Your wedding"),
        venue=payload.get("venue", "Venue to be confirmed"),
        committed=payload.get("committed"), expected_guests=payload.get("expected_guests"),
        paid=payload.get("paid"),
    )


def save_account_wedding(database_url: str, subject: str, data: WeddingData) -> None:
    import psycopg
    from psycopg.types.json import Jsonb

    payload = {
        "budget": data.budget, "wedding_date": data.wedding_date.isoformat(),
        "vendors": data.vendors.to_dict(orient="records"),
        "guests": data.guests.to_dict(orient="records"),
        "categories": data.categories.to_dict(orient="records"),
        "couple_name": data.couple_name, "venue": data.venue,
        "committed": data.committed, "expected_guests": data.expected_guests, "paid": data.paid,
    }
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO wedding_accounts (google_subject, payload) VALUES (%s, %s) ON CONFLICT (google_subject) DO UPDATE SET payload = EXCLUDED.payload", (subject, Jsonb(payload)))
