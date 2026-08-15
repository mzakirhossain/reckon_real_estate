import frappe
from frappe.model.document import Document

class RealEstateProject(Document):
    def validate(self):
        if self.start_date and self.expected_completion_date and self.expected_completion_date < self.start_date:
            frappe.throw("Expected Completion Date cannot be before Start Date.")
        self.total_units = frappe.db.count("Real Estate Unit", {"project": self.name, "docstatus": ["!=", 2]})
