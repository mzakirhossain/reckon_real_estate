frappe.ui.form.on("Real Estate Floor", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) frm.add_custom_button(__("Real Estate Unit"), () => {
            frappe.route_options = {project: frm.doc.project, building: frm.doc.building, floor: frm.doc.name};
            frappe.new_doc("Real Estate Unit");
        }, __("Create"));
    },
});
