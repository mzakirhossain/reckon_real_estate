import frappe
from frappe.model.document import Document

from reckon_real_estate.construction_workflow import block_if_submitted, require_submitted, set_cancelled_status, set_draft_status, set_submitted_status

class PropertyBooking(Document):
    def validate(self):
        set_draft_status(self, "booking_no", "document_status")
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
        if self.docstatus == 1:
            require_submitted("Real Estate Unit", self.unit)

    def on_submit(self):
        frappe.db.set_value("Real Estate Unit", self.unit, "status", "Booked")
        self.db_set("status", "Active")
        set_submitted_status(self, "document_status")

    def on_cancel(self):
        block_if_submitted("Sales Agreement", {"booking": self.name}, "Submitted Sales Agreement exists")
        block_if_submitted("Installment Plan", {"booking": self.name}, "Submitted Installment Plan exists")
        frappe.db.set_value("Real Estate Unit", self.unit, "status", "Available")
        self.db_set("status", "Cancelled")
        set_cancelled_status(self, "document_status")
