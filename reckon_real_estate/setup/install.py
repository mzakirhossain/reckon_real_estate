"""Frappe/ERPNext installation checks for supported platform versions."""

from importlib import import_module
import json

import frappe


SUPPORTED_MAJOR_VERSIONS = {"15", "16"}
REQUIRED_DOCTYPES = (
    "Real Estate Project",
    "Real Estate Building",
    "Real Estate Floor",
    "Real Estate Unit",
    "Property Booking",
    "Installment Plan",
    "Installment Schedule",
    "Collection Entry",
    "Payment Allocation",
    "BOQ",
    "Contractor",
    "Contractor Work Order",
    "Measurement Sheet",
    "Running Bill",
    "Project Budget",
    "Sales Target",
    "Sales Commission",
    "Sales Agreement",
)
ERPNext_MASTER_DOCTYPES = (
    "Customer",
    "Company",
    "Project",
    "Cost Center",
    "Item",
    "Supplier",
    "Purchase Order",
    "Purchase Invoice",
    "Payment Entry",
    "Sales Invoice",
    "Material Request",
    "Purchase Receipt",
    "Stock Entry",
    "Journal Entry",
    "Budget",
)
LEGACY_MODULES = (
    "Reckon Property Management",
    "Reckon Sales",
    "Reckon Collection",
    "Reckon Reports",
)


def _major_version(app_name):
    """Return an app's major version without adding a packaging dependency."""
    version = getattr(import_module(app_name), "__version__", "")
    major = str(version).split(".", 1)[0]
    if not major.isdigit():
        frappe.throw(f"Could not determine the {app_name.title()} version: {version!r}.")
    return major


def validate_supported_stack():
    """Require matching Frappe and ERPNext v15 or v16 installations."""
    frappe_major = _major_version("frappe")
    erpnext_major = _major_version("erpnext")

    if frappe_major not in SUPPORTED_MAJOR_VERSIONS:
        frappe.throw("Reckon Real Estate supports Frappe v15 and v16 only.")
    if erpnext_major not in SUPPORTED_MAJOR_VERSIONS:
        frappe.throw("Reckon Real Estate supports ERPNext v15 and v16 only.")
    if frappe_major != erpnext_major:
        frappe.throw(
            "Frappe and ERPNext must use the same major version "
            f"(found Frappe v{frappe_major}, ERPNext v{erpnext_major})."
        )

    return {"frappe": frappe_major, "erpnext": erpnext_major}


def before_install():
    """Stop a site installation early if its framework stack is unsupported."""
    validate_supported_stack()


def after_install():
    """Confirm that app schema sync created every Release 1 DocType."""
    cleanup_legacy_modules()
    ensure_erpnext_custom_fields()
    ensure_home_analytics()
    validate_installation()


def after_migrate():
    """Recheck the schema after an app update or framework migration."""
    cleanup_legacy_modules()
    ensure_erpnext_custom_fields()
    ensure_home_analytics()
    validate_installation()


def ensure_home_analytics():
    """Create the native, permission-aware cards and charts used by the workspace."""
    def submitted(doctype):
        return json.dumps([[doctype, "docstatus", "=", 1, False]])
    real_estate_invoices = json.dumps(
        [
            ["Sales Invoice", "docstatus", "=", 1, False],
            ["Sales Invoice", "real_estate_booking", "is", "set", False],
        ]
    )

    number_cards = (
        {
            "label": "Total Booked Sales",
            "document_type": "Property Booking",
            "aggregate_function_based_on": "net_contract_value",
            "filters_json": submitted("Property Booking"),
            "color": "#2490EF",
        },
        {
            "label": "Total Collections",
            "document_type": "Collection Entry",
            "aggregate_function_based_on": "amount",
            "filters_json": submitted("Collection Entry"),
            "color": "#29CD42",
        },
        {
            "label": "Outstanding Receivables",
            "document_type": "Sales Invoice",
            "aggregate_function_based_on": "outstanding_amount",
            "filters_json": real_estate_invoices,
            "color": "#EC864B",
        },
    )
    for values in number_cards:
        _upsert_analytics_doc(
            "Number Card",
            values["label"],
            {
                **values,
                "type": "Document Type",
                "function": "Sum",
                "is_public": 1,
                "is_standard": 0,
                "show_percentage_stats": 1,
                "stats_time_interval": "Monthly",
                "dynamic_filters_json": "[]",
            },
        )

    charts = (
        {
            "chart_name": "Monthly Booked Sales",
            "document_type": "Property Booking",
            "based_on": "booking_date",
            "value_based_on": "net_contract_value",
            "filters_json": submitted("Property Booking"),
            "color": "#2490EF",
        },
        {
            "chart_name": "Monthly Collections",
            "document_type": "Collection Entry",
            "based_on": "collection_date",
            "value_based_on": "amount",
            "filters_json": submitted("Collection Entry"),
            "color": "#29CD42",
        },
    )
    for values in charts:
        _upsert_analytics_doc(
            "Dashboard Chart",
            values["chart_name"],
            {
                **values,
                "chart_type": "Sum",
                "timeseries": 1,
                "timespan": "Last Year",
                "time_interval": "Monthly",
                "type": "Line",
                "is_public": 1,
                "is_standard": 0,
                "show_values_over_chart": 1,
                "dynamic_filters_json": "[]",
            },
        )


def _upsert_analytics_doc(doctype, name, values):
    """Keep an app-owned analytics definition current across migrations."""
    if frappe.db.exists(doctype, name):
        doc = frappe.get_doc(doctype, name)
        doc.update(values)
        doc.flags.ignore_permissions = True
        doc.save()
        return

    frappe.get_doc({"doctype": doctype, **values}).insert(ignore_permissions=True)


def ensure_erpnext_custom_fields():
    """Add traceability links without replacing ERPNext accounting/stock DocTypes."""
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

    common = {"read_only": 1, "no_copy": 0}
    custom_fields = {
        "Sales Invoice": [
            {**common, "fieldname": "sales_agreement", "label": "Sales Agreement", "fieldtype": "Link", "options": "Sales Agreement"},
            {**common, "fieldname": "installment_plan", "label": "Installment Plan", "fieldtype": "Link", "options": "Installment Plan"},
            {**common, "fieldname": "real_estate_booking", "label": "Property Booking", "fieldtype": "Link", "options": "Property Booking"},
            {**common, "fieldname": "real_estate_unit", "label": "Real Estate Unit", "fieldtype": "Link", "options": "Real Estate Unit"},
            {**common, "fieldname": "real_estate_project", "label": "Real Estate Project", "fieldtype": "Link", "options": "Real Estate Project"},
        ],
        "Payment Entry": [
            {**common, "fieldname": "collection_entry", "label": "Collection Entry", "fieldtype": "Link", "options": "Collection Entry"},
            {**common, "fieldname": "real_estate_booking", "label": "Property Booking", "fieldtype": "Link", "options": "Property Booking"},
            {**common, "fieldname": "real_estate_unit", "label": "Real Estate Unit", "fieldtype": "Link", "options": "Real Estate Unit"},
            {**common, "fieldname": "real_estate_project", "label": "Real Estate Project", "fieldtype": "Link", "options": "Real Estate Project"},
        ],
        "Purchase Order": [
            {**common, "fieldname": "contractor_work_order", "label": "Contractor Work Order", "fieldtype": "Link", "options": "Contractor Work Order"},
            {**common, "fieldname": "real_estate_project", "label": "Real Estate Project", "fieldtype": "Link", "options": "Real Estate Project"},
            {**common, "fieldname": "boq", "label": "BOQ", "fieldtype": "Link", "options": "BOQ"},
        ],
        "Purchase Invoice": [
            {**common, "fieldname": "running_bill", "label": "Running Bill", "fieldtype": "Link", "options": "Running Bill"},
            {**common, "fieldname": "contractor_work_order", "label": "Contractor Work Order", "fieldtype": "Link", "options": "Contractor Work Order"},
            {**common, "fieldname": "real_estate_project", "label": "Real Estate Project", "fieldtype": "Link", "options": "Real Estate Project"},
            {**common, "fieldname": "boq", "label": "BOQ", "fieldtype": "Link", "options": "BOQ"},
        ],
        "Stock Entry": [
            {**common, "fieldname": "real_estate_project", "label": "Real Estate Project", "fieldtype": "Link", "options": "Real Estate Project"},
            {**common, "fieldname": "contractor_work_order", "label": "Contractor Work Order", "fieldtype": "Link", "options": "Contractor Work Order"},
            {**common, "fieldname": "boq", "label": "BOQ", "fieldtype": "Link", "options": "BOQ"},
        ],
        "Material Request": [
            {**common, "fieldname": "real_estate_project", "label": "Real Estate Project", "fieldtype": "Link", "options": "Real Estate Project"},
            {**common, "fieldname": "boq", "label": "BOQ", "fieldtype": "Link", "options": "BOQ"},
        ],
        "Purchase Receipt": [
            {**common, "fieldname": "real_estate_project", "label": "Real Estate Project", "fieldtype": "Link", "options": "Real Estate Project"},
            {**common, "fieldname": "contractor_work_order", "label": "Contractor Work Order", "fieldtype": "Link", "options": "Contractor Work Order"},
            {**common, "fieldname": "boq", "label": "BOQ", "fieldtype": "Link", "options": "BOQ"},
        ],
        "Journal Entry": [
            {**common, "fieldname": "real_estate_project", "label": "Real Estate Project", "fieldtype": "Link", "options": "Real Estate Project"},
            {**common, "fieldname": "real_estate_booking", "label": "Property Booking", "fieldtype": "Link", "options": "Property Booking"},
            {**common, "fieldname": "real_estate_unit", "label": "Real Estate Unit", "fieldtype": "Link", "options": "Real Estate Unit"},
        ],
    }
    create_custom_fields(custom_fields, update=True)


def cleanup_legacy_modules():
    """Remove empty module definitions created by pre-consolidation releases."""
    for module in LEGACY_MODULES:
        if frappe.db.get_value("Module Def", module, "app_name") != "reckon_real_estate":
            continue
        if frappe.db.exists("DocType", {"module": module}):
            continue
        frappe.delete_doc("Module Def", module, force=True, ignore_permissions=True)


def validate_installation():
    """Verify custom schema and the ERPNext masters linked by this app."""
    stack = validate_supported_stack()
    missing = [doctype for doctype in REQUIRED_DOCTYPES if not frappe.db.exists("DocType", doctype)]
    if missing:
        frappe.throw(
            "Reckon Real Estate schema is incomplete. Run `bench --site <site> migrate`. "
            f"Missing DocTypes: {', '.join(missing)}"
        )
    missing_erpnext = [
        doctype for doctype in ERPNext_MASTER_DOCTYPES if not frappe.db.exists("DocType", doctype)
    ]
    if missing_erpnext:
        frappe.throw(
            "The required ERPNext master DocTypes are unavailable. "
            f"Missing: {', '.join(missing_erpnext)}"
        )
    return stack
