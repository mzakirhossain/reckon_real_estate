import frappe
from frappe.model.document import Document


class Contractor(Document):
    def validate(self):
        if frappe.db.get_value("Supplier", self.supplier, "disabled"):
            frappe.throw("The linked Supplier is disabled.")

