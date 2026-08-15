frappe.ui.form.on("Real Estate Building", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) frm.add_custom_button(__("Real Estate Floor"), () => {
            frappe.route_options = {project: frm.doc.project, building: frm.doc.name};
            frappe.new_doc("Real Estate Floor");
        }, __("Create"));
    },
});
