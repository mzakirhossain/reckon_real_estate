frappe.ui.form.on("Real Estate Project", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) frm.add_custom_button(__("Real Estate Building"), () => {
            frappe.route_options = {project: frm.doc.name};
            frappe.new_doc("Real Estate Building");
        }, __("Create"));
    },
});
