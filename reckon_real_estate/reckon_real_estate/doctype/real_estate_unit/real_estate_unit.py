import frappe
from frappe.model.document import Document

from reckon_real_estate.construction_workflow import block_if_submitted, require_submitted, set_cancelled_status, set_draft_status, set_submitted_status

class RealEstateUnit(Document):
    def validate(self):
        set_draft_status(self, "unit_code", "document_status")
        self.list_price = frappe.utils.flt(self.area_sqft) * frappe.utils.flt(self.base_rate_per_sqft)
        if self.floor:
            floor_project, floor_building = frappe.db.get_value(
                "Real Estate Floor", self.floor, ["project", "building"]
            ) or (None, None)
            if floor_project != self.project or floor_building != self.building:
                frappe.throw("Floor, Building and Project must match.")
        if self.docstatus == 1:
            require_submitted("Real Estate Floor", self.floor)

    def on_submit(self):
        set_submitted_status(self, "document_status")

    def on_cancel(self):
        block_if_submitted("Property Booking", {"unit": self.name}, "Submitted Property Booking exists")
        set_cancelled_status(self, "document_status")
