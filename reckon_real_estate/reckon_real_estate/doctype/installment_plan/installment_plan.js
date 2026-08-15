frappe.ui.form.on("Installment Plan", {
    refresh(frm) {
        if (frm.doc.docstatus !== 1) return;
        if (!frm.doc.sales_invoice) frm.add_custom_button(__("Sales Invoice"), () => frappe.call({
            method: "reckon_real_estate.reckon_real_estate.doctype.installment_plan.installment_plan.make_sales_invoice",
            args: {source_name: frm.doc.name},
            callback: (r) => frappe.model.sync(r.message) && frappe.set_route("Form", "Sales Invoice", r.message.name),
        }), __("Create"));
        frm.add_custom_button(__("Collection Entry"), () => {
            frappe.route_options = {
                booking: frm.doc.booking,
                customer: frm.doc.customer,
                project: frm.doc.project,
                unit: frm.doc.unit,
            };
            frappe.new_doc("Collection Entry");
        }, __("Create"));
    },
});
