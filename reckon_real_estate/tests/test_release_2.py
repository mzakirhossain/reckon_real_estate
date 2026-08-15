import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_release_2_standard_json_is_valid():
    for path in ROOT.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))


def test_release_2_doctypes_are_present():
    base = ROOT / "reckon_real_estate" / "doctype"
    expected = {
        "boq", "contractor", "contractor_work_order",
        "measurement_sheet", "running_bill", "project_budget", "sales_target",
        "sales_commission",
    }
    assert expected <= {path.name for path in base.iterdir() if path.is_dir()}


def test_release_2_fields_have_labels_and_child_grids_have_columns():
    base = ROOT / "reckon_real_estate" / "doctype"
    release_2 = {
        "boq", "boq_item", "contractor",
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
            assert meta.get("editable_grid") == 1, meta["name"]
            visible = [field for field in meta["fields"] if field.get("in_list_view")]
            assert visible, meta["name"]
            assert sum(field.get("columns", 0) for field in visible) <= 10, meta["name"]


def test_release_2_child_tables_are_embedded_in_their_parents():
    base = ROOT / "reckon_real_estate" / "doctype"
    mappings = {
        "boq": "BOQ Item",
        "project_budget": "Project Budget Item",
        "running_bill": "Running Bill Item",
        "measurement_sheet": "Measurement Item",
        "contractor_work_order": "Work Order Item",
    }

    for parent, child in mappings.items():
        parent_meta = json.loads(
            (base / parent / f"{parent}.json").read_text(encoding="utf-8")
        )
        items_field = next(
            field for field in parent_meta["fields"] if field["fieldname"] == "items"
        )
        assert items_field["fieldtype"] == "Table", parent_meta["name"]
        assert items_field["options"] == child, parent_meta["name"]
        assert items_field["reqd"] == 1, parent_meta["name"]

        child_folder = child.lower().replace(" ", "_")
        child_meta = json.loads(
            (base / child_folder / f"{child_folder}.json").read_text(encoding="utf-8")
        )
        assert child_meta["istable"] == 1, child
        assert child_meta["editable_grid"] == 1, child


def test_construction_parents_use_submission_flow_and_two_column_layout():
    base = ROOT / "reckon_real_estate" / "doctype"
    parents = {
        "boq": "boq_no",
        "project_budget": "budget_no",
        "contractor": "contractor_no",
        "contractor_work_order": "work_order_no",
        "measurement_sheet": "measurement_no",
        "running_bill": "running_bill_no",
    }

    for folder, number_field in parents.items():
        meta = json.loads((base / folder / f"{folder}.json").read_text(encoding="utf-8"))
        fields = {field["fieldname"]: field for field in meta["fields"]}
        assert meta["is_submittable"] == 1, meta["name"]
        assert fields[number_field]["read_only"] == 1, meta["name"]
        assert fields[number_field]["unique"] == 1, meta["name"]
        assert fields[number_field]["no_copy"] == 1, meta["name"]
        assert fields["status"]["read_only"] == 1, meta["name"]
        assert fields["status"]["options"] == "Draft\nSubmitted\nCancelled", meta["name"]
        assert fields["amended_from"]["options"] == meta["name"], meta["name"]
        assert fields["amended_from"]["no_copy"] == 1, meta["name"]
        assert any(field["fieldtype"] == "Column Break" for field in meta["fields"]), meta["name"]


def test_boq_revision_doctype_is_removed():
    base = ROOT / "reckon_real_estate" / "doctype"
    assert not (base / "boq_revision" / "boq_revision.json").exists()
