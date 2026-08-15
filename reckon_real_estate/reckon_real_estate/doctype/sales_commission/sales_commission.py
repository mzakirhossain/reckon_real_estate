import frappe
from frappe.model.document import Document
from frappe.utils import flt


class SalesCommission(Document):
    def validate(self):
        booking = frappe.get_doc("Property Booking", self.booking)
        self.project, self.customer = booking.project, booking.customer
        self.commission_amount = flt(self.commission_base) * flt(self.commission_rate) / 100
        self.payable_amount = self.commission_amount - flt(self.paid_amount)
        if self.payable_amount < 0:
            frappe.throw("Paid Amount cannot exceed Commission Amount.")

