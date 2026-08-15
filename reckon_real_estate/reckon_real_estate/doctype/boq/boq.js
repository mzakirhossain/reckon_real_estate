frappe.ui.form.on("BOQ", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Project Budget"), () => frappe.call({
                method: "reckon_real_estate.reckon_real_estate.doctype.boq.boq.make_project_budget",
                args: {source_name: frm.doc.name},
                callback: (r) => {
                    const docs = frappe.model.sync(r.message);
                    frappe.set_route("Form", docs[0].doctype, docs[0].name);
                },
            }), __("Create"));
        }
    },
});
