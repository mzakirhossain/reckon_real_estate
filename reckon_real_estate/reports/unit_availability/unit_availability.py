import frappe

def execute(filters=None):
    columns = [
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Real Estate Project", "width": 180},
        {"label": "Unit", "fieldname": "unit", "fieldtype": "Link", "options": "Real Estate Unit", "width": 130},
        {"label": "Building", "fieldname": "building", "fieldtype": "Link", "options": "Real Estate Building", "width": 140},
        {"label": "Floor", "fieldname": "floor", "fieldtype": "Link", "options": "Real Estate Floor", "width": 120},
        {"label": "Area", "fieldname": "area_sqft", "fieldtype": "Float", "width": 100},
        {"label": "List Price", "fieldname": "list_price", "fieldtype": "Currency", "width": 130},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
    ]
    filters = filters or {}
    conditions = {}
    if filters.get("project"):
        conditions["project"] = filters["project"]
    if filters.get("status"):
        conditions["status"] = filters["status"]
    data = frappe.get_all("Real Estate Unit", filters=conditions,
        fields=["project","name as unit","building","floor","area_sqft","list_price","status"],
        order_by="project, unit")
    return columns, data
