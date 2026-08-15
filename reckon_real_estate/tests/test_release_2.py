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


def test_release_2_fields_have_labels_and_child_grids_have_columns():
    base = ROOT / "reckon_real_estate" / "doctype"
    release_2 = {
        "boq", "boq_item", "boq_revision", "contractor",
        "contractor_work_order", "work_order_item", "measurement_sheet",
        "measurement_item", "running_bill", "running_bill_item",
        "project_budget", "project_budget_item", "sales_target",
        "sales_commission",
    }
    child_tables = {
        "boq_item", "work_order_item", "measurement_item",
        "running_bill_item", "project_budget_item",
    }

    for name in release_2:
        meta = json.loads((base / name / f"{name}.json").read_text(encoding="utf-8"))
        assert all(field.get("label") for field in meta["fields"]), meta["name"]
        if name in child_tables:
            visible = [field for field in meta["fields"] if field.get("in_list_view")]
            assert visible, meta["name"]
            assert sum(field.get("columns", 0) for field in visible) <= 10, meta["name"]
