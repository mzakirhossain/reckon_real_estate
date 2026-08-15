import frappe
from frappe.model.document import Document
from frappe.utils import flt

from reckon_real_estate.construction_workflow import set_cancelled_status, set_draft_status, set_submitted_status


class RunningBill(Document):
    def validate(self):
        set_draft_status(self, "running_bill_no")
        sheet = frappe.get_doc("Measurement Sheet", self.measurement_sheet)
        if sheet.docstatus != 1:
            frappe.throw("Measurement Sheet must be submitted.")
        self.work_order, self.project, self.contractor = sheet.work_order, sheet.project, sheet.contractor
        work_order = frappe.get_doc("Contractor Work Order", sheet.work_order)
        self.company, self.purchase_order = work_order.company, work_order.purchase_order
        measured = {row.item_code: flt(row.quantity) for row in sheet.items}
        self.gross_amount = 0
        for row in self.items:
            if flt(row.quantity) > measured.get(row.item_code, 0):
                frappe.throw(f"Row {row.idx}: billed quantity exceeds this measurement.")
            row.amount = flt(row.quantity) * flt(row.rate)
            self.gross_amount += row.amount
        self.retention_amount = self.gross_amount * flt(self.retention_percent) / 100
        self.net_payable = self.gross_amount - self.retention_amount - flt(self.other_deductions)
        if self.net_payable < 0:
            frappe.throw("Deductions cannot exceed the gross bill amount.")

    def on_submit(self):
        set_submitted_status(self)

    def on_cancel(self):
        if self.purchase_invoice:
            if frappe.db.get_value("Purchase Invoice", self.purchase_invoice, "docstatus") == 1:
                frappe.throw("Cancel the linked Purchase Invoice before cancelling this Running Bill.")
        set_cancelled_status(self)


@frappe.whitelist()
def make_purchase_invoice(source_name):
    source = frappe.get_doc("Running Bill", source_name)
    if source.docstatus != 1:
        frappe.throw("Submit the Running Bill first.")
    if source.purchase_invoice:
        return frappe.get_doc("Purchase Invoice", source.purchase_invoice)
    supplier = frappe.db.get_value("Contractor", source.contractor, "supplier")
    project = frappe.db.get_value("Real Estate Project", source.project, "erpnext_project")
    cost_center = frappe.db.get_value("Real Estate Project", source.project, "cost_center")
    invoice = frappe.new_doc("Purchase Invoice")
    invoice.supplier, invoice.company = supplier, source.company
    invoice.bill_no, invoice.bill_date = source.contractor_invoice_no, source.bill_date
    invoice.remarks = f"Running Bill {source.name}; retention {source.retention_amount}"
    for fieldname, value in {
        "running_bill": source.name,
        "contractor_work_order": source.work_order,
        "real_estate_project": source.project,
        "boq": frappe.db.get_value("Contractor Work Order", source.work_order, "boq"),
    }.items():
        if invoice.meta.has_field(fieldname):
            invoice.set(fieldname, value)
    po_items = {}
    if source.purchase_order:
        for po_row in frappe.get_all("Purchase Order Item", filters={"parent": source.purchase_order}, fields=["name", "item_code"]):
            po_items.setdefault(po_row.item_code, []).append(po_row.name)
    for row in source.items:
        values = {"item_code": row.item_code, "qty": row.quantity, "rate": row.rate,
            "project": project, "cost_center": cost_center}
        if source.purchase_order and po_items.get(row.item_code):
            values.update({"purchase_order": source.purchase_order, "po_detail": po_items[row.item_code].pop(0)})
        invoice.append("items", values)
    invoice.insert()
    source.db_set("purchase_invoice", invoice.name)
    source.db_set("accounting_status", "Draft Invoice")
    return invoice
