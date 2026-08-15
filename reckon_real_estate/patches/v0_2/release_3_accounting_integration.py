import frappe


def execute():
    if frappe.db.exists("DocType", "Collection Entry"):
        for row in frappe.get_all("Collection Entry", fields=["name", "payment_entry"]):
            status = "Not Created"
            if row.payment_entry:
                docstatus = frappe.db.get_value("Payment Entry", row.payment_entry, "docstatus")
                status = {0: "Draft Payment", 1: "Posted", 2: "Cancelled"}.get(docstatus, "Not Created")
            frappe.db.set_value("Collection Entry", row.name, "accounting_status", status, update_modified=False)

    if frappe.db.exists("DocType", "Running Bill"):
        for row in frappe.get_all("Running Bill", fields=["name", "purchase_invoice"]):
            status = "Not Invoiced"
            if row.purchase_invoice:
                docstatus = frappe.db.get_value("Purchase Invoice", row.purchase_invoice, "docstatus")
                status = {0: "Draft Invoice", 1: "Invoiced", 2: "Cancelled"}.get(docstatus, "Not Invoiced")
            frappe.db.set_value("Running Bill", row.name, "accounting_status", status, update_modified=False)

    for plan in frappe.get_all("Installment Plan", fields=["name", "sales_invoice"]):
        if not plan.sales_invoice:
            continue
        frappe.db.sql(
            "update `tabInstallment Schedule` set sales_invoice=%s where parent=%s",
            (plan.sales_invoice, plan.name),
        )
