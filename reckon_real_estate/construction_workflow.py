import frappe


def set_draft_status(doc, number_field):
    """Expose the autoname as a read-only business number and keep Draft status."""
    setattr(doc, number_field, doc.name)
    if doc.docstatus == 0:
        doc.status = "Draft"


def set_submitted_status(doc):
    doc.db_set("status", "Submitted")


def set_cancelled_status(doc):
    doc.db_set("status", "Cancelled")


def block_if_submitted(doctype, filters, message):
    filters = dict(filters, docstatus=1)
    dependent = frappe.db.exists(doctype, filters)
    if dependent:
        frappe.throw(f"{message}: {dependent}. Cancel it first.")

