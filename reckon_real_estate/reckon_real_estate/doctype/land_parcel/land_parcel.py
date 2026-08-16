import frappe
from frappe.model.document import Document
from frappe.utils import flt

from reckon_real_estate.construction_workflow import block_if_submitted, require_submitted, set_cancelled_status, set_draft_status, set_submitted_status


class LandParcel(Document):
    def validate(self):
        set_draft_status(self, "parcel_no", "document_status")
        if flt(self.total_land_area) <= 0:
            frappe.throw("Total Land Area must be greater than zero.")
        if self.docstatus == 1:
            require_submitted("Real Estate Project", self.project)

    def on_submit(self):
        set_submitted_status(self)
        self.db_set("document_status", "Submitted")

    def on_cancel(self):
        block_if_submitted("JV Agreement", {"land_parcel": self.name}, "Submitted JV Agreement exists")
        set_cancelled_status(self)
        self.db_set("document_status", "Cancelled")
