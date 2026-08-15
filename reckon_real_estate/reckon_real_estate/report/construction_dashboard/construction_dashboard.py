import frappe
from frappe.utils import flt


def execute(filters=None):
    filters = frappe._dict(filters or {})
    projects = frappe.get_all("Real Estate Project", filters={"name": filters.project} if filters.project else {}, fields=["name"])
    columns = [
        {"label":"Project","fieldname":"project","fieldtype":"Link","options":"Real Estate Project","width":180},
        {"label":"BOQ","fieldname":"boq","fieldtype":"Currency","width":120},
        {"label":"Budget","fieldname":"budget","fieldtype":"Currency","width":120},
        {"label":"Work Orders","fieldname":"work_orders","fieldtype":"Currency","width":120},
        {"label":"Measured","fieldname":"measured","fieldtype":"Currency","width":120},
        {"label":"Billed","fieldname":"billed","fieldtype":"Currency","width":120},
        {"label":"Progress %","fieldname":"progress","fieldtype":"Percent","width":100},
        {"label":"Forecast","fieldname":"forecast","fieldtype":"Currency","width":130},
    ]
    data=[]
    for project in projects:
        def total(dt, field):
            return flt(frappe.db.get_value(dt,{"project":project.name,"docstatus":1},f"sum({field})") or 0)
        boq, budget = total("BOQ","total_amount"), total("Project Budget","total_budget")
        orders, measured, billed = total("Contractor Work Order","total_amount"), total("Measurement Sheet","total_amount"), total("Running Bill","gross_amount")
        progress = measured/orders*100 if orders else 0
        forecast = billed/(progress/100) if progress else max(boq,budget,orders)
        data.append({"project":project.name,"boq":boq,"budget":budget,"work_orders":orders,
            "measured":measured,"billed":billed,"progress":progress,"forecast":forecast})
    chart={"data":{"labels":[r["project"] for r in data],"datasets":[{"name":"Budget","values":[r["budget"] for r in data]},{"name":"Billed","values":[r["billed"] for r in data]},{"name":"Forecast","values":[r["forecast"] for r in data]}]},"type":"bar"}
    return columns,data,None,chart

