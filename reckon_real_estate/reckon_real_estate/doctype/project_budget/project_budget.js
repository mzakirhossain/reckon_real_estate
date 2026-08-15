frappe.ui.form.on("Project Budget", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Contractor"), () => {
                frappe.route_options = {};
                frappe.new_doc("Contractor");
            }, __("Create"));
            frm.add_custom_button(__("Contractor Work Order"), () => {
                frappe.route_options = {
                    project_budget: frm.doc.name,
                    project: frm.doc.project,
                    company: frm.doc.company,
                    boq: frm.doc.boq,
                };
                frappe.new_doc("Contractor Work Order");
            }, __("Create"));
        }
    },
});
