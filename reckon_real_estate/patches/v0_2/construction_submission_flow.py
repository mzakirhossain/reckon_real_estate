import frappe


NUMBER_FIELDS = {
    "BOQ": "boq_no",
    "Project Budget": "budget_no",
    "Contractor": "contractor_no",
    "Contractor Work Order": "work_order_no",
    "Measurement Sheet": "measurement_no",
    "Running Bill": "running_bill_no",
}

def execute():
    # BOQ revisions now use Frappe's standard Cancel and Amend workflow.
    if frappe.db.exists("DocType", "BOQ Revision"):
        frappe.delete_doc("DocType", "BOQ Revision", force=True, ignore_permissions=True)

    statuses = {0: "Draft", 1: "Submitted", 2: "Cancelled"}
    for doctype, number_field in NUMBER_FIELDS.items():
        if not frappe.db.exists("DocType", doctype):
            continue
        for row in frappe.get_all(doctype, fields=["name", "docstatus"]):
            frappe.db.set_value(
                doctype,
                row.name,
                {number_field: row.name, "status": statuses[row.docstatus]},
                update_modified=False,
            )
