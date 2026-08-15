frappe.ui.form.on("Real Estate Unit", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) frm.add_custom_button(__("Property Booking"), () => {
            frappe.route_options = {project: frm.doc.project, unit: frm.doc.name};
            frappe.new_doc("Property Booking");
        }, __("Create"));
    },
});
