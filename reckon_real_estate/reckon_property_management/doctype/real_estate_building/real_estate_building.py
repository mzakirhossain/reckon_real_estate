import frappe
from frappe.model.document import Document

class RealEstateBuilding(Document):
    def validate(self):
        if self.project and not frappe.db.exists("Real Estate Project", self.project):
            frappe.throw("Selected Project does not exist.")
