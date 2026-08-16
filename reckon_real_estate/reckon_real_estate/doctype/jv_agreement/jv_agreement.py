import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate

from reckon_real_estate.construction_workflow import block_if_submitted, require_submitted, set_cancelled_status, set_draft_status, set_submitted_status


class JVAgreement(Document):
    def validate(self):
        set_draft_status(self, "agreement_no", "document_status")
        parcel = frappe.get_doc("Land Parcel", self.land_parcel)
        self.project = parcel.project
        if abs(flt(self.developer_share_percent) + flt(self.owner_share_percent) - 100) > 0.001:
            frappe.throw("Developer Share and Owner Share must total 100%.")
        if self.expiry_date and self.effective_from and getdate(self.expiry_date) < getdate(self.effective_from):
            frappe.throw("Expiry Date cannot be before Effective From.")
        if self.docstatus == 1:
            require_submitted("Land Parcel", self.land_parcel)

    def on_submit(self):
        set_submitted_status(self)
        self.db_set("document_status", "Submitted")

    def on_cancel(self):
        block_if_submitted("JV Allocation", {"jv_agreement": self.name}, "Submitted JV Allocation exists")
        set_cancelled_status(self)
        self.db_set("document_status", "Cancelled")
