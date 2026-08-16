import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class ServiceRequest(Document):
    def validate(self):
        self.request_no = self.name
        if frappe.db.get_value("Real Estate Unit", self.unit, "project") != self.project:
            frappe.throw("Unit must belong to the selected Project.")
        if self.handover:
            handover = frappe.get_doc("Handover", self.handover)
            if handover.customer != self.customer or handover.unit != self.unit:
                frappe.throw("Handover, Customer and Unit must match.")
        if self.warranty:
            warranty = frappe.get_doc("Warranty", self.warranty)
            if warranty.docstatus != 1 or warranty.customer != self.customer or warranty.unit != self.unit:
                frappe.throw("A submitted Warranty for this Customer and Unit is required.")
            if not (getdate(warranty.start_date) <= getdate(self.request_date) <= getdate(warranty.end_date)):
                frappe.throw("Request Date is outside the selected Warranty period.")
        if self.status in ("Resolved", "Closed"):
            if not self.resolution:
                frappe.throw("Resolution is required before resolving a Service Request.")
            self.resolved_date = self.resolved_date or today()
        elif self.status not in ("Resolved", "Closed"):
            self.resolved_date = None
