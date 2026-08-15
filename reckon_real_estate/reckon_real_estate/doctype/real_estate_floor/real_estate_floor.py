import frappe
from frappe.model.document import Document

from reckon_real_estate.construction_workflow import block_if_submitted, require_submitted, set_cancelled_status, set_draft_status, set_submitted_status

class RealEstateFloor(Document):
    def validate(self):
        set_draft_status(self, "floor_code", "document_status")
        if self.building:
            building_project = frappe.db.get_value("Real Estate Building", self.building, "project")
            if building_project != self.project:
                frappe.throw("Building must belong to the selected Project.")
        if self.docstatus == 1:
            require_submitted("Real Estate Building", self.building)

    def on_submit(self):
        set_submitted_status(self, "document_status")

    def on_cancel(self):
        block_if_submitted("Real Estate Unit", {"floor": self.name}, "Submitted Unit exists")
        set_cancelled_status(self, "document_status")
