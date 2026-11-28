from dataclasses import replace
import pandas as pd
from wedding_ops.data import load_wedding, sample_wedding, save_wedding


def test_expenses_survive_profile_round_trip_and_other_edits(tmp_path):
    data = sample_wedding()
    expenses = pd.DataFrame([{"description": "Flowers", "category": "Floral", "budget": 1000.0, "actual": 1200.0, "paid": 300.0, "due_by": "2027-02-01", "notes": "Deposit"}])
    profile = save_wedding(replace(data, expenses=expenses), "Our wedding", tmp_path)
    saved = load_wedding(profile, tmp_path)
    assert saved.expenses.to_dict("records") == expenses.to_dict("records")
    save_wedding(replace(saved, couple_name="Us"), profile, tmp_path)
    assert load_wedding(profile, tmp_path).expenses.to_dict("records") == expenses.to_dict("records")


def test_existing_profiles_without_expenses_still_load(tmp_path):
    data = sample_wedding()
    profile = save_wedding(data, "Existing", tmp_path)
    path = tmp_path / f"{profile}.json"
    import json
    payload = json.loads(path.read_text())
    del payload["expenses"]
    path.write_text(json.dumps(payload))
    assert load_wedding(profile, tmp_path).expenses.empty
