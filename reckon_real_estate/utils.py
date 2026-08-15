import frappe
from frappe.utils import getdate, today

def money(value):
    return frappe.utils.flt(value, 2)

def ensure_customer(customer):
    if customer and not frappe.db.exists("Customer", customer):
        frappe.throw(f"Customer {customer} does not exist.")

def validate_date_not_before(value, reference, label):
    if value and reference and getdate(value) < getdate(reference):
        frappe.throw(f"{label} cannot be before {reference}.")
