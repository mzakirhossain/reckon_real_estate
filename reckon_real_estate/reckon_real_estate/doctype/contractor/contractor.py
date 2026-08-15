import frappe
from frappe.model.document import Document

from reckon_real_estate.construction_workflow import (
    block_if_submitted,
    set_cancelled_status,
    set_draft_status,
    set_submitted_status,
)


class Contractor(Document):
    def validate(self):
        set_draft_status(self, "contractor_no")
        if frappe.db.get_value("Supplier", self.supplier, "disabled"):
            frappe.throw("The linked Supplier is disabled.")

    def on_submit(self):
        set_submitted_status(self)

    def on_cancel(self):
        block_if_submitted(
            "Contractor Work Order", {"contractor": self.name},
            "Submitted Contractor Work Order exists",
        )
        set_cancelled_status(self)
