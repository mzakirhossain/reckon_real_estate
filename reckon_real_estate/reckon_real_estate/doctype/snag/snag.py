import frappe
from frappe.model.document import Document
from frappe.utils import today


class Snag(Document):
    def validate(self):
        self.snag_no = self.name
        handover = frappe.get_doc("Handover", self.handover)
        self.project, self.unit = handover.project, handover.unit
        if self.status in ("Resolved", "Closed"):
            if not self.resolution:
                frappe.throw("Resolution is required before resolving a snag.")
            self.resolved_date = self.resolved_date or today()
        elif self.status == "Reopened":
            self.resolved_date = None
