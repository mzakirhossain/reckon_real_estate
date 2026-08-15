import frappe
from frappe.utils import getdate, today, date_diff

def execute(filters=None):
    columns = [
        {"label": "Plan", "fieldname": "plan", "fieldtype": "Link", "options": "Installment Plan", "width": 150},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 160},
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Real Estate Project", "width": 150},
        {"label": "Unit", "fieldname": "unit", "fieldtype": "Link", "options": "Real Estate Unit", "width": 120},
        {"label": "Installment", "fieldname": "installment_no", "fieldtype": "Int", "width": 90},
        {"label": "Due Date", "fieldname": "due_date", "fieldtype": "Date", "width": 110},
        {"label": "Amount", "fieldname": "total_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Paid", "fieldname": "paid_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Outstanding", "fieldname": "outstanding", "fieldtype": "Currency", "width": 120},
        {"label": "Days Overdue", "fieldname": "days_overdue", "fieldtype": "Int", "width": 110},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
    ]
    data = []
    plans = frappe.get_all("Installment Plan", filters={"docstatus": ["!=", 2]}, fields=["name","customer","project","unit"])
    for p in plans:
        doc = frappe.get_doc("Installment Plan", p.name)
        for r in doc.installments:
            if r.outstanding > 0 and r.due_date and getdate(r.due_date) < getdate(today()):
                if filters and filters.get("project") and p.project != filters["project"]:
                    continue
                data.append({
                    "plan": p.name, "customer": p.customer, "project": p.project, "unit": p.unit,
                    "installment_no": r.installment_no, "due_date": r.due_date,
                    "total_amount": r.total_amount, "paid_amount": r.paid_amount,
                    "outstanding": r.outstanding, "days_overdue": date_diff(today(), r.due_date),
                    "status": "Overdue"
                })
    return columns, data
