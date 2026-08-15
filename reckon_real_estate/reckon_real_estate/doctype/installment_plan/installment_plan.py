import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today, add_months

class InstallmentPlan(Document):
    def validate(self):
        booking = frappe.get_doc("Property Booking", self.booking)
        if booking.customer != self.customer or booking.project != self.project or booking.unit != self.unit:
            frappe.throw("Booking, Customer, Project and Unit must match.")
        self.total_scheduled = sum(frappe.utils.flt(r.total_amount) for r in self.installments)
        expected = frappe.utils.flt(booking.net_contract_value) - frappe.utils.flt(self.down_payment)
        if abs(self.total_scheduled - expected) > 0.01:
            frappe.throw(f"Installment schedule total must equal Net Contract Value minus Down Payment ({expected:,.2f}).")
        for row in self.installments:
            row.total_amount = frappe.utils.flt(row.principal) + frappe.utils.flt(row.other_charges)
            row.outstanding = max(row.total_amount - frappe.utils.flt(row.paid_amount), 0)
            row.status = self._status(row)

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
