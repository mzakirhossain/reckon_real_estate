import frappe
from frappe.utils import flt


def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = [
        {"label":"Project","fieldname":"project","fieldtype":"Link","options":"Real Estate Project","width":180},
        {"label":"ERPNext Project","fieldname":"erpnext_project","fieldtype":"Link","options":"Project","width":180},
        {"label":"Income (GL)","fieldname":"income","fieldtype":"Currency","width":140},
        {"label":"Expense / COGS (GL)","fieldname":"expense","fieldtype":"Currency","width":165},
        {"label":"Net Profit","fieldname":"profit","fieldtype":"Currency","width":140},
        {"label":"Margin %","fieldname":"margin","fieldtype":"Percent","width":105},
        {"label":"Budget","fieldname":"budget","fieldtype":"Currency","width":130},
        {"label":"Budget Variance","fieldname":"budget_variance","fieldtype":"Currency","width":145},
    ]
    project_filters = {"name": filters.project} if filters.project else {}
    data = []
    for project in frappe.get_all("Real Estate Project", filters=project_filters, fields=["name","erpnext_project"]):
        income = expense = 0
        if project.erpnext_project:
            conditions = ["gle.project=%s", "gle.is_cancelled=0", "a.root_type in ('Income','Expense')"]
            values = [project.erpnext_project]
            if filters.from_date:
                conditions.append("gle.posting_date>=%s"); values.append(filters.from_date)
            if filters.to_date:
                conditions.append("gle.posting_date<=%s"); values.append(filters.to_date)
            rows = frappe.db.sql(f"""select a.root_type, sum(gle.debit-gle.credit) amount
                from `tabGL Entry` gle join `tabAccount` a on a.name=gle.account
                where {' and '.join(conditions)} group by a.root_type""", values, as_dict=True)
            for row in rows:
                if row.root_type == "Income": income = -flt(row.amount)
                if row.root_type == "Expense": expense = flt(row.amount)
        budget = flt(frappe.db.get_value("Project Budget", {"project":project.name,"docstatus":1}, "sum(total_budget)") or 0)
        profit = income - expense
        data.append({"project":project.name,"erpnext_project":project.erpnext_project,"income":income,
            "expense":expense,"profit":profit,"margin":profit/income*100 if income else 0,
            "budget":budget,"budget_variance":budget-expense})
    return columns, data
