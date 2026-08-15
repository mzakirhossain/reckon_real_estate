import frappe
from frappe.model.document import Document
from frappe.utils import flt

from reckon_real_estate.construction_workflow import (
    block_if_submitted,
    set_cancelled_status,
    set_draft_status,
    set_submitted_status,
)


class ContractorWorkOrder(Document):
    def validate(self):
        set_draft_status(self, "work_order_no")
        contractor = frappe.get_doc("Contractor", self.contractor)
        if contractor.docstatus != 1:
            frappe.throw("Contractor must be submitted before creating a Work Order.")
        budget = frappe.get_doc("Project Budget", self.project_budget)
        if budget.docstatus != 1:
            frappe.throw("Project Budget must be submitted before creating a Work Order.")
        if budget.project != self.project:
            frappe.throw("Work Order project must match the Project Budget.")
        self.boq = budget.boq
        project = frappe.get_doc("Real Estate Project", self.project)
        if project.company != self.company:
            frappe.throw("Work Order company must match the project company.")
        self.total_amount = sum(flt(r.quantity) * flt(r.rate) for r in self.items)
        for row in self.items:
            row.amount = flt(row.quantity) * flt(row.rate)
        if self.end_date and self.start_date and self.end_date < self.start_date:
            frappe.throw("End Date cannot be before Start Date.")

    def on_submit(self):
        set_submitted_status(self)

    def on_cancel(self):
        block_if_submitted(
            "Measurement Sheet", {"work_order": self.name},
            "Submitted Measurement Sheet exists",
        )
        if self.purchase_order:
            if frappe.db.get_value("Purchase Order", self.purchase_order, "docstatus") == 1:
                frappe.throw("Cancel the linked Purchase Order before cancelling this Work Order.")
        set_cancelled_status(self)


@frappe.whitelist()
def make_purchase_order(source_name):
    source = frappe.get_doc("Contractor Work Order", source_name)
    if source.docstatus != 1:
        frappe.throw("Submit the Contractor Work Order first.")
    if source.purchase_order:
        return frappe.get_doc("Purchase Order", source.purchase_order)
    supplier = frappe.db.get_value("Contractor", source.contractor, "supplier")
    project = frappe.db.get_value("Real Estate Project", source.project, "erpnext_project")
    cost_center = frappe.db.get_value("Real Estate Project", source.project, "cost_center")
    po = frappe.new_doc("Purchase Order")
    po.supplier, po.company, po.schedule_date = supplier, source.company, source.end_date
    po.remarks = f"Contractor Work Order {source.name}"
    for row in source.items:
        po.append("items", {"item_code": row.item_code, "qty": row.quantity, "rate": row.rate,
            "schedule_date": source.end_date, "project": project, "cost_center": cost_center})
    po.insert()
    source.db_set("purchase_order", po.name)
    return po


@frappe.whitelist()
def make_measurement_sheet(source_name):
    source = frappe.get_doc("Contractor Work Order", source_name)
    if source.docstatus != 1:
        frappe.throw("Submit the Contractor Work Order first.")
    target = frappe.new_doc("Measurement Sheet")
    target.work_order = source.name
    for row in source.items:
        target.append("items", {"work_order_item": row.name, "item_code": row.item_code,
            "description": row.description, "uom": row.uom, "rate": row.rate})
    return target
