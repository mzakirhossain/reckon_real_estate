frappe.ui.form.on("Handover", {
    refresh(frm) {
        if (frm.doc.docstatus !== 1) return;
        for (const [label, doctype] of [["Warranty", "Warranty"], ["Maintenance", "Maintenance"], ["Service Request", "Service Request"]]) {
            frm.add_custom_button(__(label), () => {
                frappe.route_options = {
                    handover: frm.doc.name,
                    customer: frm.doc.customer,
                    project: frm.doc.project,
                    unit: frm.doc.unit,
                };
                frappe.new_doc(doctype);
            }, __("Create"));
        }
    },
});
