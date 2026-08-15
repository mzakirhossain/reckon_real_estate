import frappe
from frappe.model.document import Document

class RealEstateFloor(Document):
    def validate(self):
        if self.building:
            building_project = frappe.db.get_value("Real Estate Building", self.building, "project")
            if building_project != self.project:
                frappe.throw("Building must belong to the selected Project.")
