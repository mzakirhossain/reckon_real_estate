import frappe
from frappe.model.document import Document
from frappe.utils import flt

from reckon_real_estate.construction_workflow import (
    block_if_submitted,
    set_cancelled_status,
    set_draft_status,
    set_submitted_status,
)


class MeasurementSheet(Document):
    def validate(self):
        set_draft_status(self, "measurement_no")
        work_order = frappe.get_doc("Contractor Work Order", self.work_order)
        if work_order.docstatus != 1:
            frappe.throw("Contractor Work Order must be submitted.")
        if self.period_to < self.period_from:
            frappe.throw("Period To cannot be before Period From.")
        self.project, self.contractor = work_order.project, work_order.contractor
        order_rows = {row.name: row for row in work_order.items}
        self.total_amount = 0
        for row in self.items:
            ordered = order_rows.get(row.work_order_item)
            if not ordered:
                frappe.throw(f"Row {row.idx}: item is not from the selected Work Order.")
            previous = frappe.db.sql("""select coalesce(sum(mi.quantity), 0) from `tabMeasurement Item` mi
                join `tabMeasurement Sheet` ms on ms.name=mi.parent
                where ms.work_order=%s and mi.work_order_item=%s and ms.docstatus=1 and ms.name!=%s""",
                (self.work_order, row.work_order_item, self.name or ""))[0][0]
            row.item_code, row.uom, row.rate = ordered.item_code, ordered.uom, ordered.rate
            row.previous_quantity = flt(previous)
            row.cumulative_quantity = flt(previous) + flt(row.quantity)
            if row.cumulative_quantity > flt(ordered.quantity):
                frappe.throw(f"Row {row.idx}: cumulative measurement exceeds ordered quantity.")
            row.amount = flt(row.quantity) * flt(row.rate)
            self.total_amount += row.amount

    def on_submit(self):
        set_submitted_status(self)

    def on_cancel(self):
        block_if_submitted(
            "Running Bill", {"measurement_sheet": self.name},
            "Submitted Running Bill exists",
        )
        set_cancelled_status(self)


@frappe.whitelist()
def make_running_bill(source_name):
    source = frappe.get_doc("Measurement Sheet", source_name)
    if source.docstatus != 1:
        frappe.throw("Submit the Measurement Sheet first.")
    work_order = frappe.get_doc("Contractor Work Order", source.work_order)
    target = frappe.new_doc("Running Bill")
    target.measurement_sheet, target.company = source.name, work_order.company
    target.retention_percent = work_order.retention_percent
    for row in source.items:
        target.append("items", {"item_code": row.item_code, "description": row.description,
            "uom": row.uom, "quantity": row.quantity, "rate": row.rate})
    return target
