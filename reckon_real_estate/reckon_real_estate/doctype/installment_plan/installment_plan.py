import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today, add_months

from reckon_real_estate.construction_workflow import block_if_submitted, require_submitted, set_cancelled_status, set_draft_status, set_submitted_status

class InstallmentPlan(Document):
    def validate(self):
        set_draft_status(self, "plan_no", "document_status")
        agreement = frappe.get_doc("Sales Agreement", self.sales_agreement)
        if agreement.booking != self.booking:
            frappe.throw("Installment Plan booking must match the Sales Agreement.")
        duplicate = frappe.db.exists("Installment Plan", {
            "sales_agreement": self.sales_agreement, "name": ["!=", self.name], "docstatus": ["!=", 2]
        })
        if duplicate:
            frappe.throw(f"Active Installment Plan already exists for this Sales Agreement: {duplicate}")
        booking = frappe.get_doc("Property Booking", self.booking)
        if booking.customer != self.customer or booking.project != self.project or booking.unit != self.unit:
            frappe.throw("Booking, Customer, Project and Unit must match.")
        for row in self.installments:
            row.total_amount = frappe.utils.flt(row.principal) + frappe.utils.flt(row.other_charges)
            row.outstanding = max(row.total_amount - frappe.utils.flt(row.paid_amount), 0)
            row.status = self._status(row)
        self.total_scheduled = sum(frappe.utils.flt(r.total_amount) for r in self.installments)
        expected = frappe.utils.flt(booking.net_contract_value) - frappe.utils.flt(self.down_payment)
        if abs(self.total_scheduled - expected) > 0.01:
            frappe.throw(f"Installment schedule total must equal Net Contract Value minus Down Payment ({expected:,.2f}).")
        if self.docstatus == 1:
            require_submitted("Sales Agreement", self.sales_agreement)
            require_submitted("Property Booking", self.booking)

    def on_submit(self):
        self.db_set("status", "Active")
        set_submitted_status(self, "document_status")

    def on_cancel(self):
        if self.sales_invoice and frappe.db.get_value("Sales Invoice", self.sales_invoice, "docstatus") != 2:
            frappe.throw(f"Cancel and delete Sales Invoice {self.sales_invoice} before cancelling this Installment Plan.")
        collection = frappe.db.sql("""select ce.name from `tabCollection Entry` ce
            join `tabPayment Allocation` pa on pa.parent=ce.name
            where ce.docstatus=1 and pa.installment_plan=%s limit 1""", self.name)
        if collection:
            frappe.throw(f"Submitted Collection Entry exists: {collection[0][0]}. Cancel it first.")
        self.db_set("status", "Cancelled")
        set_cancelled_status(self, "document_status")


@frappe.whitelist()
def make_sales_invoice(source_name):
    source = frappe.get_doc("Installment Plan", source_name)
    if source.docstatus != 1:
        frappe.throw("Submit the Installment Plan first.")
    if source.sales_invoice:
        return frappe.get_doc("Sales Invoice", source.sales_invoice)

    agreement = frappe.get_doc("Sales Agreement", source.sales_agreement)
    project = frappe.get_doc("Real Estate Project", source.project)
    unit = frappe.get_doc("Real Estate Unit", source.unit)
    if not project.erpnext_project or not project.cost_center:
        frappe.throw("Map both ERPNext Project and Cost Center on the Real Estate Project first.")
    if not unit.erpnext_item:
        frappe.throw("Map an ERPNext Item on the Real Estate Unit first.")

    invoice = frappe.new_doc("Sales Invoice")
    invoice.customer = source.customer
    invoice.company = project.company
    invoice.posting_date = source.plan_start_date
    invoice.due_date = max((row.due_date for row in source.installments), default=source.plan_start_date)
    if invoice.meta.has_field("project"):
        invoice.project = project.erpnext_project

    item = {"item_code": unit.erpnext_item, "qty": 1, "rate": agreement.net_contract_value,
        "project": project.erpnext_project, "cost_center": project.cost_center}
    if project.default_income_account:
        item["income_account"] = project.default_income_account
    if frappe.db.get_value("Item", unit.erpnext_item, "is_stock_item") and project.project_warehouse:
        invoice.update_stock = 1
        item["warehouse"] = project.project_warehouse
    invoice.append("items", item)

    schedule = []
    if frappe.utils.flt(source.down_payment):
        schedule.append((source.plan_start_date, frappe.utils.flt(source.down_payment), "Booking / Down Payment"))
    schedule.extend((row.due_date, frappe.utils.flt(row.total_amount), row.description) for row in source.installments)
    total = frappe.utils.flt(agreement.net_contract_value)
    allocated_portion = 0
    for index, (due_date, amount, description) in enumerate(schedule):
        portion = 100 - allocated_portion if index == len(schedule) - 1 else amount / total * 100 if total else 0
        allocated_portion += portion
        invoice.append("payment_schedule", {"due_date": due_date, "payment_amount": amount,
            "invoice_portion": portion, "description": description})

    for fieldname, value in {
        "sales_agreement": source.sales_agreement,
        "real_estate_booking": source.booking,
        "real_estate_unit": source.unit,
        "real_estate_project": source.project,
        "installment_plan": source.name,
    }.items():
        if invoice.meta.has_field(fieldname):
            invoice.set(fieldname, value)
    invoice.remarks = f"Real estate sale under Sales Agreement {agreement.name}"
    invoice.insert()
    source.db_set("sales_invoice", invoice.name)
    for row in source.installments:
        frappe.db.set_value("Installment Schedule", row.name, "sales_invoice", invoice.name, update_modified=False)
    return invoice

    def _status(self, row):
        if row.outstanding <= 0.01:
            return "Paid"
        if row.paid_amount > 0:
            return "Partial"
        if row.due_date and getdate(row.due_date) < getdate(today()):
            return "Overdue"
        if row.due_date and getdate(row.due_date) == getdate(today()):
            return "Due"
        return "Upcoming"

def update_all_installment_statuses():
    plans = frappe.get_all("Installment Plan", filters={"docstatus": ["!=", 2]}, pluck="name")
    for name in plans:
        doc = frappe.get_doc("Installment Plan", name)
        changed = False
        for row in doc.installments:
            old = row.status
            row.status = doc._status(row)
            if old != row.status:
                changed = True
        if changed:
            doc.flags.ignore_validate_update_after_submit = True
            doc.save(ignore_permissions=True)
