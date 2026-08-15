frappe.ui.form.on("Contractor Work Order", {
    refresh(frm) {
        if (frm.doc.docstatus !== 1) return;
        if (!frm.doc.purchase_order) {
            frm.add_custom_button(__("Purchase Order"), () => frappe.call({
                method: "reckon_real_estate.reckon_real_estate.doctype.contractor_work_order.contractor_work_order.make_purchase_order",
                args: {source_name: frm.doc.name},
                callback: (r) => frappe.model.sync(r.message) && frappe.set_route("Form", "Purchase Order", r.message.name),
            }), __("Create"));
        }
        frm.add_custom_button(__("Measurement Sheet"), () => frappe.call({
            method: "reckon_real_estate.reckon_real_estate.doctype.contractor_work_order.contractor_work_order.make_measurement_sheet",
            args: {source_name: frm.doc.name},
            callback: (r) => {
                const docs = frappe.model.sync(r.message);
                frappe.set_route("Form", docs[0].doctype, docs[0].name);
            },
        }), __("Create"));
    },
});
