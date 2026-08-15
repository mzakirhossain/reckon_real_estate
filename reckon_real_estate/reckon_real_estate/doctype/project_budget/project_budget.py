import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate

from reckon_real_estate.construction_workflow import (
    block_if_submitted,
    set_cancelled_status,
    set_draft_status,
    set_submitted_status,
)


class ProjectBudget(Document):
    def validate(self):
        set_draft_status(self, "budget_no")
        boq = frappe.get_doc("BOQ", self.boq)
        if boq.docstatus != 1:
            frappe.throw("BOQ must be submitted before creating a Project Budget.")
        if boq.project != self.project or boq.company != self.company:
            frappe.throw("Project Budget project and company must match the BOQ.")
        project = frappe.get_doc("Real Estate Project", self.project)
        if project.company != self.company:
            frappe.throw("Budget company must match the project company.")
        if getdate(self.to_date) < getdate(self.from_date):
            frappe.throw("To Date cannot be before From Date.")
        self.total_budget = sum(flt(row.budget_amount) for row in self.items)

    def on_submit(self):
        set_submitted_status(self)

    def on_cancel(self):
        block_if_submitted(
            "Contractor Work Order", {"project_budget": self.name},
            "Submitted Contractor Work Order exists",
        )
        set_cancelled_status(self)
