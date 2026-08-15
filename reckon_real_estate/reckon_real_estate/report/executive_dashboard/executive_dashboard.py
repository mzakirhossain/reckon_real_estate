import frappe
from frappe.utils import flt, today


def execute(filters=None):
    filters=frappe._dict(filters or {})
    projects=frappe.get_all("Real Estate Project",filters={"name":filters.project} if filters.project else {},pluck="name")
    columns=[
        {"label":"Project","fieldname":"project","fieldtype":"Link","options":"Real Estate Project","width":170},
        {"label":"Sales","fieldname":"sales","fieldtype":"Currency","width":125},
        {"label":"Collected","fieldname":"collected","fieldtype":"Currency","width":125},
        {"label":"Receivable","fieldname":"receivable","fieldtype":"Currency","width":125},
        {"label":"Construction Cost","fieldname":"cost","fieldtype":"Currency","width":140},
        {"label":"Gross Profit","fieldname":"profit","fieldtype":"Currency","width":125},
        {"label":"Collection Forecast","fieldname":"collection_forecast","fieldtype":"Currency","width":150},
        {"label":"Commission Payable","fieldname":"commission","fieldtype":"Currency","width":145},
    ]
    data=[]
    for project in projects:
        sales=flt(frappe.db.get_value("Property Booking",{"project":project,"docstatus":["!=",2]},"sum(net_contract_value)") or 0)
        collected=flt(frappe.db.get_value("Collection Entry",{"project":project,"docstatus":1},"sum(amount)") or 0)
        cost=flt(frappe.db.get_value("Running Bill",{"project":project,"docstatus":1},"sum(gross_amount)") or 0)
        commission=flt(frappe.db.get_value("Sales Commission",{"project":project,"docstatus":1},"sum(payable_amount)") or 0)
        due=frappe.db.sql("""select coalesce(sum(i.outstanding),0) from `tabInstallment Schedule` i
            join `tabInstallment Plan` p on p.name=i.parent where p.project=%s and p.docstatus!=2
            and i.due_date<=%s""",(project,today()))[0][0]
        data.append({"project":project,"sales":sales,"collected":collected,"receivable":sales-collected,
            "cost":cost,"profit":sales-cost,"collection_forecast":due,"commission":commission})
    chart={"data":{"labels":projects,"datasets":[{"name":"Sales","values":[r["sales"] for r in data]},{"name":"Cost","values":[r["cost"] for r in data]},{"name":"Collected","values":[r["collected"] for r in data]}]},"type":"bar"}
    summary=[{"value":sum(r["sales"] for r in data),"label":"Total Sales","datatype":"Currency"},{"value":sum(r["collected"] for r in data),"label":"Collections","datatype":"Currency"},{"value":sum(r["profit"] for r in data),"label":"Gross Profit","datatype":"Currency"}]
    return columns,data,None,chart,summary

