import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_release_2_standard_json_is_valid():
    for path in ROOT.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))


def test_release_2_doctypes_are_present():
    base = ROOT / "reckon_real_estate" / "doctype"
    expected = {
        "boq", "boq_revision", "contractor", "contractor_work_order",
        "measurement_sheet", "running_bill", "project_budget", "sales_target",
        "sales_commission",
    }
    assert expected <= {path.name for path in base.iterdir() if path.is_dir()}
