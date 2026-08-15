from frappe.model.document import Document

class InstallmentSchedule(Document):
    def validate(self):
        self.total_amount = self.principal + self.other_charges
        self.outstanding = max(self.total_amount - self.paid_amount, 0)
