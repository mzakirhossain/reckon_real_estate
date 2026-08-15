import frappe


def sync_payment_entry(doc, method=None):
    if doc.meta.has_field("collection_entry") and doc.collection_entry:
        status = "Posted" if doc.docstatus == 1 else "Cancelled" if doc.docstatus == 2 else "Draft Payment"
        frappe.db.set_value("Collection Entry", doc.collection_entry, "accounting_status", status)

    for row in doc.references:
        if row.reference_doctype != "Purchase Invoice":
            continue
        running_bill = frappe.db.get_value("Running Bill", {"purchase_invoice": row.reference_name}, "name")
        if running_bill:
            frappe.db.set_value("Running Bill", running_bill, "accounting_status", "Paid" if doc.docstatus == 1 else "Invoiced")


def sync_purchase_invoice(doc, method=None):
    running_bill = None
    if doc.meta.has_field("running_bill"):
        running_bill = doc.running_bill
    running_bill = running_bill or frappe.db.get_value("Running Bill", {"purchase_invoice": doc.name}, "name")
    if running_bill:
        status = "Invoiced" if doc.docstatus == 1 else "Cancelled"
        frappe.db.set_value("Running Bill", running_bill, "accounting_status", status)
