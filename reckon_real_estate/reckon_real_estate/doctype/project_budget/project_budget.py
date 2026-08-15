import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate


class ProjectBudget(Document):
    def validate(self):
        project = frappe.get_doc("Real Estate Project", self.project)
        if project.company != self.company:
            frappe.throw("Budget company must match the project company.")
        if getdate(self.to_date) < getdate(self.from_date):
            frappe.throw("To Date cannot be before From Date.")
        self.total_budget = sum(flt(row.budget_amount) for row in self.items)

