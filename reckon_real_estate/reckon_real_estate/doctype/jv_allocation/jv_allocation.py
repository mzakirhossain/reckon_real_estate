import frappe
from frappe.model.document import Document
from frappe.utils import flt

from reckon_real_estate.construction_workflow import require_submitted, set_cancelled_status, set_draft_status, set_submitted_status


class JVAllocation(Document):
    def validate(self):
        set_draft_status(self, "allocation_no", "document_status")
        agreement = frappe.get_doc("JV Agreement", self.jv_agreement)
        self.project, self.land_parcel = agreement.project, agreement.land_parcel
        if self.allocation_type == "Flat":
            if not self.unit:
                frappe.throw("Flat / Unit is required for a flat allocation.")
            if frappe.db.get_value("Real Estate Unit", self.unit, "project") != self.project:
                frappe.throw("Allocated Unit must belong to the JV project.")
        if flt(self.land_area) < 0 or flt(self.share_percent) < 0:
            frappe.throw("Land Area and Share Percent cannot be negative.")
        if self.docstatus == 1:
            require_submitted("JV Agreement", self.jv_agreement)

    def on_submit(self):
        if self.unit:
            frappe.db.set_value("Real Estate Unit", self.unit, {
                "land_parcel": self.land_parcel,
                "proportionate_land_area": flt(self.land_area),
                "land_share_percent": flt(self.share_percent),
                "jv_allocation": self.name,
            })
        set_submitted_status(self)
        self.db_set("document_status", "Submitted")

    def on_cancel(self):
        if self.unit and frappe.db.get_value("Real Estate Unit", self.unit, "jv_allocation") == self.name:
            frappe.db.set_value("Real Estate Unit", self.unit, {
                "land_parcel": None, "proportionate_land_area": 0, "land_share_percent": 0, "jv_allocation": None,
            })
        set_cancelled_status(self)
        self.db_set("document_status", "Cancelled")
