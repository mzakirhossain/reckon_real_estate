import frappe
from frappe.model.document import Document

from reckon_real_estate.construction_workflow import require_submitted, set_cancelled_status, set_draft_status, set_submitted_status

class CollectionEntry(Document):
    def validate(self):
        set_draft_status(self, "collection_no", "document_status")
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
        plan_names = set()
        for row in self.allocations:
            if row.allocated_amount <= 0:
                frappe.throw("Allocated amount must be greater than zero.")
            plan = frappe.get_doc("Installment Plan", row.installment_plan)
            plan_names.add(plan.name)
            if plan.customer != self.customer or plan.project != self.project or plan.unit != self.unit:
                frappe.throw(f"Installment Plan {row.installment_plan} does not belong to this customer/project/unit.")
            if not plan.sales_invoice:
                frappe.throw(f"Create and submit the Sales Invoice for Installment Plan {plan.name} first.")
            if frappe.db.get_value("Sales Invoice", plan.sales_invoice, "docstatus") != 1:
                frappe.throw(f"Sales Invoice {plan.sales_invoice} must be submitted first.")
            row.sales_invoice = plan.sales_invoice
            if row.allocation_type == "Down Payment":
                already_collected = frappe.db.sql("""select coalesce(sum(pa.allocated_amount), 0)
                    from `tabPayment Allocation` pa
                    join `tabCollection Entry` ce on ce.name=pa.parent
                    where pa.installment_plan=%s and pa.allocation_type='Down Payment'
                    and ce.docstatus=1 and ce.name!=%s""", (plan.name, self.name))[0][0]
                available = max(frappe.utils.flt(plan.down_payment) - frappe.utils.flt(already_collected), 0)
                if row.allocated_amount > available + 0.01:
                    frappe.throw(f"Allocation exceeds remaining down payment ({available:,.2f}).")
                total += frappe.utils.flt(row.allocated_amount)
                continue
            if not row.installment_no:
                frappe.throw("Installment No is required for an installment allocation.")
            target = next((x for x in plan.installments if int(x.installment_no) == int(row.installment_no)), None)
            if not target:
                frappe.throw(f"Installment {row.installment_no} does not exist in Plan {row.installment_plan}.")
            available = frappe.utils.flt(target.outstanding)
            if row.allocated_amount > available + 0.01:
                frappe.throw(f"Allocation exceeds outstanding amount for installment {row.installment_no}.")
            total += frappe.utils.flt(row.allocated_amount)

        if self.docstatus == 1:
            require_submitted("Property Booking", self.booking)

        self.allocated_amount = total
        self.installment_plan = next(iter(plan_names)) if len(plan_names) == 1 else None
        if total > frappe.utils.flt(self.amount) + 0.01:
            frappe.throw("Total allocation cannot exceed Collection Amount.")
        self.unallocated_amount = max(frappe.utils.flt(self.amount) - total, 0)
        if self.unallocated_amount > 0.01:
            frappe.throw("Allocate the full Collection Amount before saving.")

    def on_submit(self):
        self._make_payment_entry()
        self._apply_allocations()
        self.db_set("status", "Submitted")
        set_submitted_status(self, "document_status")

    def on_cancel(self):
        if self.payment_entry:
            payment_status = frappe.db.get_value("Payment Entry", self.payment_entry, "docstatus")
            if payment_status == 1:
                frappe.throw(f"Cancel Payment Entry {self.payment_entry} before cancelling this Collection Entry.")
            if payment_status == 0:
                frappe.throw(f"Delete draft Payment Entry {self.payment_entry} before cancelling this Collection Entry.")
        self._apply_allocations(reverse=True)
        self.db_set("status", "Cancelled")
        set_cancelled_status(self, "document_status")

    def _make_payment_entry(self):
        if self.payment_entry:
            frappe.throw(f"Payment Entry {self.payment_entry} is already linked.")
        invoice_allocations = {}
        for row in self.allocations:
            invoice_allocations[row.sales_invoice] = (
                invoice_allocations.get(row.sales_invoice, 0) + frappe.utils.flt(row.allocated_amount)
            )

        bootstrap_invoice = next(iter(invoice_allocations), None)
        if not bootstrap_invoice and self.booking:
            bootstrap_invoice = frappe.db.get_value(
                "Installment Plan", {"booking": self.booking, "docstatus": 1}, "sales_invoice"
            )
        if not bootstrap_invoice:
            frappe.throw("A submitted Sales Invoice is required to create the ERPNext Payment Entry.")

        get_payment_entry = frappe.get_attr(
            "erpnext.accounts.doctype.payment_entry.payment_entry.get_payment_entry"
        )
        payment = get_payment_entry("Sales Invoice", bootstrap_invoice)
        payment.posting_date = self.collection_date
        payment.reference_no = self.reference_no or self.name
        payment.reference_date = self.collection_date
        if frappe.db.exists("Mode of Payment", self.payment_mode):
            payment.mode_of_payment = self.payment_mode
        payment.paid_amount = frappe.utils.flt(self.amount)
        payment.received_amount = frappe.utils.flt(self.amount) * frappe.utils.flt(
            payment.source_exchange_rate or 1
        )
        payment.set("references", [])
        for invoice, amount in invoice_allocations.items():
            outstanding = frappe.utils.flt(
                frappe.db.get_value("Sales Invoice", invoice, "outstanding_amount")
            )
            if amount > outstanding + 0.01:
                frappe.throw(f"Allocation exceeds ERPNext outstanding amount for Sales Invoice {invoice}.")
            payment.append("references", {
                "reference_doctype": "Sales Invoice",
                "reference_name": invoice,
                "total_amount": frappe.db.get_value("Sales Invoice", invoice, "grand_total"),
                "outstanding_amount": outstanding,
                "allocated_amount": amount,
            })

        project = frappe.get_doc("Real Estate Project", self.project)
        for fieldname, value in {
            "project": project.erpnext_project,
            "cost_center": project.cost_center,
            "collection_entry": self.name,
            "real_estate_booking": self.booking,
            "real_estate_unit": self.unit,
            "real_estate_project": self.project,
            "installment_plan": self.installment_plan,
        }.items():
            if payment.meta.has_field(fieldname):
                payment.set(fieldname, value)
        payment.remarks = f"Real estate collection {self.name}"
        payment.insert()
        payment.submit()
        self.db_set("payment_entry", payment.name)
        self.db_set("accounting_status", "Posted")

    def _apply_allocations(self, reverse=False):
        multiplier = -1 if reverse else 1
        for row in self.allocations:
            if row.allocation_type == "Down Payment":
                continue
            plan = frappe.get_doc("Installment Plan", row.installment_plan)
            target = next(x for x in plan.installments if int(x.installment_no) == int(row.installment_no))
            target.paid_amount = max(frappe.utils.flt(target.paid_amount) + multiplier * frappe.utils.flt(row.allocated_amount), 0)
            target.outstanding = max(frappe.utils.flt(target.total_amount) - frappe.utils.flt(target.paid_amount), 0)
            target.status = plan._status(target)
            plan.flags.ignore_validate_update_after_submit = True
            plan.save(ignore_permissions=True)
