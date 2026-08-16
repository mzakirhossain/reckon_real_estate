import frappe
from frappe.model.document import Document
from frappe.utils import flt

from reckon_real_estate.construction_workflow import block_if_submitted, require_submitted, set_cancelled_status, set_draft_status, set_submitted_status


class Handover(Document):
    def validate(self):
        set_draft_status(self, "handover_no", "document_status")
        agreement = frappe.get_doc("Sales Agreement", self.sales_agreement)
        self.booking, self.customer, self.project, self.unit = agreement.booking, agreement.customer, agreement.project, agreement.unit
        if self.docstatus == 1:
            require_submitted("Sales Agreement", self.sales_agreement)
            outstanding = frappe.db.sql("""select coalesce(sum(s.outstanding), 0) from `tabInstallment Schedule` s
                join `tabInstallment Plan` p on p.name=s.parent
                where p.sales_agreement=%s and p.docstatus=1""", self.sales_agreement)[0][0]
            if flt(outstanding) > 0.01:
                frappe.throw(f"Cannot hand over with outstanding installments of {flt(outstanding):,.2f}.")
            open_snag = frappe.db.exists("Snag", {"handover": self.name, "status": ["in", ["Open", "In Progress", "Reopened"]]})
            if open_snag:
                frappe.throw(f"Resolve open Snag {open_snag} before handover.")
            if not self.customer_accepted:
                frappe.throw("Customer Accepted must be checked before submission.")

    def on_submit(self):
        frappe.db.set_value("Real Estate Unit", self.unit, "status", "Handed Over")
        set_submitted_status(self)
        self.db_set("document_status", "Submitted")

    def on_cancel(self):
        block_if_submitted("Warranty", {"handover": self.name}, "Submitted Warranty exists")
        frappe.db.set_value("Real Estate Unit", self.unit, "status", "Handover Pending")
        set_cancelled_status(self)
        self.db_set("document_status", "Cancelled")
