import frappe
from frappe.utils import flt


def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = [
        {"label":"Project","fieldname":"project","fieldtype":"Link","options":"Real Estate Project","width":170},
        {"label":"Account","fieldname":"account","fieldtype":"Link","options":"Account","width":200},
        {"label":"Budget","fieldname":"budget","fieldtype":"Currency","width":130},
        {"label":"Committed","fieldname":"committed","fieldtype":"Currency","width":130},
        {"label":"Actual","fieldname":"actual","fieldtype":"Currency","width":130},
        {"label":"Variance","fieldname":"variance","fieldtype":"Currency","width":130},
        {"label":"Used %","fieldname":"used_percent","fieldtype":"Percent","width":100},
    ]
    query_filters = {"docstatus": 1}
    if filters.project:
        query_filters["project"] = filters.project
    rows = []
    for budget in frappe.get_all("Project Budget", filters=query_filters, fields=["name","project","from_date","to_date"]):
        erp_project = frappe.db.get_value("Real Estate Project", budget.project, "erpnext_project")
        for item in frappe.get_all("Project Budget Item", filters={"parent":budget.name}, fields=["account","budget_amount"]):
            actual = 0
            if erp_project:
                actual = frappe.db.sql("""select coalesce(sum(debit-credit),0) from `tabGL Entry`
                    where project=%s and account=%s and posting_date between %s and %s and is_cancelled=0""",
                    (erp_project, item.account, budget.from_date, budget.to_date))[0][0]
            committed = 0
            if erp_project:
                committed = frappe.db.sql("""select coalesce(sum(poi.base_amount),0) from `tabPurchase Order Item` poi
                    join `tabPurchase Order` po on po.name=poi.parent where po.docstatus=1 and po.status not in ('Closed','Completed')
                    and poi.project=%s and poi.expense_account=%s""", (erp_project, item.account))[0][0]
            used = flt(actual) + flt(committed)
            rows.append({"project":budget.project,"account":item.account,"budget":item.budget_amount,
                "committed":committed,"actual":actual,"variance":flt(item.budget_amount)-used,
                "used_percent":used/flt(item.budget_amount)*100 if flt(item.budget_amount) else 0})
    return columns, rows

