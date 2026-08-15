import frappe
from frappe.model.document import Document

from reckon_real_estate.construction_workflow import block_if_submitted, require_submitted, set_cancelled_status, set_draft_status, set_submitted_status

class RealEstateBuilding(Document):
    def validate(self):
        set_draft_status(self, "building_code", "document_status")
        if self.project and not frappe.db.exists("Real Estate Project", self.project):
            frappe.throw("Selected Project does not exist.")
        if self.docstatus == 1:
            require_submitted("Real Estate Project", self.project)

    def on_submit(self):
        set_submitted_status(self, "document_status")

    def on_cancel(self):
        block_if_submitted("Real Estate Floor", {"building": self.name}, "Submitted Floor exists")
        set_cancelled_status(self, "document_status")
