import json
import re
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
        "sales_agreement",
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
        assert not fields[number_field].get("reqd"), meta["name"]
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


def test_release_1_parents_use_numbering_submission_and_two_columns():
    base = ROOT / "reckon_real_estate" / "doctype"
    parents = {
        "real_estate_project": "project_code",
        "real_estate_building": "building_code",
        "real_estate_floor": "floor_code",
        "real_estate_unit": "unit_code",
        "property_booking": "booking_no",
        "installment_plan": "plan_no",
        "collection_entry": "collection_no",
    }

    for folder, number_field in parents.items():
        meta = json.loads((base / folder / f"{folder}.json").read_text(encoding="utf-8"))
        fields = {field["fieldname"]: field for field in meta["fields"]}
        assert meta["is_submittable"] == 1, meta["name"]
        assert meta["autoname"].startswith("format:"), meta["name"]
        assert fields[number_field]["read_only"] == 1, meta["name"]
        assert not fields[number_field].get("reqd"), meta["name"]
        assert fields[number_field]["unique"] == 1, meta["name"]
        assert fields[number_field]["no_copy"] == 1, meta["name"]
        assert fields["document_status"]["read_only"] == 1, meta["name"]
        assert fields["document_status"]["options"] == "Draft\nSubmitted\nCancelled", meta["name"]
        assert fields["amended_from"]["options"] == meta["name"], meta["name"]
        assert fields["amended_from"]["no_copy"] == 1, meta["name"]
        assert any(field["fieldtype"] == "Column Break" for field in meta["fields"]), meta["name"]


def test_release_3_uses_native_erpnext_accounting_links():
    base = ROOT / "reckon_real_estate" / "doctype"
    plan = json.loads((base / "installment_plan" / "installment_plan.json").read_text(encoding="utf-8"))
    plan_fields = {field["fieldname"]: field for field in plan["fields"]}
    assert plan_fields["sales_agreement"]["options"] == "Sales Agreement"
    assert plan_fields["sales_invoice"]["options"] == "Sales Invoice"

    collection = json.loads((base / "collection_entry" / "collection_entry.json").read_text(encoding="utf-8"))
    collection_fields = {field["fieldname"]: field for field in collection["fields"]}
    assert collection_fields["payment_entry"]["options"] == "Payment Entry"
    assert collection_fields["accounting_status"]["read_only"] == 1

    for child in ("installment_schedule", "payment_allocation"):
        meta = json.loads((base / child / f"{child}.json").read_text(encoding="utf-8"))
        assert meta["istable"] == 1, meta["name"]
        assert meta["editable_grid"] == 1, meta["name"]

    reports = ROOT / "reckon_real_estate" / "report"
    assert (reports / "accounting_reconciliation" / "accounting_reconciliation.py").exists()
    assert (reports / "project_profitability" / "project_profitability.py").exists()


def test_home_workspace_has_three_cards_and_two_charts_at_the_top():
    workspace_path = (
        ROOT / "reckon_real_estate" / "workspace" / "real_estate" / "real_estate.json"
    )
    workspace = json.loads(workspace_path.read_text(encoding="utf-8"))
    content = json.loads(workspace["content"])

    assert [item["type"] for item in content[1:6]] == [
        "number_card", "number_card", "number_card", "chart", "chart"
    ]
    assert [item["data"]["number_card_name"] for item in content[1:4]] == [
        "Total Booked Sales", "Total Collections", "Outstanding Receivables"
    ]
    assert [item["data"]["chart_name"] for item in content[4:6]] == [
        "Monthly Booked Sales", "Monthly Collections"
    ]
    assert [row["number_card_name"] for row in workspace["number_cards"]] == [
        "Total Booked Sales", "Total Collections", "Outstanding Receivables"
    ]
    assert [row["chart_name"] for row in workspace["charts"]] == [
        "Monthly Booked Sales", "Monthly Collections"
    ]


def test_home_analytics_are_installed_during_setup_and_migration():
    install = (ROOT / "setup" / "install.py").read_text(encoding="utf-8")
    assert install.count("ensure_home_analytics()") == 3
    for label in (
        "Total Booked Sales",
        "Total Collections",
        "Outstanding Receivables",
        "Monthly Booked Sales",
        "Monthly Collections",
    ):
        assert label in install
    assert "_register_workspace_analytics" in install


def test_collection_allocations_support_down_payments_and_installments():
    base = ROOT / "reckon_real_estate" / "doctype"
    allocation = json.loads(
        (base / "payment_allocation" / "payment_allocation.json").read_text(encoding="utf-8")
    )
    fields = {field["fieldname"]: field for field in allocation["fields"]}
    assert fields["allocation_type"]["options"] == "Down Payment\nInstallment"
    assert not fields["installment_no"].get("reqd")

    collection = json.loads(
        (base / "collection_entry" / "collection_entry.json").read_text(encoding="utf-8")
    )
    collection_fields = {field["fieldname"]: field for field in collection["fields"]}
    assert collection_fields["installment_plan"]["options"] == "Installment Plan"


def test_installment_aging_report_and_workspace_links_are_registered():
    report = ROOT / "reckon_real_estate" / "report" / "installment_due_collection_aging"
    report_meta = json.loads(
        (report / "installment_due_collection_aging.json").read_text(encoding="utf-8")
    )
    assert report_meta["name"] == "Installment Due Collection Aging"

    workspace = json.loads(
        (ROOT / "reckon_real_estate" / "workspace" / "real_estate" / "real_estate.json").read_text(encoding="utf-8")
    )
    report_links = {row.get("link_to") for row in workspace["links"] if row.get("link_type") == "Report"}
    assert "Collection Overdue" in report_links
    assert "Installment Due Collection Aging" in report_links


def test_all_standard_reports_have_frappe_reference_doctypes_and_query_links():
    reports_root = ROOT / "reckon_real_estate" / "report"
    report_names = set()
    for report_path in reports_root.glob("*/*.json"):
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert report.get("ref_doctype"), report["name"]
        assert report.get("report_type") == "Script Report", report["name"]
        assert report.get("is_standard") == "Yes", report["name"]
        module_name = re.sub(r"[\s-]+", "_", report["name"].lower())
        assert module_name == report_path.parent.name, report["name"]
        report_names.add(report["name"])

    workspace = json.loads(
        (ROOT / "reckon_real_estate" / "workspace" / "real_estate" / "real_estate.json").read_text(encoding="utf-8")
    )
    for link in workspace["links"]:
        if link.get("link_type") == "Report" and link.get("link_to") in report_names:
            assert link.get("is_query_report") == 1, link["link_to"]


def test_release_4_land_handover_and_after_sales_schema():
    base = ROOT / "reckon_real_estate" / "doctype"
    release_4 = {
        "land_parcel": ("Land Parcel", True),
        "land_owner": ("Land Owner", False),
        "jv_agreement": ("JV Agreement", True),
        "jv_allocation": ("JV Allocation", True),
        "handover": ("Handover", True),
        "snag": ("Snag", False),
        "warranty": ("Warranty", True),
        "service_request": ("Service Request", False),
        "maintenance": ("Maintenance", True),
    }
    for folder, (doctype, is_submittable) in release_4.items():
        meta = json.loads((base / folder / f"{folder}.json").read_text(encoding="utf-8"))
        assert meta["name"] == doctype
        assert bool(meta.get("is_submittable")) is is_submittable
        assert (base / folder / f"{folder}.py").exists()

    unit = json.loads((base / "real_estate_unit" / "real_estate_unit.json").read_text(encoding="utf-8"))
    unit_fields = {field["fieldname"]: field for field in unit["fields"]}
    assert unit_fields["land_parcel"]["options"] == "Land Parcel"
    assert unit_fields["proportionate_land_area"]["read_only"] == 1
    assert unit_fields["land_share_percent"]["read_only"] == 1
    assert unit_fields["jv_allocation"]["options"] == "JV Allocation"


def test_release_4_doctypes_are_installed_and_linked_from_workspace():
    install = (ROOT / "setup" / "install.py").read_text(encoding="utf-8")
    workspace = json.loads(
        (ROOT / "reckon_real_estate" / "workspace" / "real_estate" / "real_estate.json").read_text(encoding="utf-8")
    )
    workspace_doctypes = {
        row.get("link_to") for row in workspace["links"] if row.get("link_type") == "DocType"
    }
    for doctype in (
        "Land Parcel", "Land Owner", "JV Agreement", "JV Allocation", "Handover",
        "Snag", "Warranty", "Service Request", "Maintenance",
    ):
        assert f'"{doctype}"' in install
        assert doctype in workspace_doctypes
