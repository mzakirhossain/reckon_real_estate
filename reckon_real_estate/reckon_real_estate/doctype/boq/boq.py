import frappe
from frappe.model.document import Document
from frappe.utils import flt


class BOQ(Document):
    def validate(self):
        project = frappe.get_doc("Real Estate Project", self.project)
        if project.company != self.company:
            frappe.throw("BOQ company must match the Real Estate Project company.")
        self.total_amount = sum(flt(row.quantity) * flt(row.rate) for row in self.items)
        for row in self.items:
            row.amount = flt(row.quantity) * flt(row.rate)

    def on_submit(self):
        self.db_set("status", "Approved")
