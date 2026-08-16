import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate

from reckon_real_estate.construction_workflow import require_submitted, set_cancelled_status, set_draft_status, set_submitted_status


class Maintenance(Document):
    def validate(self):
        set_draft_status(self, "maintenance_no", "document_status")
        handover = frappe.get_doc("Handover", self.handover)
        self.customer, self.project, self.unit = handover.customer, handover.project, handover.unit
        area = flt(frappe.db.get_value("Real Estate Unit", self.unit, "area_sqft"))
        self.monthly_amount = area * flt(self.maintenance_rate)
        if self.end_date and getdate(self.end_date) < getdate(self.start_date):
            frappe.throw("End Date cannot be before Start Date.")
        if self.docstatus == 1:
            require_submitted("Handover", self.handover)

    def on_submit(self):
        set_submitted_status(self)
        self.db_set("document_status", "Submitted")

    def on_cancel(self):
        set_cancelled_status(self)
        self.db_set("document_status", "Cancelled")
