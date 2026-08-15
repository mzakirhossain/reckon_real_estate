import frappe
from frappe.model.document import Document

class CollectionEntry(Document):
    def validate(self):
        if self.amount <= 0:
            frappe.throw("Collection Amount must be greater than zero.")
        if not self.booking:
            self.booking = frappe.db.exists("Property Booking", {
                "customer": self.customer,
                "project": self.project,
                "unit": self.unit,
                "status": ["in", ["Reserved", "Confirmed", "Agreement Signed", "Active"]]
            })
        if self.booking:
            b = frappe.get_doc("Property Booking", self.booking)
            if b.customer != self.customer or b.project != self.project or b.unit != self.unit:
                frappe.throw("Booking, Customer, Project and Unit must match.")

        total = 0
        for row in self.allocations:
            if row.allocated_amount <= 0:
                frappe.throw("Allocated amount must be greater than zero.")
            plan = frappe.get_doc("Installment Plan", row.installment_plan)
            if plan.customer != self.customer or plan.project != self.project or plan.unit != self.unit:
                frappe.throw(f"Installment Plan {row.installment_plan} does not belong to this customer/project/unit.")
            target = next((x for x in plan.installments if int(x.installment_no) == int(row.installment_no)), None)
            if not target:
                frappe.throw(f"Installment {row.installment_no} does not exist in Plan {row.installment_plan}.")
            available = frappe.utils.flt(target.outstanding)
            if row.allocated_amount > available + 0.01:
                frappe.throw(f"Allocation exceeds outstanding amount for installment {row.installment_no}.")
            total += frappe.utils.flt(row.allocated_amount)

        self.allocated_amount = total
        self.unallocated_amount = max(frappe.utils.flt(self.amount) - total, 0)

    def on_submit(self):
        self._apply_allocations()

    def on_cancel(self):
        self._apply_allocations(reverse=True)

    def _apply_allocations(self, reverse=False):
        multiplier = -1 if reverse else 1
        for row in self.allocations:
            plan = frappe.get_doc("Installment Plan", row.installment_plan)
            target = next(x for x in plan.installments if int(x.installment_no) == int(row.installment_no))
            target.paid_amount = max(frappe.utils.flt(target.paid_amount) + multiplier * frappe.utils.flt(row.allocated_amount), 0)
            target.outstanding = max(frappe.utils.flt(target.total_amount) - frappe.utils.flt(target.paid_amount), 0)
            target.status = plan._status(target)
            plan.flags.ignore_validate_update_after_submit = True
            plan.save(ignore_permissions=True)
