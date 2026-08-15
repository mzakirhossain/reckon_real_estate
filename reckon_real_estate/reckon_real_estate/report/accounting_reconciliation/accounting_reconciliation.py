import frappe


def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = [
        {"label":"Area","fieldname":"area","fieldtype":"Data","width":115},
        {"label":"Project","fieldname":"project","fieldtype":"Link","options":"Real Estate Project","width":150},
        {"label":"Source Type","fieldname":"source_type","fieldtype":"Data","width":145},
        {"label":"Source","fieldname":"source","fieldtype":"Dynamic Link","options":"source_type","width":160},
        {"label":"ERPNext Voucher Type","fieldname":"voucher_type","fieldtype":"Data","width":160},
        {"label":"ERPNext Voucher","fieldname":"voucher","fieldtype":"Dynamic Link","options":"voucher_type","width":170},
        {"label":"Status","fieldname":"status","fieldtype":"Data","width":110},
        {"label":"Issue","fieldname":"issue","fieldtype":"Data","width":260},
    ]
    data = []
    project_filter = {"project": filters.project} if filters.project else {}
    for plan in frappe.get_all("Installment Plan", filters={**project_filter, "docstatus": 1}, fields=["name","project","sales_invoice"]):
        status = frappe.db.get_value("Sales Invoice", plan.sales_invoice, "docstatus") if plan.sales_invoice else None
        data.append({"area":"Sales","project":plan.project,"source_type":"Installment Plan","source":plan.name,
            "voucher_type":"Sales Invoice","voucher":plan.sales_invoice,"status":_status(status),
            "issue":"" if status == 1 else "Sales Invoice is missing or not submitted"})
    for collection in frappe.get_all("Collection Entry", filters={**project_filter, "docstatus": 1}, fields=["name","project","payment_entry"]):
        status = frappe.db.get_value("Payment Entry", collection.payment_entry, "docstatus") if collection.payment_entry else None
        data.append({"area":"Collection","project":collection.project,"source_type":"Collection Entry","source":collection.name,
            "voucher_type":"Payment Entry","voucher":collection.payment_entry,"status":_status(status),
            "issue":"" if status == 1 else "Payment Entry is missing or not submitted"})
    for work_order in frappe.get_all("Contractor Work Order", filters={**project_filter, "docstatus": 1}, fields=["name","project","purchase_order"]):
        status = frappe.db.get_value("Purchase Order", work_order.purchase_order, "docstatus") if work_order.purchase_order else None
        data.append({"area":"Procurement","project":work_order.project,"source_type":"Contractor Work Order","source":work_order.name,
            "voucher_type":"Purchase Order","voucher":work_order.purchase_order,"status":_status(status),
            "issue":"" if status == 1 else "Purchase Order is missing or not submitted"})
    for bill in frappe.get_all("Running Bill", filters={**project_filter, "docstatus": 1}, fields=["name","project","purchase_invoice"]):
        status = frappe.db.get_value("Purchase Invoice", bill.purchase_invoice, "docstatus") if bill.purchase_invoice else None
        data.append({"area":"Payable","project":bill.project,"source_type":"Running Bill","source":bill.name,
            "voucher_type":"Purchase Invoice","voucher":bill.purchase_invoice,"status":_status(status),
            "issue":"" if status == 1 else "Purchase Invoice is missing or not submitted"})
    return columns, data


def _status(docstatus):
    return {0:"Draft",1:"Submitted",2:"Cancelled"}.get(docstatus, "Missing")

