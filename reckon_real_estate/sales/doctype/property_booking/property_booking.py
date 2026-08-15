import frappe
from frappe.model.document import Document

class PropertyBooking(Document):
    def validate(self):
        self.net_contract_value = frappe.utils.flt(self.contract_value) - frappe.utils.flt(self.discount)
        if self.net_contract_value < 0:
            frappe.throw("Discount cannot exceed Contract Value.")
        if not frappe.db.exists("Customer", self.customer):
            frappe.throw("Customer does not exist.")
        unit = frappe.get_doc("Real Estate Unit", self.unit)
        if unit.project != self.project:
            frappe.throw("Unit must belong to the selected Project.")
        if self.is_new():
            active = frappe.db.exists("Property Booking", {
                "unit": self.unit,
                "status": ["in", ["Reserved", "Confirmed", "Agreement Signed", "Active"]],
                "docstatus": ["!=", 2],
            })
            if active:
                frappe.throw(f"Unit {self.unit} already has an active booking: {active}")

    def on_submit(self):
        frappe.db.set_value("Real Estate Unit", self.unit, "status", "Booked")

    def on_cancel(self):
        frappe.db.set_value("Real Estate Unit", self.unit, "status", "Available")
