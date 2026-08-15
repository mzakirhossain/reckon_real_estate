import frappe
from frappe.model.document import Document
from frappe.utils import flt


class BOQRevision(Document):
    def validate(self):
        boq = frappe.get_doc("BOQ", self.boq)
        if boq.docstatus != 1:
            frappe.throw("Only a submitted BOQ can be revised.")
        self.project = boq.project
        self.previous_total = boq.total_amount
        self.revised_total = sum(flt(r.quantity) * flt(r.rate) for r in self.items)
        self.variance = flt(self.revised_total) - flt(self.previous_total)
        for row in self.items:
            row.amount = flt(row.quantity) * flt(row.rate)

    def on_submit(self):
        frappe.db.set_value("BOQ", self.boq, {"status": "Superseded", "revision_no": self.revision_no})

