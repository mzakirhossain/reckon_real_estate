import frappe
from frappe.model.document import Document

class RealEstateUnit(Document):
    def validate(self):
        self.list_price = frappe.utils.flt(self.area_sqft) * frappe.utils.flt(self.base_rate_per_sqft)
        if self.floor:
            floor_project, floor_building = frappe.db.get_value(
                "Real Estate Floor", self.floor, ["project", "building"]
            ) or (None, None)
            if floor_project != self.project or floor_building != self.building:
                frappe.throw("Floor, Building and Project must match.")
