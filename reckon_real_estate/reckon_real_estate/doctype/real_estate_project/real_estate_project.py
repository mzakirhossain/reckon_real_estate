import frappe
from frappe.model.document import Document

from reckon_real_estate.construction_workflow import block_if_submitted, set_cancelled_status, set_draft_status, set_submitted_status

class RealEstateProject(Document):
    def validate(self):
        set_draft_status(self, "project_code", "document_status")
        if self.start_date and self.expected_completion_date and self.expected_completion_date < self.start_date:
            frappe.throw("Expected Completion Date cannot be before Start Date.")
        self.total_units = frappe.db.count("Real Estate Unit", {"project": self.name, "docstatus": ["!=", 2]})
        if self.erpnext_project and frappe.db.get_value("Project", self.erpnext_project, "company") != self.company:
            frappe.throw("ERPNext Project must belong to the selected Company.")
        if self.cost_center and frappe.db.get_value("Cost Center", self.cost_center, "company") != self.company:
            frappe.throw("Cost Center must belong to the selected Company.")
        if self.project_warehouse and frappe.db.get_value("Warehouse", self.project_warehouse, "company") != self.company:
            frappe.throw("Project Warehouse must belong to the selected Company.")
        if self.default_income_account:
            account = frappe.db.get_value(
                "Account", self.default_income_account, ["company", "root_type", "is_group"], as_dict=True
            )
            if not account or account.company != self.company or account.root_type != "Income" or account.is_group:
                frappe.throw("Default Sales Income Account must be a ledger Income account for this Company.")

    def on_submit(self):
        self._ensure_erpnext_dimensions()
        set_submitted_status(self, "document_status")

    def on_cancel(self):
        block_if_submitted("Real Estate Building", {"project": self.name}, "Submitted Building exists")
        set_cancelled_status(self, "document_status")

    def _ensure_erpnext_dimensions(self):
        if not self.erpnext_project:
            erp_project = frappe.db.get_value(
                "Project", {"project_name": self.project_name, "company": self.company}, "name"
            )
            if not erp_project:
                erp_project = frappe.get_doc({
                    "doctype": "Project",
                    "project_name": self.project_name,
                    "company": self.company,
                    "status": "Open",
                    "expected_start_date": self.start_date,
                    "expected_end_date": self.expected_completion_date,
                }).insert(ignore_permissions=True).name
            self.db_set("erpnext_project", erp_project)

        if not self.cost_center:
            cost_center = frappe.db.get_value(
                "Cost Center", {"cost_center_name": self.project_name, "company": self.company}, "name"
            )
            if not cost_center:
                parent = frappe.db.get_value("Company", self.company, "cost_center")
                if not parent:
                    parent = frappe.db.get_value(
                        "Cost Center", {"company": self.company, "is_group": 1, "parent_cost_center": ["is", "not set"]}, "name"
                    )
                if not parent:
                    frappe.throw("Configure the Company's default/root Cost Center first.")
                cost_center = frappe.get_doc({
                    "doctype": "Cost Center",
                    "cost_center_name": self.project_name,
                    "company": self.company,
                    "parent_cost_center": parent,
                    "is_group": 0,
                }).insert(ignore_permissions=True).name
            self.db_set("cost_center", cost_center)
