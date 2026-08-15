import frappe


NUMBER_FIELDS = {
    "Real Estate Project": "project_code",
    "Real Estate Building": "building_code",
    "Real Estate Floor": "floor_code",
    "Real Estate Unit": "unit_code",
    "Property Booking": "booking_no",
    "Installment Plan": "plan_no",
    "Collection Entry": "collection_no",
}


def execute():
    statuses = {0: "Draft", 1: "Submitted", 2: "Cancelled"}
    for doctype, number_field in NUMBER_FIELDS.items():
        if not frappe.db.exists("DocType", doctype):
            continue
        for row in frappe.get_all(doctype, fields=["name", "docstatus"]):
            frappe.db.set_value(
                doctype,
                row.name,
                {number_field: row.name, "document_status": statuses[row.docstatus]},
                update_modified=False,
            )
