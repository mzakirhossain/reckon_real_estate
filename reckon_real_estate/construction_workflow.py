import frappe


def set_draft_status(doc, number_field, status_field="status"):
    """Expose the autoname as a read-only business number and keep Draft status."""
    setattr(doc, number_field, doc.name)
    if doc.docstatus == 0:
        setattr(doc, status_field, "Draft")


def set_submitted_status(doc, status_field="status"):
    doc.db_set(status_field, "Submitted")


def set_cancelled_status(doc, status_field="status"):
    doc.db_set(status_field, "Cancelled")


def require_submitted(doctype, name, label=None):
    if name and frappe.db.get_value(doctype, name, "docstatus") != 1:
        frappe.throw(f"{label or doctype} must be submitted first.")


def block_if_submitted(doctype, filters, message):
    filters = dict(filters, docstatus=1)
    dependent = frappe.db.exists(doctype, filters)
    if dependent:
        frappe.throw(f"{message}: {dependent}. Cancel it first.")
