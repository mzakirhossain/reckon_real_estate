from frappe.model.document import Document


class LandOwner(Document):
    def before_insert(self):
        self.owner_no = self.name

    def validate(self):
        self.owner_no = self.name
