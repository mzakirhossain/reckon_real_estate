import frappe
from frappe.utils import date_diff, flt, getdate, today


def execute(filters=None):
    filters = frappe._dict(filters or {})
    as_of_date = getdate(filters.as_of_date or today())
    conditions = ["p.docstatus = 1"]
    values = {"as_of_date": as_of_date}

    for fieldname in ("customer", "project", "unit"):
        if filters.get(fieldname):
            conditions.append(f"p.{fieldname} = %({fieldname})s")
            values[fieldname] = filters[fieldname]
    if filters.from_due_date:
        conditions.append("s.due_date >= %(from_due_date)s")
        values["from_due_date"] = filters.from_due_date
    if filters.to_due_date:
        conditions.append("s.due_date <= %(to_due_date)s")
        values["to_due_date"] = filters.to_due_date
    if filters.get("only_outstanding", 1):
        conditions.append("s.outstanding > 0.01")

    rows = frappe.db.sql(f"""select
            p.customer, p.project, p.unit, p.booking, p.name as installment_plan,
            p.sales_invoice, s.installment_no, s.due_date, s.description,
            s.total_amount, s.paid_amount, s.outstanding, s.status
        from `tabInstallment Schedule` s
        join `tabInstallment Plan` p on p.name = s.parent
        where {' and '.join(conditions)}
        order by p.customer, s.due_date, p.name, s.installment_no""", values, as_dict=True)

    buckets = {"Current / Future": 0, "1-30 Days": 0, "31-60 Days": 0, "61-90 Days": 0, "Over 90 Days": 0}
    for row in rows:
        overdue_days = max(date_diff(as_of_date, row.due_date), 0)
        row.days_overdue = overdue_days
        row.aging_bucket = _aging_bucket(overdue_days)
        row.due_status = "Upcoming" if getdate(row.due_date) > as_of_date else "Due" if overdue_days == 0 else "Overdue"
        buckets[row.aging_bucket] += flt(row.outstanding)

    columns = [
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 170},
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Real Estate Project", "width": 145},
        {"label": "Unit", "fieldname": "unit", "fieldtype": "Link", "options": "Real Estate Unit", "width": 125},
        {"label": "Plan", "fieldname": "installment_plan", "fieldtype": "Link", "options": "Installment Plan", "width": 145},
        {"label": "Installment", "fieldname": "installment_no", "fieldtype": "Int", "width": 85},
        {"label": "Due Date", "fieldname": "due_date", "fieldtype": "Date", "width": 105},
        {"label": "Due Status", "fieldname": "due_status", "fieldtype": "Data", "width": 90},
        {"label": "Amount", "fieldname": "total_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Collected", "fieldname": "paid_amount", "fieldtype": "Currency", "width": 120},
        {"label": "Outstanding", "fieldname": "outstanding", "fieldtype": "Currency", "width": 125},
        {"label": "Days Overdue", "fieldname": "days_overdue", "fieldtype": "Int", "width": 100},
        {"label": "Aging Bucket", "fieldname": "aging_bucket", "fieldtype": "Data", "width": 125},
        {"label": "Sales Invoice", "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 145},
    ]
    chart = {
        "data": {"labels": list(buckets), "datasets": [{"name": "Outstanding", "values": list(buckets.values())}]},
        "type": "bar",
    }
    summary = [
        {"label": label, "value": value, "datatype": "Currency"}
        for label, value in buckets.items()
    ]
    return columns, rows, None, chart, summary


def _aging_bucket(days):
    if days <= 0:
        return "Current / Future"
    if days <= 30:
        return "1-30 Days"
    if days <= 60:
        return "31-60 Days"
    if days <= 90:
        return "61-90 Days"
    return "Over 90 Days"
