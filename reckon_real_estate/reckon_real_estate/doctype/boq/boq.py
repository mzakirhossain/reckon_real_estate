import frappe
from frappe.model.document import Document
from frappe.utils import flt

from reckon_real_estate.construction_workflow import (
    block_if_submitted,
    set_cancelled_status,
    set_draft_status,
    set_submitted_status,
)


class BOQ(Document):
    def validate(self):
        set_draft_status(self, "boq_no")
        project = frappe.get_doc("Real Estate Project", self.project)
        if project.company != self.company:
            frappe.throw("BOQ company must match the Real Estate Project company.")
        self.total_amount = sum(flt(row.quantity) * flt(row.rate) for row in self.items)
        for row in self.items:
            row.amount = flt(row.quantity) * flt(row.rate)

    def on_submit(self):
        set_submitted_status(self)

    def on_cancel(self):
        block_if_submitted("Project Budget", {"boq": self.name}, "Submitted Project Budget exists")
        set_cancelled_status(self)


@frappe.whitelist()
def make_project_budget(source_name):
    source = frappe.get_doc("BOQ", source_name)
    if source.docstatus != 1:
        frappe.throw("Submit the BOQ first.")
    target = frappe.new_doc("Project Budget")
    target.boq, target.project, target.company = source.name, source.project, source.company
    return target
