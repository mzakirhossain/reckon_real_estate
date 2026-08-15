frappe.ui.form.on("Contractor", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Contractor Work Order"), () => {
                frappe.route_options = {contractor: frm.doc.name};
                frappe.new_doc("Contractor Work Order");
            }, __("Create"));
        }
    },
});
