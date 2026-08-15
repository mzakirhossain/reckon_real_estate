frappe.ui.form.on("Measurement Sheet", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Running Bill"), () => frappe.call({
                method: "reckon_real_estate.reckon_real_estate.doctype.measurement_sheet.measurement_sheet.make_running_bill",
                args: {source_name: frm.doc.name},
                callback: (r) => {
                    const docs = frappe.model.sync(r.message);
                    frappe.set_route("Form", docs[0].doctype, docs[0].name);
                },
            }), __("Create"));
        }
    },
});
