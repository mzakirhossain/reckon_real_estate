import frappe

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label":"Date","fieldname":"date","fieldtype":"Date","width":110},
        {"label":"Customer","fieldname":"customer","fieldtype":"Link","options":"Customer","width":150},
        {"label":"Project","fieldname":"project","fieldtype":"Link","options":"Real Estate Project","width":150},
        {"label":"Unit","fieldname":"unit","fieldtype":"Link","options":"Real Estate Unit","width":120},
        {"label":"Type","fieldname":"transaction_type","fieldtype":"Data","width":120},
        {"label":"Reference","fieldname":"reference","fieldtype":"Dynamic Link","options":"reference_doctype","width":160},
        {"label":"Debit","fieldname":"debit","fieldtype":"Currency","width":120},
        {"label":"Credit","fieldname":"credit","fieldtype":"Currency","width":120},
    ]
    data = []
    if filters.get("customer"):
        bookings = frappe.get_all("Property Booking",
            filters={"customer": filters["customer"], "docstatus": ["!=",2]},
            fields=["name","customer","project","unit","booking_date","net_contract_value"])
        for b in bookings:
            data.append({
                "date": b.booking_date, "customer": b.customer, "project": b.project, "unit": b.unit,
                "transaction_type": "Booking", "reference": b.name, "reference_doctype": "Property Booking",
                "debit": b.net_contract_value, "credit": 0
            })
        cols = frappe.get_all("Collection Entry",
            filters={"customer": filters["customer"], "docstatus": 1},
            fields=["name","customer","project","unit","collection_date","amount"])
        for c in cols:
            data.append({
                "date": c.collection_date, "customer": c.customer, "project": c.project, "unit": c.unit,
                "transaction_type": "Collection", "reference": c.name, "reference_doctype": "Collection Entry",
                "debit": 0, "credit": c.amount
            })
    data.sort(key=lambda x: str(x.get("date") or ""))
    return columns, data
